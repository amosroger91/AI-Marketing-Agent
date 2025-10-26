# AI-Marketing-Agent

An intelligent email outreach system that uses Kali Linux OSINT tools, chain filtering, and AI-powered email generation to identify and contact local businesses.

## Features

### Core Functionality
- **Chain Filtering**: Automatically filters out franchise chains and corporate entities using 500+ keywords
- **Company Research**: Gathers information from multiple sources including websites, public registries, and OSINT
- **Email Generation**: AI-powered email composition using Gemini API with personalized content based on company information
- **Email Delivery**: Integrates with msmtp for reliable email sending

### Information Gathering
- **Enhanced OSINT**: Comprehensive reconnaissance using multiple Kali Linux tools:
  - WHOIS lookups (domain registrant, registrar, nameserver information)
  - DNS enumeration (A, AAAA, MX, TXT, NS, CNAME records)
  - Reverse DNS lookups
  - Port scanning with Nmap
  - HTTP header analysis for technology detection
  - Nikto web vulnerability scanning
  - DNSRecon comprehensive DNS enumeration
  - Fierce subdomain enumeration
  - Shodan device/service queries

- **WordPress Detection**: Identifies WordPress sites and gathers plugin/vulnerability information
- **Email Discovery**: Uses theHarvester to find additional email addresses and subdomains
- **Web Scraping**: BBB and company directory integration for lead discovery

### Testing
- Complete test suites demonstrating email generation without sending
- Real website validation with URL connectivity checks
- Kali tool integration testing
- Enhanced OSINT gathering demonstrations

## Project Structure

```
consolidated_outreach/
├── automate_outreach.py              # Main orchestration script
├── send_outreach_emails.py           # Email delivery implementation
├── enhanced_info_gathering.py        # Chain filtering and enhanced gathering
├── enhanced_osint_gathering.py       # Comprehensive Kali Linux OSINT tools
├── test_email_generation.py          # Email generation test suite
├── test_real_website_validation.py   # Website validation with Kali tools
├── test_enhanced_osint.py            # Enhanced OSINT gathering test
├── CLAUDE.md                         # Architecture and command documentation
└── README.md                         # This file
```

## Installation

### Requirements
- Python 3.8+
- Kali Linux or system with Kali tools installed:
  - whois
  - dig
  - nmap
  - nikto
  - dnsrecon
  - fierce
  - wpscan
  - curl

### Python Dependencies
```bash
pip install requests beautifulsoup4 selenium shodan dnspython
```

### Configuration
1. Set up environment variables for sensitive data:
   - `SHODAN_API_KEY`: Your Shodan API key (optional)
   - Email credentials for msmtp

2. Edit company lists and test data as needed

## Usage

### Testing Email Generation
```bash
# Test all companies
python3 test_email_generation.py

# Test specific number of companies
python3 test_email_generation.py 2
```

### Real Website Validation
```bash
python3 test_real_website_validation.py
```

### Enhanced OSINT Gathering
```bash
python3 test_enhanced_osint.py
```

### Full Outreach Process
```bash
python3 automate_outreach.py
```

## Output Files

- `email_generation_test_results.txt` - Full email generation details
- `email_generation_test_summary.csv` - Tabular email summary
- `real_website_validation_results.txt` - Website validation details
- `enhanced_osint_results.txt` - Comprehensive OSINT findings

## Security Notes

- **Chain Filtering**: Ensures compliance with regulations and avoids targeting franchise operations
- **URL Validation**: Only processes responsive websites
- **Credential Protection**: Sensitive data is in .gitignore
- **Rate Limiting**: Built-in delays to avoid blocking

## Key Features Explained

### Chain Filtering
The system uses a sophisticated chain detection mechanism with:
- 500+ keywords matching franchise patterns
- Multi-layer detection (company name, address, context)
- Whitelisted terms for false positive prevention

### Email Personalization
Emails are generated with:
- Company-specific context and research
- Location-based personalization
- Technology stack awareness (WordPress detection)
- Custom offerings based on industry

### OSINT Integration
Leverages industry-standard tools for:
- Infrastructure mapping
- Technology identification
- Vulnerability assessment
- Subdomain discovery

## Testing Workflow

1. **Chain Filtering**: Validates company against chain database
2. **URL Validation**: Ensures website is responsive
3. **OSINT Gathering**: Collects information using Kali tools
4. **Email Generation**: Creates personalized email
5. **Output**: Generates preview and CSV export

## Limitations

- WordPress detection uses heuristics (not 100% accurate)
- theHarvester depends on search engine limits
- Port scanning may be blocked by firewalls
- Requires Kali tools to be installed

## Contributing

This project demonstrates various information gathering and email automation techniques. Ensure all usage complies with:
- Terms of service of target websites
- Local regulations on automated contact
- Privacy and data protection laws

## License

Educational use only. Ensure compliance with all applicable laws and terms of service.
# AI-Marketing-Agent
