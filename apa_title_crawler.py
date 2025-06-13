#!/usr/bin/env python3
"""Simple crawler to collect APA document titles from the Dutch Tax Authority website."""

import requests
from bs4 import BeautifulSoup
import re
import time
import json
from urllib.parse import urljoin
from typing import Set, List
import logging


class APATitleCrawler:
    """Crawl APA pages and collect document titles."""

    def __init__(self, base_url: str, delay: float = 1.0):
        self.base_url = base_url
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        })
        self.visited: Set[str] = set()
        self.titles: Set[str] = set()
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def fetch(self, url: str) -> BeautifulSoup | None:
        """Fetch URL and return BeautifulSoup object."""
        try:
            self.logger.info("Fetching %s", url)
            resp = self.session.get(url, timeout=30)
            resp.raise_for_status()
            return BeautifulSoup(resp.text, "lxml")
        except Exception as exc:
            self.logger.warning("Failed to fetch %s: %s", url, exc)
            return None

    def extract_titles(self, soup: BeautifulSoup) -> None:
        """Extract APA titles from given soup."""
        pattern = re.compile(r"\b\d{8}\s+APA\s+\d{6}\b")
        for text in soup.stripped_strings:
            m = pattern.search(text)
            if m:
                self.titles.add(m.group())

    def crawl_page(self, url: str) -> None:
        if url in self.visited:
            return
        self.visited.add(url)
        soup = self.fetch(url)
        if not soup:
            return
        self.extract_titles(soup)
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if href.startswith("#"):
                continue
            full = urljoin(url, href)
            if self.base_url in full and full not in self.visited:
                time.sleep(self.delay)
                self.crawl_page(full)

    def crawl(self) -> List[str]:
        self.crawl_page(self.base_url)
        return sorted(self.titles)


def main() -> None:
    base_url = (
        "https://www.belastingdienst.nl/wps/wcm/connect/"
        "bldcontentnl/standaard_functies/prive/contact/"
        "rechten_en_plichten_bij_de_belastingdienst/ruling/apa"
    )
    crawler = APATitleCrawler(base_url)
    titles = crawler.crawl()
    print("Found titles:")
    for t in titles:
        print(t)
    with open("apa_titles.json", "w", encoding="utf-8") as f:
        json.dump({"titles": titles}, f, indent=2, ensure_ascii=False)
    print("Saved titles to apa_titles.json")


if __name__ == "__main__":
    main()
