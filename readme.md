# Belastingdienst APA PDF Crawler

A Python web crawler designed to extract PDF documents from the Dutch Tax Authority's (Belastingdienst) Advance Pricing Agreement (APA) rulings page.

## Overview

This crawler navigates through the APA rulings page at `belastingdienst.nl`, follows intermediate links to individual ruling pages, and extracts the direct PDF download URLs. It handles the multi-step process where:

1. Main page contains links to individual ruling pages
2. Individual pages contain the actual PDF download links
3. PDFs are typically hosted on `download.belastingdienst.nl`

## Features

- **Multi-step crawling**: Handles intermediate pages to find actual PDF links
- **Respectful crawling**: Includes delays between requests
- **Comprehensive logging**: Detailed logs of the crawling process
- **JSON output**: Saves all found documents with metadata
- **PDF downloading**: Optional bulk download of all found PDFs
- **Error handling**: Robust error handling for network issues
- **Flexible link detection**: Multiple strategies for finding PDF links

## Installation

### Prerequisites

- Python 3.7+
- pip

### Setup

1. Clone this repository:
```bash
git clone <your-repo-url>
cd apa-pdf-crawler
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Run the crawler with default settings:

```bash
python crawler.py
```

This will:
- Crawl the main APA page
- Follow all found links to extract PDF URLs
- Save results to `apa_documents.json`
- Create a log file `apa_crawler.log`
- Optionally download all PDFs to a `pdfs/` directory

### Advanced Usage

```python
from crawler import APACrawler

# Initialize crawler with custom settings
crawler = APACrawler(
    base_url="https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/standaard_functies/prive/contact/rechten_en_plichten_bij_de_belastingdienst/ruling/apa",
    delay=2.0  # 2 second delay between requests
)

# Crawl for documents
documents = crawler.crawl_main_page()

# Save results
crawler.save_results("my_results.json")

# Download PDFs
crawler.download_pdfs("my_pdfs")
```

### APA Title Crawler

To crawl only the list of APA titles without downloading PDFs:

```bash
python apa_title_crawler.py
```

This generates `apa_titles.json`, `apa_titles.csv`, and `apa_titles.txt`
containing all titles found on the site. The workflow in
`.github/workflows/crawl_titles.yml` can be triggered manually to produce these
files as build artifacts.

## Output

### JSON Results

The crawler saves results in JSON format with the following structure:

```json
{
  "crawl_date": "2025-06-12T10:30:00",
  "base_url": "https://www.belastingdienst.nl/...",
  "total_documents": 5,
  "documents": [
    {
      "title": "Advance Pricing Agreement 20250603 APA 000005",
      "intermediate_url": "https://www.belastingdienst.nl/.../advance-pricing-agreement-20250603-apa-000005",
      "pdf_url": "https://download.belastingdienst.nl/belastingdienst/docs/rul-20250603-apa-000005.pdf",
      "date_found": "2025-06-12T10:30:15"
    }
  ]
}
```

### Log Files

Detailed logging includes:
- URLs being processed
- PDFs found
- Errors encountered
- Download progress

## Configuration

### Crawler Settings

- `delay`: Time between requests (default: 1.0 seconds)
- `timeout`: Request timeout (default: 30 seconds)
- `user_agent`: Browser user agent string

### Customization

The crawler can be easily customized by modifying:

- `extract_apa_links()`: Change link detection patterns
- `find_pdf_link()`: Modify PDF link extraction logic
- `extract_title()`: Adjust title extraction methods

## GitHub Codespaces

This repository is optimized for GitHub Codespaces:

1. Open the repository in Codespaces
2. Dependencies will be automatically installed
3. Run the crawler directly:
   ```bash
   python crawler.py
   ```

## Rate Limiting

The crawler is designed to be respectful:
- Default 1-second delay between requests
- Proper user agent headers
- Timeout handling
- Error recovery

## Error Handling

The crawler handles common issues:
- Network timeouts
- Invalid URLs
- Missing PDF links
- Server errors
- Rate limiting

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Legal Notice

This tool is for legitimate research and data collection purposes. Please:
- Respect the website's robots.txt
- Use appropriate delays between requests
- Don't overload the server
- Comply with terms of service

## License

MIT License - see LICENSE file for details.

## Troubleshooting

### Common Issues

1. **No PDFs found**: Check if the website structure has changed
2. **Network errors**: Increase timeout or delay settings
3. **Empty results**: Verify the base URL is correct

### Debug Mode

Enable debug logging:

```python
import logging
logging.getLogger().setLevel(logging.DEBUG)
```

## Support

For issues or questions:
1. Check the log files for error details
2. Create an issue on GitHub
3. Include relevant log excerpts

---

**Note**: This crawler is designed specifically for the Dutch Tax Authority's APA rulings page. The website structure may change over time, requiring updates to the crawler logic.
