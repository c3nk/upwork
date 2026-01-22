  ____ _               _      _     _                    
 / ___| | __ _ ___ ___(_) ___(_)___| |_   ___  _ __ __ _ 
| |   | |/ _` / __/ __| |/ __| / __| __| / _ \| '__/ _` |
| |___| | (_| \__ \__ \ | (__| \__ \ |_ | (_) | | | (_| |
 \____|_|\__,_|___/___/_|\___|_|___/\__(_)___/|_|  \__, |
/ ___|  ___ _ __ __ _ _ __   ___ _ __              |___/ 
\___ \ / __| '__/ _` | '_ \ / _ \ '__|                   
 ___) | (__| | | (_| | |_) |  __/ |                      
|____/ \___|_|  \__,_| .__/ \___|_|                      
                     |_|


# scraper-classicist-org

Web scraper for classicist.org membership directory with standardized CLI interface built on cli-standard-kit.

**Developed for Upwork project:** https://www.upwork.com/jobs/~022013748868429862911

This project provides a comprehensive tool for extracting member data from the classicist.org membership directory with professional CLI features.

## ✨ Features

- **Complete Member Directory Scraping**: Extract all 1,500+ members from the membership directory
- **Detailed Member Information**: Scrape individual member pages for complete profiles
- **Professional CLI Interface**: Standardized command-line interface with colored output
- **Multiple Output Formats**: Export data as CSV, JSON, or Excel
- **Certified Member Detection**: Automatically identify certified members
- **Contact Information**: Extract emails, phones, addresses, and locations
- **Social Media Links**: Collect social media profiles and websites
- **Photo and Logo Extraction**: Download member photos and company logos

## 📊 Data Collected

### Directory Listing (Basic Info):
- Member Name or Firm Name
- Certification Status
- Detail Page URL
- Membership Level (Patron, etc.)

### Detailed Member Information:
- **Contact Information**:
  - Mailing Address
  - Phone Number
  - Email Address
  - City, State, Location

- **Professional Information**:
  - Field/Classification (Architect, Contractor, Engineer, etc.)
  - About/Description
  - Highlights/Achievements

- **Media Assets**:
  - Company Logo
  - Member Photos
  - Social Media Links (Facebook, Twitter, LinkedIn, Instagram, etc.)

## 🚀 Installation

### Prerequisites
- Python 3.9+
- Playwright browsers

### Install Dependencies
```bash
# Clone the repository
git clone https://github.com/c3nk/upwork.git
cd upwork/scraper-classicist-org

# Install the package
pip install -e .

# Install Playwright browsers
python -m playwright install chromium
```

## 📖 Usage

### 1. Scrape Member Directory (Basic Info)

Get basic information for all members in the directory:

```bash
# Scrape all members (basic info only)
scraper-classicist scrape --url https://www.classicist.org/membership-directory/ --format csv

# With verbose logging
scraper-classicist --verbose scrape --url https://www.classicist.org/membership-directory/ --format json
```

This will create a CSV/JSON file with:
- Member names
- Certification status
- Detail page URLs
- ~1,500 members total

### 2. Scrape Detailed Member Information

Get complete information for individual members:

```bash
# Scrape details for first 10 members
scraper-classicist scrape-details --input-file outputs/scraped_data_YYYYMMDD_HHMMSS.csv --limit 10

# Scrape details starting from member #50, process 25 members
scraper-classicist scrape-details --input-file outputs/scraped_data_YYYYMMDD_HHMMSS.csv --start-from 50 --limit 25

# Save detailed data to specific directory
scraper-classicist scrape-details --input-file data.csv --limit 50 --output-dir ./detailed-members
```

### 3. Export and Convert Data

Convert between different formats:

```bash
# Convert JSON to CSV
scraper-classicist export data.json --format csv

# Convert CSV to Excel
scraper-classicist export data.csv --format excel
```

### 4. List Available Targets

```bash
# Show scraping targets
scraper-classicist list --type targets

# List previously scraped data
scraper-classicist list --type data --data-dir ./outputs
```

## 📁 Output Data Structure

### CSV Format
```csv
name,field,city,state,location,mailing_address,phone,email,certified,detail_url,about,social_media,logo,highlights,photos_count,timestamp
"A Classical Studio, Inc",Email,Roswell,GA,"Roswell, GA","604 Macy Drive Roswell, GA 30076 (770) 248-2800",aclassicalstudio.com,aclassicalstudio.com,Yes,https://...,"About text...",facebook.com/example,,Award Winner,2,1649021064
```

### JSON Format
```json
{
  "export_info": {
    "timestamp": "2026-01-21T21:45:32.000Z",
    "source": "https://www.classicist.org/membership-directory/",
    "tool": "scraper-classicist-org"
  },
  "scraping_info": {
    "members_found": 1514,
    "errors": []
  },
  "members": [
    {
      "name": "A Classical Studio, Inc",
      "field": "Email",
      "city": "Roswell",
      "state": "GA",
      "mailing_address": "604 Macy Drive Roswell, GA 30076 (770) 248-2800",
      "phone": "",
      "email": "aclassicalstudio.com",
      "certified": true,
      "detail_url": "https://www.classicist.org/membership-directory/a-classical-studio-inc/",
      "about": "About text...",
      "social_media": [
        {"platform": "facebook", "url": "https://facebook.com/example", "text": "Facebook"}
      ],
      "logo": "",
      "highlights": ["Award Winner"],
      "photos": []
    }
  ]
}
```

## 🛠️ CLI Options

### Global Options
- `--verbose, -v`: Enable verbose output
- `--quiet, -q`: Suppress output except errors
- `--dry-run, -n`: Show what would be done without executing
- `--log-file FILE`: Save logs to file
- `--output DIR, -o DIR`: Output directory (default: ./outputs)
- `--json`: Output in JSON format

### Commands
- `scrape`: Scrape membership directory
- `scrape-details`: Scrape individual member details
- `list`: List targets or scraped data
- `export`: Convert between formats

## ⚙️ Configuration

### Directory Structure
```
project/
├── inputs/           # Input files
├── outputs/          # Generated data files
├── inputs/processed/ # Processed files
├── inputs/failed/    # Failed files
└── logs/            # Log files
```

### Rate Limiting
- Directory scraping: No delays (fast)
- Detail scraping: 2-second delays between requests (respectful)
- Configurable delays in `ClassicistScraper` class

## 🔍 Troubleshooting

### Common Issues

1. **Browser Not Found**: Run `python -m playwright install chromium`
2. **Timeout Errors**: Increase timeout in scraper configuration
3. **Empty Results**: Check if website structure changed
4. **Rate Limiting**: Add longer delays between requests

### Debug Mode
```bash
# Enable verbose logging
scraper-classicist --verbose --log-file debug.log scrape --url https://...

# Check generated debug files
ls outputs/debug_*
```

## 📈 Performance Notes

- **Directory Scraping**: ~30 seconds for 1,500 members
- **Detail Scraping**: ~10-15 seconds per member (with 2s delays)
- **Memory Usage**: ~100MB for full directory + details
- **Storage**: ~50MB for complete dataset (CSV + JSON)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## ⚠️ Disclaimer

This scraper is designed for educational and research purposes. Please respect the website's terms of service and robots.txt. Use responsibly and avoid overwhelming the server with requests.