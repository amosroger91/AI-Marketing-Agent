#!/usr/bin/env python3
"""
Email Outreach Generator for Verified Prospects
Automatically generates personalized emails for ANY city's verified crawl results

Usage:
    python3 generate_outreach_emails.py "fort_smith" "ar"
    python3 generate_outreach_emails.py "fayetteville" "ar"

Input: [city]_[state]_verified_results.csv (from crawl_verified.py)
Output:
    - [city]_[state]_outreach_emails.txt (email previews)
    - [city]_[state]_outreach_emails.json (structured data)
    - [city]_[state]_outreach_report.txt (summary + strategy)
"""

import pandas as pd
import json
import sys
import os
from datetime import datetime

# Email templates optimized for different tech stacks and industries
WORDPRESS_VULNERABILITY_TEMPLATE = """Subject: Security Alert for {company_name} Website

Hi {contact_name},

I was reviewing your website at {website} and noticed something important: your WordPress site has {plugin_count} vulnerable plugins that are actively being exploited by hackers.

This puts your customer data, business reputation, and bottom line at risk.

I help local businesses like {company_name} secure their WordPress sites against these threats. Most of my clients are shocked to learn how easily these vulnerabilities can be exploited - and how simple the fixes are.

A few key points:
• Your site detected: {server_type}
• WordPress site found: ✓
• Vulnerable plugins: {plugin_count}
• Security headers: {security_headers}

Would you be open to a quick 15-minute call this week to discuss how to protect {company_name}? No sales pitch - just honest security advice.

Best regards,
{sender_name}
n8n Automation & WordPress Security Specialist
{sender_phone}
{sender_email}
"""

WORDPRESS_GENERAL_TEMPLATE = """Subject: Quick Security & Automation Opportunity for {company_name}

Hi {contact_name},

I noticed {company_name} has a WordPress-powered website - great platform choice!

I work with local {industry} businesses to:
✓ Secure WordPress sites against common vulnerabilities
✓ Automate repetitive business processes
✓ Improve website performance & security

Based on {company_name}'s profile, I think there are probably some quick wins we could find:

• Website security assessment (usually reveals 2-3 quick fixes)
• Automation opportunities (process efficiency, time savings)
• Performance optimization

Would you be interested in a quick 15-minute conversation? I typically find immediate improvements that save time and money.

Best regards,
{sender_name}
n8n Automation & WordPress Security Specialist
{sender_phone}
{sender_email}
"""

GENERAL_AUTOMATION_TEMPLATE = """Subject: Efficiency Opportunity for {company_name}

Hi {contact_name},

I work with local {industry} businesses to automate repetitive tasks and save them 5-10 hours per week.

For {industry} businesses like {company_name}, common automation opportunities include:
• Customer communication workflows
• Data entry and form processing
• Scheduling and appointment management
• Invoice generation and follow-ups
• Lead tracking and follow-up

The process is low-risk - we typically start with a free consultation to identify quick wins.

Would you have 15 minutes this week to explore what might work for {company_name}?

Best regards,
{sender_name}
n8n Automation & Business Process Consultant
{sender_phone}
{sender_email}
"""

def select_template(row):
    """Select best email template based on tech stack"""
    if row['Has_WordPress'] == 'Yes':
        # Prefer security angle if WordPress detected
        return 'wordpress_general'
    else:
        # Fall back to general automation
        return 'general'

def guess_industry(company_name):
    """Guess industry from company name"""
    name_lower = company_name.lower()

    industries = {
        'auto': ['auto', 'repair', 'transmission', 'tire', 'car', 'automotive', 'ford', 'toyota', 'lincoln', 'chevrolet'],
        'hvac': ['hvac', 'heating', 'cooling', 'air conditioning', 'hvac'],
        'plumbing': ['plumbing', 'drain', 'pipe', 'water'],
        'electrical': ['electric', 'electrical', 'electrician'],
        'construction': ['construction', 'roofing', 'concrete', 'paving', 'landscaping', 'contractor'],
        'retail': ['retail', 'antique', 'gallery', 'mall', 'store', 'shop', 'boutique'],
        'food': ['restaurant', 'cafe', 'coffee', 'pizza', 'steakhouse', 'diner', 'smoothie', 'creamery', 'bakery'],
        'professional': ['law', 'lawyer', 'attorney', 'cpa', 'accounting', 'tax', 'consulting', 'consultant'],
        'healthcare': ['medical', 'clinic', 'dentist', 'dental', 'physical therapy', 'chiropractic', 'wellness', 'health', 'doctor'],
        'hospitality': ['hotel', 'motel', 'inn', 'resort', 'parking', 'venue'],
        'education': ['school', 'training', 'academy', 'institute', 'bootcamp', 'learning'],
        'fitness': ['fitness', 'gym', 'yoga', 'crossfit', 'tennis', 'aquatic', 'recreation'],
        'real_estate': ['realty', 'realtor', 'property', 'real estate', 'appraisal'],
    }

    for industry, keywords in industries.items():
        for keyword in keywords:
            if keyword in name_lower:
                return industry.replace('_', ' ').title()

    return 'Business'

def get_contact_name(row):
    """Try to extract likely contact name"""
    # Simple heuristic - use generic for now
    return "Team"

def generate_emails(csv_file, sender_name="Roger", sender_phone="(555) 123-4567", sender_email="roger@example.com"):
    """Generate emails from verified crawl results CSV"""

    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found")
        print("\nFirst, run:")
        city_state = csv_file.replace('_verified_results.csv', '')
        parts = city_state.rsplit('_', 1)
        if len(parts) == 2:
            city, state = parts[0].replace('_', ' ').title(), parts[1].upper()
            print(f"  python3 crawl_verified.py \"{city}\" \"{state}\"")
        return None

    # Load CSV
    df = pd.read_csv(csv_file)

    if len(df) == 0:
        print(f"Error: {csv_file} is empty")
        return None

    emails = []

    for idx, row in df.iterrows():
        company_name = row['Company']
        website = row['Website'] if pd.notna(row['Website']) and row['Website'] else row['Domain_Verified']
        phone = row['Contact_Phone']
        address = row['Address']
        domain = row['Domain_Verified']

        # Select template
        template_key = select_template(row)
        if template_key == 'wordpress_vulnerability':
            template = WORDPRESS_VULNERABILITY_TEMPLATE
        elif template_key == 'wordpress_general':
            template = WORDPRESS_GENERAL_TEMPLATE
        else:
            template = GENERAL_AUTOMATION_TEMPLATE

        # Get contact name
        contact_name = get_contact_name(row)

        # Guess industry
        industry = guess_industry(company_name)

        # Count security headers
        security_headers_count = row['Security_Headers_Count'] if pd.notna(row['Security_Headers_Count']) else 0
        security_headers = f"{int(security_headers_count)} headers" if security_headers_count > 0 else "missing"

        # Prepare email
        email_content = template.format(
            company_name=company_name,
            contact_name=contact_name,
            website=website,
            plugin_count="multiple" if row['Has_WordPress'] == 'Yes' else "unknown",
            server_type=row['Server_Detected'] if row['Server_Detected'] != 'None' else 'web server',
            security_headers=security_headers,
            industry=industry,
            sender_name=sender_name,
            sender_phone=sender_phone,
            sender_email=sender_email,
        )

        emails.append({
            'company': company_name,
            'phone': phone,
            'address': address,
            'website': website,
            'domain': domain,
            'score': row['Sales_Fit_Score'],
            'recommendation': row['Sales_Recommendation'],
            'template_used': template_key,
            'email': email_content,
            'server': row['Server_Detected'],
            'has_wordpress': row['Has_WordPress'],
            'industry': industry,
        })

    return emails

def format_email_report(emails, city: str, state: str):
    """Format emails into readable report"""
    report = []
    report.append("="*80)
    report.append(f"EMAIL OUTREACH CAMPAIGN - {city.upper()}, {state.upper()}")
    report.append("="*80)
    report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Total prospects: {len(emails)}\n")

    # Group by recommendation
    contacts = [e for e in emails if e['recommendation'] == 'CONTACT']
    maybes = [e for e in emails if e['recommendation'] == 'MAYBE']
    excludes = [e for e in emails if e['recommendation'] == 'EXCLUDE']

    report.append(f"CONTACT prospects (score 70+): {len(contacts)}")
    report.append(f"MAYBE prospects (score 50-69): {len(maybes)}")
    report.append(f"EXCLUDE prospects (score <50): {len(excludes)}\n")

    # Show emails
    for i, email_data in enumerate(emails, 1):
        report.append("="*80)
        report.append(f"#{i} - {email_data['company']}")
        report.append("="*80)
        report.append(f"\nCompany: {email_data['company']}")
        report.append(f"Phone: {email_data['phone']}")
        report.append(f"Website: {email_data['website']}")
        report.append(f"Domain: {email_data['domain']}")
        report.append(f"Industry: {email_data['industry']}")
        report.append(f"Score: {email_data['score']}/100")
        report.append(f"Recommendation: {email_data['recommendation']}")
        report.append(f"Server: {email_data['server']}")
        report.append(f"WordPress: {email_data['has_wordpress']}\n")

        report.append("EMAIL PREVIEW:")
        report.append("-"*80)
        report.append(email_data['email'])
        report.append("")

    report.append("="*80)
    report.append("END OF OUTREACH TEMPLATES")
    report.append("="*80)

    return "\n".join(report)

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 generate_outreach_emails.py <city> <state>")
        print("\nExamples:")
        print("  python3 generate_outreach_emails.py \"Fort Smith\" \"AR\"")
        print("  python3 generate_outreach_emails.py \"Fayetteville\" \"AR\"")
        print("\nThis reads from: [city]_[state]_verified_results.csv")
        print("First run: python3 crawl_verified.py \"City\" \"State\"")
        sys.exit(1)

    city = sys.argv[1]
    state = sys.argv[2]
    city_slug = city.lower().replace(" ", "_")
    state_slug = state.lower().replace(" ", "_")

    csv_file = f"{city_slug}_{state_slug}_verified_results.csv"

    print("="*80)
    print("EMAIL OUTREACH GENERATOR")
    print("="*80)
    print()

    # Generate emails
    print(f"📧 Generating emails for {city}, {state}...")
    emails = generate_emails(csv_file)

    if not emails:
        return

    print(f"✓ Generated {len(emails)} email templates\n")

    # Format and save report
    print("📝 Creating outreach report...")
    report = format_email_report(emails, city, state)

    # Save text report
    report_file = f"{city_slug}_{state_slug}_outreach_report.txt"
    with open(report_file, 'w') as f:
        f.write(report)
    print(f"✓ Saved: {report_file}")

    # Save JSON for programmatic use
    emails_json_file = f"{city_slug}_{state_slug}_outreach_emails.json"
    with open(emails_json_file, 'w') as f:
        json.dump(emails, f, indent=2)
    print(f"✓ Saved: {emails_json_file}")

    # Print summary
    print("\n" + "="*80)
    print("EMAIL GENERATION SUMMARY")
    print("="*80)

    contact = len([e for e in emails if e['recommendation'] == 'CONTACT'])
    maybe = len([e for e in emails if e['recommendation'] == 'MAYBE'])
    exclude = len([e for e in emails if e['recommendation'] == 'EXCLUDE'])

    print(f"\nTotal prospects: {len(emails)}")
    print(f"  CONTACT (70+): {contact}")
    print(f"  MAYBE (50-69): {maybe}")
    print(f"  EXCLUDE (<50): {exclude}")

    print(f"\nIndustry breakdown:")
    industries = {}
    for email in emails:
        ind = email['industry']
        industries[ind] = industries.get(ind, 0) + 1

    for ind, count in sorted(industries.items(), key=lambda x: x[1], reverse=True):
        print(f"  {ind}: {count}")

    print("\n✓ Email generation complete!")
    print(f"✓ Ready to customize and send {len(emails)} outreach emails")
    print("\nNext steps:")
    print(f"  1. Review {report_file} for email previews")
    print(f"  2. Customize sender details in {emails_json_file} if needed")
    print(f"  3. Copy Contact_Phone from {csv_file} into your dialer/CRM")
    print(f"  4. Send emails or make phone calls (your choice!)")

if __name__ == '__main__':
    main()
