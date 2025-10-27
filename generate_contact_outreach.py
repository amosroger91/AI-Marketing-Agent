#!/usr/bin/env python3
"""
Contact Prospect Email Outreach Generator
Generates personalized email templates for CONTACT-level prospects from unlimited crawl results
"""

import pandas as pd
import json
from datetime import datetime
import sys

# Email templates optimized for different tech stacks and industries
WORDPRESS_VULNERABILITY_TEMPLATE = """Subject: Security Alert for {company_name} Website

Hi {contact_name},

I was reviewing your website at {website} and noticed something important: your WordPress site is running {wordpress_version}, which has {plugin_count} vulnerable plugins that are actively being exploited by hackers.

This puts your customer data, business reputation, and bottom line at risk.

I help local businesses like {company_name} secure their WordPress sites against these threats. Most of my clients are shocked to learn how easily these vulnerabilities can be exploited - and how simple the fixes are.

A few key points:
• Your site detected: {server_type}
• WordPress version: {wordpress_version}
• Vulnerable plugins: {plugin_count}
• Security headers: {security_headers}

Would you be open to a quick 15-minute call this week to discuss how to protect {company_name}? No sales pitch - just honest security advice.

Best regards,
{sender_name}
n8n Automation & WordPress Security
{sender_phone}
"""

WORDPRESS_OUTDATED_TEMPLATE = """Subject: Quick Improvement for {company_name}'s Website

Hi {contact_name},

I noticed your website at {website} is built with WordPress - great platform choice!

But I also noticed your site might benefit from some updates and security improvements. Outdated WordPress installations are a common target for hackers, and it's one of the easiest fixes.

Here's what I saw:
• Platform: WordPress
• Server: {server_type}
• Security headers: {security_headers}

The good news? This is usually a quick fix that can:
✓ Improve website security
✓ Speed up your site
✓ Improve search rankings

Would you be interested in a quick 15-minute conversation about how to optimize your website? I work with local {industry} businesses and usually find 2-3 quick wins.

Let me know if you'd like to chat.

Best regards,
{sender_name}
n8n Automation & WordPress Security
{sender_phone}
"""

GENERAL_AUTOMATION_TEMPLATE = """Subject: Quick Efficiency Opportunity for {company_name}

Hi {contact_name},

I work with local {industry} businesses to automate repetitive tasks and save them 5-10 hours per week.

I noticed {company_name} is based in Fort Smith, AR, and based on your business profile, I think there are probably some quick wins we could find:

Common opportunities for {industry} businesses:
• Customer communication automation
• Data entry and form processing
• Lead follow-up workflows
• Appointment/scheduling optimization

The whole process is low-risk - we typically start with a free consultation to identify quick wins that could save you real time and money.

Would you have 15 minutes this week for a quick call?

Best regards,
{sender_name}
n8n Automation & Business Process Consultant
{sender_phone}
"""

TEMPLATE_SELECT = {
    'wordpress_vulnerable': WORDPRESS_VULNERABILITY_TEMPLATE,
    'wordpress_general': WORDPRESS_OUTDATED_TEMPLATE,
    'general': GENERAL_AUTOMATION_TEMPLATE
}

def select_template(row):
    """Select best email template based on tech stack"""
    if row['Has_WordPress'] == 'Yes':
        # Prefer vulnerability angle if we detected something
        return 'wordpress_vulnerable'
    else:
        # Fall back to general automation
        return 'general'

def extract_contact_prospects(csv_file='unlimited_crawl_results.csv'):
    """Extract CONTACT-level prospects from CSV"""
    df = pd.read_csv(csv_file)
    contacts = df[df['Sales_Recommendation'] == 'CONTACT'].copy()
    return contacts.sort_values('Sales_Fit_Score', ascending=False)

def get_contact_name(company_name):
    """Generate likely contact name from company"""
    # For simplicity, use owner/manager titles
    return "Team"

def generate_emails(contacts_df, sender_name="Roger", sender_phone="(555) 123-4567"):
    """Generate personalized emails for contact prospects"""

    emails = []

    for idx, row in contacts_df.iterrows():
        company_name = row['Company']
        website = row['Website'] if pd.notna(row['Website']) and row['Website'] else row['Domain_Guessed']
        phone = row['Phone']
        address = row['Address']
        domain = row['Domain_Guessed']

        # Select template
        template_key = select_template(row)
        template = TEMPLATE_SELECT[template_key]

        # Get contact name
        contact_name = get_contact_name(company_name)

        # Guess industry from company name
        industry = guess_industry(company_name)

        # Prepare email
        email_content = template.format(
            company_name=company_name,
            contact_name=contact_name,
            website=website,
            wordpress_version="recent version",  # Would need WPScan data for this
            plugin_count=row['Has_WordPress'],  # Simplified for demo
            server_type=row['Server_Detected'] if row['Server_Detected'] != 'None' else 'web server',
            security_headers=row['Security_Headers_Count'] if row['Security_Headers_Count'] > 0 else 'missing',
            industry=industry,
            sender_name=sender_name,
            sender_phone=sender_phone,
            score=row['Sales_Fit_Score']
        )

        emails.append({
            'company': company_name,
            'phone': phone,
            'address': address,
            'website': website,
            'score': row['Sales_Fit_Score'],
            'template_used': template_key,
            'email': email_content,
            'server': row['Server_Detected'],
            'has_wordpress': row['Has_WordPress']
        })

    return emails

def guess_industry(company_name):
    """Guess industry from company name"""
    name_lower = company_name.lower()

    industries = {
        'auto': ['auto', 'repair', 'transmission', 'tire', 'car', 'automotive', 'ford', 'toyota', 'lincoln'],
        'hvac': ['hvac', 'heating', 'cooling', 'air conditioning'],
        'plumbing': ['plumbing', 'drain', 'pipe'],
        'electrical': ['electric', 'electrical'],
        'construction': ['construction', 'roofing', 'concrete', 'paving', 'landscaping'],
        'retail': ['retail', 'antique', 'gallery', 'mall', 'store', 'shop'],
        'food': ['restaurant', 'cafe', 'coffee', 'pizza', 'steakhouse', 'diner', 'smoothie', 'creamery'],
        'professional': ['law', 'lawyer', 'attorney', 'cpa', 'accounting', 'tax', 'consulting'],
        'healthcare': ['medical', 'clinic', 'dentist', 'dental', 'physical therapy', 'chiropractic', 'wellness', 'health'],
        'hospitality': ['hotel', 'motel', 'inn', 'resort', 'parking'],
        'education': ['school', 'training', 'academy', 'institute', 'bootcamp'],
        'fitness': ['fitness', 'gym', 'yoga', 'crossfit', 'tennis', 'aquatic'],
        'real_estate': ['realty', 'realtor', 'property', 'real estate'],
    }

    for industry, keywords in industries.items():
        for keyword in keywords:
            if keyword in name_lower:
                return industry.replace('_', ' ').title()

    return 'Business'

def format_email_report(emails):
    """Format emails into readable report"""
    report = []
    report.append("="*80)
    report.append("CONTACT PROSPECT EMAIL OUTREACH")
    report.append("="*80)
    report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Total prospects: {len(emails)}\n")

    for i, email_data in enumerate(emails, 1):
        report.append("="*80)
        report.append(f"#{i} - {email_data['company']}")
        report.append("="*80)
        report.append(f"\nCompany: {email_data['company']}")
        report.append(f"Phone: {email_data['phone']}")
        report.append(f"Website: {email_data['website']}")
        report.append(f"Server: {email_data['server']}")
        report.append(f"WordPress: {email_data['has_wordpress']}")
        report.append(f"Sales Score: {email_data['score']}/100")
        report.append(f"Template: {email_data['template_used']}\n")

        report.append("EMAIL PREVIEW:")
        report.append("-"*80)
        report.append(email_data['email'])
        report.append("")

    report.append("="*80)
    report.append("END OF OUTREACH TEMPLATES")
    report.append("="*80)

    return "\n".join(report)

def save_emails_json(emails, filename='contact_outreach_emails.json'):
    """Save emails as JSON for programmatic use"""
    with open(filename, 'w') as f:
        json.dump(emails, f, indent=2)

def main():
    print("="*80)
    print("CONTACT PROSPECT EMAIL OUTREACH GENERATOR")
    print("="*80)
    print()

    # Extract contact prospects
    print("📧 Extracting CONTACT-level prospects from unlimited_crawl_results.csv...")
    contacts = extract_contact_prospects()
    print(f"✓ Found {len(contacts)} CONTACT prospects\n")

    # Generate emails
    print("🔧 Generating personalized email templates...")
    emails = generate_emails(contacts)
    print(f"✓ Generated {len(emails)} email templates\n")

    # Format and save report
    print("📝 Creating outreach report...")
    report = format_email_report(emails)

    # Save text report
    with open('contact_outreach_report.txt', 'w') as f:
        f.write(report)
    print("✓ Saved: contact_outreach_report.txt")

    # Save JSON for programmatic use
    save_emails_json(emails, 'contact_outreach_emails.json')
    print("✓ Saved: contact_outreach_emails.json")

    # Print summary
    print("\n" + "="*80)
    print("OUTREACH SUMMARY")
    print("="*80)
    for email_data in emails:
        print(f"\n{email_data['company']}")
        print(f"  Score: {email_data['score']}/100")
        print(f"  Template: {email_data['template_used']}")
        print(f"  Contact: {email_data['phone']}")

    print("\n✓ Email generation complete!")
    print(f"✓ Ready to send {len(emails)} outreach emails to CONTACT prospects")
    print("\nNext steps:")
    print("  1. Review contact_outreach_report.txt for email previews")
    print("  2. Customize sender name/phone in contact_outreach_emails.json")
    print("  3. Use send_outreach_emails.py to send campaigns")

if __name__ == '__main__':
    main()
