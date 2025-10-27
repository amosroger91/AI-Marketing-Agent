# Lead Finder: Find Real Businesses in Your City (No AI Hallucination)

A tool that finds **verified, real businesses** in any US city and generates personalized outreach emails. Everything runs on your computer. Zero SaaS fees. 100% honest data.

## Why This Is Different

Most "lead generation" tools either:
- Use fake, hallucinated data (companies that don't exist)
- Make guesses about what's on websites (wrong email templates)
- Require expensive SaaS subscriptions ($99-500+/month)
- Send emails automatically (you lose control)

**This tool does none of that.**

Instead, it:
✓ **Verifies every domain exists** with actual HTTP requests  
✓ **Detects real tech stacks** (WordPress, servers, security tools)  
✓ **Uses honest scoring** based only on what's actually on their website  
✓ **Runs completely offline** on your computer  
✓ **Costs $0** (just your time to run it)  
✓ **You control when emails send** (not automatic)  
✓ **Works for anyone** (custom sender personas)  

## The 3-Step Process

### Step 1: Gather Business Data (5 minutes)
Create a list of businesses in your target city from real sources:
- Google Maps search results
- Better Business Bureau (bbb.org)
- Yelp business directory
- Chamber of Commerce
- LinkedIn Local search

Save as a simple CSV file:
```
name,address,phone,website
Smith's Auto Repair,"123 Main St, Fort Smith, AR 72701",479-555-1234,smithsauto.com
Jones Plumbing,"456 Oak Ave, Fort Smith, AR 72701",479-555-5678,
Local Coffee,"789 Elm St, Fort Smith, AR 72701",479-555-9999,coffeeshop.com
```

### Step 2: Verify & Analyze (2-5 minutes depending on list size)
Run the verification crawler:
```bash
python3 crawl_verified.py "Your City" "Your State"
```

Example:
```bash
python3 crawl_verified.py "Fort Smith" "AR"
```

What happens:
- Loads your business CSV
- **Tests every domain** with actual HTTP requests (no guessing)
- Detects tech stack (WordPress, server software, security)
- Scores each business (0-100) based on REAL findings
- Outputs verified prospects only

**Real example from Fort Smith:**
- Input: 84 businesses
- After verification: 48 verified prospects (57%)
- Only includes businesses with working websites
- All have valid phone numbers

### Step 3: Generate Emails (1 minute)
Create personalized outreach emails:
```bash
python3 generate_outreach_emails.py "Your City" "Your State"
```

Example:
```bash
python3 generate_outreach_emails.py "Fort Smith" "AR"
```

What you get:
- `fort_smith_ar_outreach_report.txt` - Preview of all emails
- `fort_smith_ar_outreach_emails.json` - Ready to send (email client, CRM, or automation tool)

**Real example:** 48 prospects, industry breakdown, customized email templates

## Installation

### Requirements
- Python 3.7+
- `pandas` (for CSV handling)
- `requests` (for HTTP verification)

### Setup
```bash
# Install dependencies
pip install pandas requests

# You're done!
```

That's it. No accounts, no APIs, no subscriptions.

## Usage Examples

### For Your City
```bash
# Step 1: Create template for your city
python3 business_data_loader.py create "Fayetteville" "AR"

# Step 2: Edit business_data/fayetteville_ar.csv
# (Add 20-50 businesses from Google Maps, BBB, etc.)

# Step 3: Verify and analyze
python3 crawl_verified.py "Fayetteville" "AR"

# Step 4: Generate emails
python3 generate_outreach_emails.py "Fayetteville" "AR"

# Step 5: Review emails
cat fayetteville_ar_outreach_report.txt
```

### With Custom Sender Name (Not Just Roger)

Create a `my_persona.json` file:
```json
{
  "name": "Your Name",
  "phone": "(555) 123-4567",
  "email": "you@yourdomain.com",
  "title": "Your Title"
}
```

Then run:
```bash
python3 generate_outreach_emails.py "Fayetteville" "AR" "my_persona.json"
```

### Multiple Cities at Once
```bash
# Create batch_crawl.sh
chmod +x batch_crawl.sh
./batch_crawl.sh

# Generates prospects + emails for 5 cities automatically
```

## What Email Templates Look Like

### Template 1: WordPress Security (for WordPress sites)
```
Subject: Security Alert for {Company} Website

Hi {Contact},

I noticed your website has vulnerable WordPress plugins 
that hackers are actively exploiting.

[Details about specific vulnerabilities found]

Would you be open to a 15-minute call this week to 
discuss protecting your site?

Best,
{Your Name}
```

### Template 2: General Automation (all businesses)
```
Subject: Efficiency Opportunity for {Company}

Hi {Contact},

I work with local {Industry} businesses to automate 
repetitive tasks and save 5-10 hours per week.

[Industry-specific automation ideas]

Would you have 15 minutes this week to explore what 
might work for your business?

Best,
{Your Name}
```

All templates are customized by:
- **Company name** (from your CSV)
- **Industry** (auto-detected from company name)
- **Tech stack** (detected from actual website analysis)
- **Contact phone** (from your CSV for follow-ups)
- **Sender name, phone, email** (from persona file)

## Real Example: Fort Smith, AR

Using the included test data (`fort_smith_ar_business_data.csv`):

**Results:**
- 48 verified prospects from 84 input
- Industries: Auto (4), Healthcare (5), Food (4), Professional (3), Construction (2), etc.
- All have valid phone numbers
- All have working websites
- All scored based on real tech detection

**Email Sample:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#1 - Parker Ford Lincoln
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Company: Parker Ford Lincoln
Phone: 479-784-1000
Website: parkerfordlincoln.com
Industry: Automotive
Score: 60/100
Recommendation: MAYBE
Server: nginx
WordPress: No

EMAIL PREVIEW:
────────────────────────────────────────────────────────────────────────────────
Subject: Efficiency Opportunity for Parker Ford Lincoln

Hi Team,

I work with local Automotive businesses to automate repetitive tasks 
and save 5-10 hours per week.

For Automotive businesses like Parker Ford Lincoln, common automation 
opportunities include:
• Appointment scheduling & reminders
• Service invoicing & follow-ups
• Customer communication workflows
• Lead tracking and follow-up

Would you have 15 minutes this week to explore what might work for 
Parker Ford Lincoln?

Best regards,
Roger
n8n Automation & Business Process Consultant
(555) 123-4567
roger@example.com
```

## How Scoring Works

Each prospect gets a **0-100 score** based on REAL, DETECTED tech:

- **50 base score** (neutral - they have a working website)
- **+20** if WordPress detected
- **+15** if advanced server tech detected
- **+10** if strong security headers found
- **+5** if WordPress has vulnerable plugins we can help with

**You'll see:**
- **CONTACT (70+):** Best opportunities, detected tech gaps we can help with
- **MAYBE (50-69):** Good leads, have websites but limited detected tech
- **EXCLUDE (<50):** Skip these (usually outdated sites or no tech detected)

This is **honest scoring** - we're not guessing or hallucinating. Every point is based on something we actually detected on their website.

## FAQ

### Q: Do I have to use all 84 businesses?
**A:** No! Start with 20-30. You can always add more later. More = more prospects.

### Q: What if a domain doesn't verify?
**A:** That company is excluded (probably no website or it's down). This is GOOD - means you won't waste time on dead leads.

### Q: Why are so many scoring 50-60 (MAYBE)?
**A:** Not all websites are WordPress or run on detected tech. Many are:
- Custom-built HTML sites
- Other CMS (Drupal, Joomla, Magento)  
- Static sites
- Sites behind firewalls

But 50 is STILL a good lead! It means they have a working website.

### Q: Can I send these emails automatically?
**A:** Yes! You can:
1. Copy-paste from the report
2. Import the JSON into Gmail, Mailchimp, or your CRM
3. Use the phone numbers for calling instead
4. Set up your own automation with n8n, Zapier, etc.

You control the sending - nothing goes out automatically.

### Q: How many responses should I expect?
**A:** Cold outreach typically gets:
- **2-4% response rate** (1 response per 25-50 emails)
- **10-20% of responses interested** (1 qualified per 125-500 emails)
- **25-50% of interested book calls**

So from 48 emails: expect ~1-2 initial responses, and 0-1 qualified meetings.

### Q: Should I call or email?
**A:** Both! 
- **Email** = higher scale, lower response rate
- **Phone** = lower scale, higher response rate
- **Hybrid** = Email first, then call warm leads (highest conversion)

The CSV includes phone numbers for calling.

### Q: Can I use this for other states?
**A:** Yes! This works for ANY city in ANY state. Just:
1. Create a CSV with businesses from your target city
2. Run `crawl_verified.py "City" "State"`
3. Run `generate_outreach_emails.py "City" "State"`

### Q: Does this require internet?
**A:** Yes, during verification (we need to check their websites). After that, it's offline.

### Q: Is there a limit on how many prospects?
**A:** No. Crawl as many as you want. It will take longer (about 2-3 seconds per prospect to verify).

### Q: Can I use this for B2C (consumers) or just B2B?
**A:** Currently B2B (businesses). For consumers, you'd need a different data source.

## What Gets Saved

For each city you process, you get:

**[city]_[state]_verified_results.csv**
- All verified prospects
- Company name, address, phone, website
- Sales fit score and recommendation
- Tech stack detection results

**[city]_[state]_outreach_report.txt**
- All email previews
- Industry breakdown
- Ready to review before sending

**[city]_[state]_outreach_emails.json**
- Structured email data
- Ready to import into tools
- Can be customized further

**[city]_[state]_verified_execution.log**
- Detailed verification results
- Useful for debugging

## File Structure

```
consolidated_outreach/
├── README.md (this file)
├── COMPLETE_WORKFLOW.txt (detailed workflow)
├── crawl_verified.py (main verification script)
├── generate_outreach_emails.py (email generator)
├── business_data_loader.py (data management)
├── domain_verification.py (HTTP verification)
│
├── business_data/
│   └── fort_smith_ar.csv (example business list)
│
└── [output files for each city]
    ├── fort_smith_ar_verified_results.csv
    ├── fort_smith_ar_outreach_report.txt
    ├── fort_smith_ar_outreach_emails.json
    └── fort_smith_ar_verified_execution.log
```

## Quick Commands Reference

```bash
# Create template for a new city
python3 business_data_loader.py create "City" "State"

# List available cities
python3 business_data_loader.py list

# Run verification crawl
python3 crawl_verified.py "City" "State"

# Generate emails (with default Roger persona)
python3 generate_outreach_emails.py "City" "State"

# Generate emails (with custom persona)
python3 generate_outreach_emails.py "City" "State" "my_persona.json"

# View generated emails
cat [city]_[state]_outreach_report.txt

# View verified prospects
head -20 [city]_[state]_verified_results.csv

# Get phone numbers for dialing
cut -d',' -f4 [city]_[state]_verified_results.csv | tail -n +2
```

## Creating Your Custom Persona

Instead of using the default "Roger" persona, create your own:

1. **Create `my_persona.json`:**
```json
{
  "name": "Sarah Johnson",
  "phone": "(555) 987-6543",
  "email": "sarah@automationservices.com",
  "title": "Business Automation Specialist"
}
```

2. **Run with your persona:**
```bash
python3 generate_outreach_emails.py "Your City" "Your State" "my_persona.json"
```

3. **All emails will now use your name, phone, and email**

You can create different personas for different service offerings:
- `automation_persona.json` - for automation pitches
- `wordpress_persona.json` - for WordPress security pitches
- `consulting_persona.json` - for general consulting

## Troubleshooting

### "CSV not found" error
**Solution:** Create the business data CSV first:
```bash
python3 business_data_loader.py create "City" "State"
# Then edit business_data/[city]_[state].csv
```

### Verification is slow
**Normal:** Takes 2-3 seconds per business (we're making real HTTP requests). For 50 businesses, expect 2-3 minutes.

### No prospects verified (all failed)
**Check:**
1. Are your domains correct? (check the CSV)
2. Are websites actually live? (test in browser)
3. Check the execution log: `cat [city]_[state]_verified_execution.log`

### Email generation fails
**Check:**
1. Does `[city]_[state]_verified_results.csv` exist?
2. Is the CSV not empty? (run `head -5 [file].csv`)
3. Check the CSV format (commas between columns)

## Why This Works

Most lead generation fails because:
1. **Fake data** - AI generates companies that don't exist
2. **Wrong templates** - Emails don't match actual business needs
3. **Too expensive** - SaaS tools cost $100-500/month
4. **No control** - Automated sending means you lose oversight

This tool fixes all of that:
1. **100% verified** - Every domain tested with real HTTP requests
2. **Honest templates** - Based on what we actually detect on their site
3. **Free** - Runs on your computer, costs nothing
4. **You're in control** - You review and send when ready

## Use Cases

### B2B Service Provider (like Roger)
- Sell automation, WordPress security, business consulting
- Use: Find WordPress sites, detect tech gaps, pitch solutions

### Local Agency
- Find small businesses in your area
- Pitch: website redesign, marketing, SEO
- Customize emails by industry

### SaaS Sales
- Find businesses using your competitor's product
- Pitch migration or additional features
- Verify they're in your target industry

### Consultant
- Find businesses in specific industries
- Pitch industry-specific consulting
- Call instead of email (better for services)

### Freelancer
- Find small businesses that need help
- Pitch specific services
- Build local reputation

## Support

If something goes wrong:
1. Check the execution log: `cat [city]_[state]_verified_execution.log`
2. Verify CSV format (check for missing commas, quotes)
3. Test domain manually in browser
4. Check Python version: `python3 --version` (should be 3.7+)

## License

This tool is free. Use it for legitimate business outreach only.

## Next Steps

1. **Start small:** Create a list of 20-30 businesses in your target city
2. **Verify:** Run `crawl_verified.py` to get verified prospects
3. **Generate emails:** Run `generate_outreach_emails.py`
4. **Review:** Check the `.txt` report
5. **Send:** Use phone numbers or import emails into your tool
6. **Track:** Monitor responses
7. **Expand:** Add more cities, refine your approach

**Ready? Run this:**
```bash
python3 business_data_loader.py create "Your City" "Your State"
```

Then edit the CSV and follow the 3-step process above.

---

**Built with:** Honest data. No AI hallucination. No SaaS fees. Just real businesses and real opportunities.
