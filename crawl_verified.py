#!/usr/bin/env python3
"""
Universal VERIFIED Business Crawl - Any City/State
Loads business data and runs verified domain checking

Usage:
    python3 crawl_verified.py "Fayetteville" "AR"
    python3 crawl_verified.py "Little Rock" "AR"
    python3 crawl_verified.py "Bentonville" "AR"

Requirements:
1. Business data file in business_data/ directory
   - Format: business_data/fayetteville_ar.csv
   - Columns: name, address, phone, website

2. To create business data for a new city:
   python3 business_data_loader.py create "City Name" "ST"

3. Then populate the CSV with data from:
   - Google Maps
   - BBB.org
   - Yelp
   - Local chamber of commerce
"""

import csv
import sys
from datetime import datetime
from business_data_loader import BusinessDataLoader
from domain_verification import DomainVerifier
from enhanced_tech_detection import TechStackDetector
from sales_viability_filter import SalesViabilityFilter

def write_log(message: str, file_path: str, to_stdout=True):
    """Write to log and optionally print"""
    if to_stdout:
        print(message)
    with open(file_path, 'a') as f:
        f.write(message + "\n")

def run_crawl(city: str, state: str):
    """Run verified crawl for specified city"""
    # Setup file names
    city_slug = city.lower().replace(" ", "_")
    state_slug = state.lower().replace(" ", "_")
    output_csv = f"{city_slug}_{state_slug}_verified_results.csv"
    execution_log = f"{city_slug}_{state_slug}_verified_execution.log"

    # Clear old logs
    open(execution_log, 'w').close()

    write_log("="*80, execution_log)
    write_log(f"VERIFIED BUSINESS CRAWL - {city.upper()}, {state.upper()}", execution_log)
    write_log("="*80, execution_log)
    write_log(f"\nStarted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", execution_log)
    write_log("CRITICAL: Only companies with VERIFIED domains will be included", execution_log)
    write_log("Each domain must respond to HTTP request before being analyzed\n", execution_log)

    # Load business data
    write_log("Loading business data...", execution_log)
    loader = BusinessDataLoader()
    businesses = loader.load_businesses(city, state)

    if not businesses:
        write_log(f"❌ No data file found for {city}, {state}", execution_log)
        write_log("", execution_log)
        write_log("To add this city:", execution_log)
        write_log(f"  1. python3 business_data_loader.py create \"{city}\" \"{state}\"", execution_log)
        write_log(f"  2. Populate business_data/{city_slug}_{state_slug}.csv", execution_log)
        write_log(f"  3. Run: python3 crawl_verified.py \"{city}\" \"{state}\"", execution_log)
        return

    write_log(f"✓ Loaded {len(businesses)} businesses\n", execution_log)

    # Phase 0: Domain Verification
    write_log("="*80, execution_log)
    write_log("PHASE 0: DOMAIN VERIFICATION (HTTP Request Test)", execution_log)
    write_log("="*80 + "\n", execution_log)

    verifier = DomainVerifier()
    verified_businesses = []

    for i, business in enumerate(businesses, 1):
        if i % 10 == 0 or i == 1:
            write_log(f"  Verified {i}/{len(businesses)}...", execution_log)

        company_name = business['name']
        website_provided = business.get('website', '')

        # Try to verify the domain
        if website_provided:
            result = verifier.verify_domain(website_provided)
            if result['verified']:
                verified_businesses.append({
                    **business,
                    'verified_domain': result['domain'],
                    'verification_result': result
                })
                continue

        # If provided domain failed, try common patterns
        patterns = [
            company_name.lower().replace(' ', ''),
            company_name.lower().replace(' ', '-'),
            company_name.lower().split()[0],  # First word only
        ]

        found = False
        for pattern in patterns:
            for tld in ['com', 'net', 'org', 'biz']:
                domain = f"{pattern}.{tld}"
                result = verifier.verify_domain(domain)
                if result['verified']:
                    verified_businesses.append({
                        **business,
                        'verified_domain': result['domain'],
                        'verification_result': result
                    })
                    found = True
                    break
            if found:
                break

    write_log(f"\n✓ Domain verification complete:", execution_log)
    write_log(f"  Verified: {len(verified_businesses)} ({100*len(verified_businesses)//len(businesses)}%)", execution_log)
    write_log(f"  Failed: {len(businesses) - len(verified_businesses)} ({100*(len(businesses)-len(verified_businesses))//len(businesses)}%)", execution_log)
    write_log("", execution_log)

    if not verified_businesses:
        write_log("❌ No verified businesses found. Stopping.", execution_log)
        return

    # Phase 1: Tech Detection & Sales Assessment
    write_log("="*80, execution_log)
    write_log("PHASE 1: TECH DETECTION & SALES ASSESSMENT", execution_log)
    write_log("="*80 + "\n", execution_log)

    detector = TechStackDetector()
    filter_viability = SalesViabilityFilter()
    results = []

    for i, business in enumerate(verified_businesses, 1):
        if i % 10 == 0 or i == 1:
            write_log(f"  Processed {i}/{len(verified_businesses)}...", execution_log)

        domain = business['verified_domain']

        # Detect tech stack
        tech_stack = detector.analyze_tech_stack(domain)
        signals = detector.extract_sales_signals(tech_stack)

        # Pure script-based scoring
        score = 50
        recommendation = "MAYBE"
        reasons = []

        company_lower = business['name'].lower()
        for keyword in filter_viability.EXCLUDE_KEYWORDS:
            if keyword in company_lower:
                score = 0
                recommendation = "EXCLUDE"
                reasons = [f"Matches exclusion keyword: {keyword}"]
                break

        if recommendation != "EXCLUDE":
            if tech_stack.get('wordpress', {}).get('is_wordpress'):
                score += 20
                reasons.append("WordPress detected")

            if tech_stack.get('server', {}).get('server'):
                score += 15
                reasons.append(f"Server: {tech_stack['server']['server']}")

            vulnerable_count = len(tech_stack.get('wordpress', {}).get('vulnerable_plugins', []))
            if vulnerable_count > 0:
                score += 25
                reasons.append(f"{vulnerable_count} vulnerable plugins")

            if tech_stack.get('wordpress', {}).get('outdated_core'):
                score += 15
                reasons.append("Outdated WordPress")

            security_headers = len(tech_stack.get('server', {}).get('security_headers', {}))
            if security_headers == 0:
                score += 10
                reasons.append("Missing security headers")

            score = min(score, 100)

            if score >= 70:
                recommendation = "CONTACT"
            elif score >= 50:
                recommendation = "MAYBE"
            else:
                recommendation = "EXCLUDE"

        result = {
            'Company': business['name'],
            'Address': business['address'],
            'Phone': business['phone'],
            'Contact_Phone': business['phone'],
            'Website': business.get('website', ''),
            'Domain_Verified': domain,
            'Sales_Fit_Score': score,
            'Sales_Recommendation': recommendation,
            'Has_WordPress': 'Yes' if tech_stack.get('wordpress', {}).get('is_wordpress') else 'No',
            'Server_Detected': tech_stack.get('server', {}).get('server') or 'None',
            'Security_Headers_Count': len(tech_stack.get('server', {}).get('security_headers', {}))
        }
        results.append(result)

    write_log(f"\n  Processed {len(verified_businesses)}/{len(verified_businesses)}...", execution_log)
    write_log("", execution_log)

    # Phase 2: CSV Output
    write_log("="*80, execution_log)
    write_log("PHASE 2: CSV GENERATION", execution_log)
    write_log("="*80 + "\n", execution_log)

    with open(output_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'Company', 'Address', 'Phone', 'Contact_Phone',
            'Website', 'Domain_Verified',
            'Sales_Fit_Score', 'Sales_Recommendation', 'Has_WordPress',
            'Server_Detected', 'Security_Headers_Count'
        ])
        writer.writeheader()
        writer.writerows(results)

    write_log(f"✓ CSV created: {output_csv}", execution_log)
    write_log("", execution_log)

    # Phase 3: Summary
    write_log("="*80, execution_log)
    write_log("PHASE 3: RESULTS SUMMARY", execution_log)
    write_log("="*80 + "\n", execution_log)

    contact = len([r for r in results if r['Sales_Recommendation'] == 'CONTACT'])
    maybe = len([r for r in results if r['Sales_Recommendation'] == 'MAYBE'])
    exclude = len([r for r in results if r['Sales_Recommendation'] == 'EXCLUDE'])

    write_log("Final Statistics:", execution_log)
    write_log(f"  Total businesses in database: {len(businesses)}", execution_log)
    write_log(f"  Domain verification passed: {len(verified_businesses)}", execution_log)
    write_log(f"  Successfully analyzed: {len(results)}", execution_log)
    write_log(f"  CONTACT (70+): {contact}", execution_log)
    write_log(f"  MAYBE (50-69): {maybe}", execution_log)
    write_log(f"  EXCLUDE (<50): {exclude}", execution_log)
    write_log("", execution_log)

    if contact > 0:
        write_log(f"Top CONTACT Prospects:", execution_log)
        write_log("", execution_log)
        contact_results = [r for r in results if r['Sales_Recommendation'] == 'CONTACT']
        contact_results.sort(key=lambda x: x['Sales_Fit_Score'], reverse=True)
        for i, r in enumerate(contact_results[:10], 1):
            write_log(f"  #{i} - {r['Company']}: Score {r['Sales_Fit_Score']}", execution_log)

    write_log("", execution_log)
    write_log(f"Output files:", execution_log)
    write_log(f"  - CSV data: {output_csv}", execution_log)
    write_log(f"  - Execution log: {execution_log}", execution_log)
    write_log("", execution_log)
    write_log(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", execution_log)
    write_log("", execution_log)
    write_log("✓ Verified crawl complete!", execution_log)
    write_log(f"✓ Processed {len(results)} verified businesses", execution_log)
    write_log(f"✓ Found {contact} CONTACT prospects", execution_log)

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 crawl_verified.py \"City Name\" \"State Code\"")
        print("\nExamples:")
        print("  python3 crawl_verified.py \"Fort Smith\" \"AR\"")
        print("  python3 crawl_verified.py \"Fayetteville\" \"AR\"")
        print("  python3 crawl_verified.py \"Little Rock\" \"AR\"")
        print("\nTo add a new city:")
        print("  1. python3 business_data_loader.py create \"City Name\" \"ST\"")
        print("  2. Edit business_data/city_state.csv with your data")
        print("  3. Run: python3 crawl_verified.py \"City Name\" \"ST\"")
        print("\nTo list available cities:")
        print("  python3 business_data_loader.py list")
        sys.exit(1)

    city = sys.argv[1]
    state = sys.argv[2]

    run_crawl(city, state)

if __name__ == '__main__':
    main()
