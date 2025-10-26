#!/usr/bin/env python3
"""
Enhanced OSINT Gathering + Tech Stack Detection + Sales Viability Assessment
Tests OSINT, detects tech stacks, runs WPScan, and assesses sales fit
"""

import json
import csv
import sys
import os
from datetime import datetime
from enhanced_osint_gathering import gather_all_osint
from enhanced_tech_detection import TechStackDetector
from sales_viability_filter import SalesViabilityFilter

OUTPUT_TXT = "enhanced_osint_results.txt"
OUTPUT_CSV = "enhanced_osint_results.csv"
FINAL_REPORT = "enhanced_osint_final_report.txt"

# Test domains
TEST_DOMAINS = [
    {
        "name": "Smith's Auto Repair",
        "domain": "smithsauto.local",
        "url": "https://smithsauto.local",
        "email": "contact@smithsauto.local",
        "location": "Fort Smith, AR"
    },
    {
        "name": "Local Pizza House",
        "domain": "localpizza.local",
        "url": "https://localpizza.local",
        "email": "manager@localpizza.local",
        "location": "Fort Smith, AR"
    },
    {
        "name": "WordPress Test",
        "domain": "wordpress.com",
        "url": "https://wordpress.com",
        "email": "contact@wordpress.com",
        "location": "Online"
    },
    {
        "name": "Example Domain",
        "domain": "example.com",
        "url": "https://example.com",
        "email": "contact@example.com",
        "location": "Online"
    },
    {
        "name": "Google",
        "domain": "google.com",
        "url": "https://google.com",
        "email": "contact@google.com",
        "location": "Mountain View, CA"
    },
    {
        "name": "GitHub",
        "domain": "github.com",
        "url": "https://github.com",
        "email": "contact@github.com",
        "location": "San Francisco, CA"
    },
]


def write_output(message: str, file_path=OUTPUT_TXT):
    """Write to file and print"""
    print(message)
    with open(file_path, 'a') as f:
        f.write(message + "\n")


def parse_osint_data(osint_data):
    """Extract key metrics from OSINT data"""
    total_findings = 0
    has_whois = False
    has_dns = False
    has_reverse_dns = False
    registrant = "N/A"
    registrar = "N/A"
    nameservers = "N/A"
    creation_date = "N/A"
    a_records = 0
    mx_records = 0
    ns_records = 0
    txt_records = 0

    # Count WHOIS findings
    if osint_data.get('whois'):
        has_whois = len(osint_data['whois']) > 0
        if has_whois:
            registrant = osint_data['whois'].get('registrant', 'N/A')
            registrar = osint_data['whois'].get('registrar', 'N/A')
            nameservers = ', '.join(osint_data['whois'].get('nameservers', []))
            creation_date = osint_data['whois'].get('creation_date', 'N/A')
            total_findings += len([v for v in osint_data['whois'].values() if v])

    # Check reverse DNS
    if osint_data.get('dns_reverse'):
        has_reverse_dns = len(osint_data['dns_reverse']) > 0

    # Count DNS records
    if osint_data.get('dns'):
        has_dns = len(osint_data['dns']) > 0
        a_records = len(osint_data['dns'].get('a_records', []))
        mx_records = len(osint_data['dns'].get('mx_records', []))
        ns_records = len(osint_data['dns'].get('ns_records', []))
        txt_records = len(osint_data['dns'].get('txt_records', []))
        total_findings += a_records + mx_records + ns_records + txt_records

    return {
        'total_findings': total_findings,
        'has_whois': 'Yes' if has_whois else 'No',
        'has_dns': 'Yes' if has_dns else 'No',
        'has_reverse_dns': 'Yes' if has_reverse_dns else 'No',
        'registrant': str(registrant)[:50],
        'registrar': str(registrar)[:50],
        'nameservers': str(nameservers)[:100],
        'creation_date': str(creation_date)[:30],
        'a_records': a_records,
        'mx_records': mx_records,
        'ns_records': ns_records,
        'txt_records': txt_records,
    }


def generate_csv(osint_results):
    """Generate CSV from OSINT results with tech stack and sales fit"""
    with open(OUTPUT_CSV, 'w', newline='') as f:
        fieldnames = [
            'Company', 'Domain', 'URL', 'Email', 'Status', 'IP_Address', 'Total_OSINT_Findings',
            'Tech_Stack_JSON', 'Sales_Signals_JSON',
            'Sales_Fit_Score', 'Sales_Recommendation', 'Sales_Reasons_JSON',
            'Has_WHOIS', 'Has_DNS', 'Has_Reverse_DNS',
            'Registrant', 'Registrar', 'Creation_Date',
            'A_Records', 'MX_Records', 'NS_Records', 'TXT_Records'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for result in osint_results:
            status = 'Success' if result['total_findings'] > 0 else 'Failed'
            row = {
                'Company': result['name'],
                'Domain': result['domain'],
                'URL': result['url'],
                'Email': result['email'],
                'Status': status,
                'IP_Address': result.get('ip_address', 'N/A'),
                'Total_OSINT_Findings': result['total_findings'],
                'Tech_Stack_JSON': json.dumps(result.get('tech_stack', {})),
                'Sales_Signals_JSON': json.dumps(result.get('sales_signals', {})),
                'Sales_Fit_Score': result.get('sales_fit_score', 0),
                'Sales_Recommendation': result.get('sales_recommendation', 'UNKNOWN'),
                'Sales_Reasons_JSON': json.dumps(result.get('sales_reasons', [])),
                'Has_WHOIS': result['has_whois'],
                'Has_DNS': result['has_dns'],
                'Has_Reverse_DNS': result['has_reverse_dns'],
                'Registrant': result['registrant'],
                'Registrar': result['registrar'],
                'Creation_Date': result['creation_date'],
                'A_Records': result['a_records'],
                'MX_Records': result['mx_records'],
                'NS_Records': result['ns_records'],
                'TXT_Records': result['txt_records'],
            }
            writer.writerow(row)

    print(f"✓ CSV created: {OUTPUT_CSV}")


def main():
    """Main test: OSINT -> Tech Stack -> Sales Viability Assessment"""

    # Determine how many domains to test
    num_tests = int(sys.argv[1]) if len(sys.argv) > 1 else len(TEST_DOMAINS)
    test_domains = TEST_DOMAINS[:num_tests]

    # Clear previous results
    for f in [OUTPUT_TXT, OUTPUT_CSV, FINAL_REPORT]:
        if os.path.exists(f):
            os.remove(f)

    write_output("="*80)
    write_output("ENHANCED OSINT + TECH STACK + SALES VIABILITY TEST")
    write_output("="*80)
    write_output(f"\nStarted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    write_output(f"Testing {len(test_domains)} domains\n")

    osint_results = []

    # PHASE 1: OSINT GATHERING + TECH STACK DETECTION + SALES ASSESSMENT
    write_output(f"\n{'='*80}")
    write_output("PHASE 1: COMPREHENSIVE ANALYSIS")
    write_output(f"{'='*80}\n")

    for idx, test in enumerate(test_domains, 1):
        name = test['name']
        domain = test['domain']
        url = test['url']

        write_output(f"[{idx}/{len(test_domains)}] {name}")

        try:
            # OSINT Gathering
            write_output(f"  • Gathering OSINT...", OUTPUT_TXT)
            osint_data = gather_all_osint(domain, url)
            parsed = parse_osint_data(osint_data)

            # Tech Stack Detection
            write_output(f"  • Detecting tech stack...", OUTPUT_TXT)
            tech_stack = TechStackDetector.analyze_tech_stack(url)
            sales_signals = TechStackDetector.extract_sales_signals(tech_stack)

            # Sales Viability Assessment
            write_output(f"  • Assessing sales fit...", OUTPUT_TXT)
            sales_fit_score, sales_recommendation, sales_reasons = SalesViabilityFilter.assess_sales_fit(
                company_name=name,
                location=test.get('location', ''),
                domain=domain,
                osint_findings=parsed['total_findings'],
                tech_stack=tech_stack,
                sales_signals=sales_signals
            )

            result = {
                'name': name,
                'domain': domain,
                'url': url,
                'email': test['email'],
                'location': test.get('location', ''),
                'ip_address': osint_data.get('ip', 'N/A'),
                'total_findings': parsed['total_findings'],
                'tech_stack': tech_stack,
                'sales_signals': sales_signals,
                'sales_fit_score': sales_fit_score,
                'sales_recommendation': sales_recommendation,
                'sales_reasons': sales_reasons,
                **parsed
            }

            osint_results.append(result)
            write_output(f"  ✓ Complete (Score: {sales_fit_score}, {sales_recommendation})\n")

        except Exception as e:
            write_output(f"  ✗ Error: {str(e)}\n")
            osint_results.append({
                'name': name,
                'domain': domain,
                'url': url,
                'email': test['email'],
                'location': test.get('location', ''),
                'ip_address': 'N/A',
                'total_findings': 0,
                'tech_stack': {},
                'sales_signals': {},
                'sales_fit_score': 0,
                'sales_recommendation': 'ERROR',
                'sales_reasons': [str(e)],
                'has_whois': 'No',
                'has_dns': 'No',
                'has_reverse_dns': 'No',
                'registrant': 'N/A',
                'registrar': 'N/A',
                'creation_date': 'N/A',
                'a_records': 0,
                'mx_records': 0,
                'ns_records': 0,
                'txt_records': 0,
            })

    # PHASE 2: CSV GENERATION
    write_output(f"\n{'='*80}")
    write_output("PHASE 2: CSV GENERATION")
    write_output(f"{'='*80}\n")

    generate_csv(osint_results)
    write_output("")

    # PHASE 3: FINAL REPORT
    write_output(f"\n{'='*80}")
    write_output("PHASE 3: SALES VIABILITY REPORT")
    write_output(f"{'='*80}\n")

    write_output("\n" + "="*80, FINAL_REPORT)
    write_output("SALES VIABILITY ASSESSMENT REPORT", FINAL_REPORT)
    write_output("="*80 + "\n", FINAL_REPORT)
    write_output(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n", FINAL_REPORT)

    # Sort by sales fit score
    ranked = sorted(osint_results, key=lambda x: x['sales_fit_score'], reverse=True)

    for idx, result in enumerate(ranked, 1):
        write_output(f"\n{'='*80}", FINAL_REPORT)
        write_output(f"#{idx} - {result['name']}", FINAL_REPORT)
        write_output(f"{'='*80}\n", FINAL_REPORT)

        write_output(f"Company: {result['name']}", FINAL_REPORT)
        write_output(f"Domain: {result['domain']}", FINAL_REPORT)
        write_output(f"Location: {result['location']}", FINAL_REPORT)
        write_output(f"Email: {result['email']}\n", FINAL_REPORT)

        write_output(f"SALES FIT ASSESSMENT:", FINAL_REPORT)
        write_output(f"  Score: {result['sales_fit_score']}/100", FINAL_REPORT)
        write_output(f"  Recommendation: {result['sales_recommendation']}", FINAL_REPORT)
        if result['sales_reasons']:
            write_output(f"  Reasons:", FINAL_REPORT)
            for reason in result['sales_reasons']:
                write_output(f"    - {reason}", FINAL_REPORT)
        write_output("", FINAL_REPORT)

        write_output(f"TECH STACK DETECTED:", FINAL_REPORT)
        tech = result['tech_stack']
        if tech.get('server'):
            write_output(f"  Server: {json.dumps(tech['server'], indent=4)}", FINAL_REPORT)
        if tech.get('wordpress', {}).get('is_wordpress'):
            write_output(f"  WordPress: {json.dumps(tech['wordpress'], indent=4)}", FINAL_REPORT)
        if tech.get('other_cms'):
            write_output(f"  Other CMS: {json.dumps(tech['other_cms'], indent=4)}", FINAL_REPORT)
        write_output("", FINAL_REPORT)

        write_output(f"SALES SIGNALS:", FINAL_REPORT)
        signals = result['sales_signals']
        write_output(f"  Opportunity Score: {signals.get('opportunity_score', 0)}", FINAL_REPORT)
        if signals.get('pain_points'):
            for pain_point in signals['pain_points']:
                write_output(f"    • {pain_point}", FINAL_REPORT)
        write_output("", FINAL_REPORT)

    # Summary
    write_output(f"\n{'='*80}")
    write_output("TEST SUMMARY")
    write_output(f"{'='*80}\n")

    total_findings = sum(r['total_findings'] for r in osint_results)
    successful = sum(1 for r in osint_results if r['total_findings'] > 0)
    good_fit = sum(1 for r in osint_results if r['sales_recommendation'] == 'CONTACT')

    write_output(f"Domains analyzed: {len(osint_results)}")
    write_output(f"Successful OSINT: {successful}")
    write_output(f"Total OSINT findings: {total_findings}")
    write_output(f"Good sales fit: {good_fit}\n")

    write_output(f"Output files:")
    write_output(f"  - CSV data: {OUTPUT_CSV}")
    write_output(f"  - Final report: {FINAL_REPORT}")
    write_output(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    print(f"\n✓ Test complete!")
    print(f"View final report: cat {FINAL_REPORT}")


if __name__ == "__main__":
    main()
