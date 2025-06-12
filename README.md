# PDF Downloader for Belastingdienst APA Page

This script downloads all PDF files listed on the [Belastingdienst APA ruling page](https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/standaard_functies/prive/contact/rechten_en_plichten_bij_de_belastingdienst/ruling/apa).

## Features

- Automatically finds all PDF links on the page
- Downloads each PDF into a local `pdfs/` directory

## Requirements

- Python 3.6+
- `requests`
- `beautifulsoup4`

Install requirements:

```bash
pip install requests beautifulsoup4
