# Multi-City Business Crawl Guide

## Quick Start

Run verified crawl for ANY city/state:

```bash
python3 crawl_verified.py "Fayetteville" "AR"
python3 crawl_verified.py "Little Rock" "AR"
python3 crawl_verified.py "Bentonville" "AR"
```

## Step-by-Step: Add a New City

### Step 1: Create Template
```bash
python3 business_data_loader.py create "City Name" "ST"
```

This creates: `business_data/city_state.csv`

Example:
```bash
python3 business_data_loader.py create "Fayetteville" "AR"
```

Creates: `business_data/fayetteville_ar.csv`

### Step 2: Populate with Business Data

Edit the CSV file and add business information. Format:

```csv
name,address,phone,website
Smith's Auto Repair,"123 Main St, Fayetteville, AR 72701",479-555-1234,smithsauto.com
Jones Plumbing,"456 Oak Ave, Fayetteville, AR 72701",479-555-5678,jonesplumbing.com
Local Coffee Shop,"789 Elm St, Fayetteville, AR 72701",479-555-9999,
```

**Required columns:**
- `name` - Company name
- `address` - Full address
- `phone` - Contact phone number
- `website` - Website (can be blank if unknown)

### Step 3: Get Business Data

You can populate the CSV from these sources:

#### Option A: Google Maps (Easiest)
1. Go to Google Maps
2. Search "[City Name], [State]" + "[Category]" (e.g., "Restaurants")
3. Export/download the list (or manually copy)
4. Paste into Excel/Google Sheets
5. Save as CSV
6. Import to business_data/city_state.csv

#### Option B: BBB.org
1. Go to bbb.org
2. Search by city
3. Filter by category
4. Copy business information
5. Paste into CSV

#### Option C: Yelp
1. Go to yelp.com
2. Search city + category
3. View the list of businesses
4. Copy name, address, phone into CSV
5. Visit each website to verify/add domain

#### Option D: Local Chamber of Commerce
1. Visit local chamber website
2. Download member directory if available
3. Convert to CSV format
4. Populate the CSV file

#### Option E: LinkedIn Local
1. Use LinkedIn Local feature
2. Filter by location and industry
3. Export results if available

### Step 4: Run the Crawl

```bash
python3 crawl_verified.py "Fayetteville" "AR"
```

This will:
1. Load your business data
2. Verify each domain via HTTP request
3. Detect tech stack (WordPress, servers, security)
4. Score each prospect (0-100)
5. Output CSV with results

### Step 5: Review Results

Output files:
- `fayetteville_ar_verified_results.csv` - Your prospect list with scores
- `fayetteville_ar_verified_execution.log` - Execution details

## Example Workflow

### 1. Setup Fort Smith (Already Done)
```bash
# Fort Smith data already in business_data/fort_smith_ar.csv
python3 crawl_verified.py "Fort Smith" "AR"
# Output: fort_smith_ar_verified_results.csv (48 verified prospects)
```

### 2. Add Fayetteville
```bash
# Create template
python3 business_data_loader.py create "Fayetteville" "AR"

# Populate from Google Maps (download list, save to CSV)
# Edit business_data/fayetteville_ar.csv and paste data

# Run crawl
python3 crawl_verified.py "Fayetteville" "AR"

# Review results
cat fayetteville_ar_verified_execution.log
```

### 3. Add Little Rock
```bash
python3 business_data_loader.py create "Little Rock" "AR"
# Edit business_data/little_rock_ar.csv
python3 crawl_verified.py "Little Rock" "AR"
```

## List Available Cities

```bash
python3 business_data_loader.py list
```

Output:
```
Available cities:
  Fort Smith, AR: 84 businesses
  Fayetteville, AR: 120 businesses
  Little Rock, AR: 250 businesses
```

## Scaling to Multiple Cities

### Batch Processing Script
Create `batch_crawl.sh`:

```bash
#!/bin/bash

CITIES=(
  "Fort Smith:AR"
  "Fayetteville:AR"
  "Bentonville:AR"
  "Little Rock:AR"
  "Rogers:AR"
  "Jonesboro:AR"
  "Springdale:AR"
  "Conway:AR"
)

for city_state in "${CITIES[@]}"; do
  IFS=':' read -r city state <<< "$city_state"
  echo "Processing $city, $state..."
  python3 crawl_verified.py "$city" "$state"
done

echo "All crawls complete!"
```

Run it:
```bash
chmod +x batch_crawl.sh
./batch_crawl.sh
```

## Data Quality Tips

### Ensure Accurate Phone Numbers
- Use current phone numbers
- Include area code (479, 501, etc. for Arkansas)
- Format: 123-456-7890 or (123) 456-7890

### Verify Addresses
- Include full street address
- Include city, state, ZIP code
- Example: "123 Main St, Fayetteville, AR 72701"

### Website Domain Hints
- Don't invent domains
- Leave blank if unknown
- The crawler will try common patterns
- Only verified domains appear in output

### Categories to Prioritize
For maximum ROI, focus on:
1. **Professional Services** (lawyers, accountants, consultants)
   - Higher likely spend on automation
   - Small teams, good contractor fit

2. **Service Businesses** (plumbing, HVAC, construction)
   - Scheduling/job management pain points
   - Clear ROI on automation

3. **Retail/Food** (restaurants, shops, boutiques)
   - Inventory management opportunities
   - Customer management systems needed

4. **Healthcare** (clinics, dental, physical therapy)
   - Appointment scheduling
   - Patient intake automation

5. **Real Estate** (agents, property management)
   - High potential for automation
   - Multiple leads tracking

## File Structure

```
consolidated_outreach/
├── business_data/                    # Business lists by city
│   ├── fort_smith_ar.csv            # Fort Smith businesses
│   ├── fayetteville_ar.csv          # Fayetteville businesses (if added)
│   └── little_rock_ar.csv           # Little Rock businesses (if added)
├── crawl_verified.py                 # Main crawl script (use this!)
├── business_data_loader.py           # Data loading utility
├── domain_verification.py            # HTTP/DNS verification
├── enhanced_tech_detection.py        # Tech stack detection
├── fort_smith_ar_verified_results.csv        # Results from crawl
├── fayetteville_ar_verified_results.csv      # Results from crawl
└── [city]_[state]_verified_results.csv       # Results for each city
```

## Troubleshooting

### "No data file found"
```
Error: No data file found for Fayetteville, AR
```

**Solution:** Create the CSV file first:
```bash
python3 business_data_loader.py create "Fayetteville" "AR"
```

Then populate `business_data/fayetteville_ar.csv` with data.

### "0 verified businesses"
**Cause:** All domains failed verification (don't exist or don't respond to HTTP)

**Solution:**
1. Check domain names in CSV are correct
2. Verify websites exist by visiting manually
3. Some small businesses may not have websites (mark as blank, crawler tries patterns)

### "All prospects scored 50 (MAYBE)"
**Cause:** WordPress not detected on domains

**Reason:** Not all websites are WordPress. Some are:
- Custom-built sites
- Static HTML
- Other CMS (Drupal, Joomla, Magento)
- Sites behind WAF/proxy

**This is OK!** 50 is honest baseline. Can still reach out about automation.

## Commands Reference

```bash
# Create template for new city
python3 business_data_loader.py create "City Name" "ST"

# List all available cities
python3 business_data_loader.py list

# Run crawl for specific city
python3 crawl_verified.py "City Name" "ST"

# View results for Fort Smith
cat fort_smith_ar_verified_execution.log
head -20 fort_smith_ar_verified_results.csv
```

## Next Steps

1. **Start with Fort Smith** (already populated)
   - `python3 crawl_verified.py "Fort Smith" "AR"`

2. **Add Fayetteville**
   - `python3 business_data_loader.py create "Fayetteville" "AR"`
   - Populate with Google Maps data
   - Run crawl

3. **Scale to other Arkansas cities**
   - Create CSVs for Little Rock, Rogers, Jonesboro, etc.
   - Run batch_crawl.sh for all at once

4. **Move to other states**
   - Same process works for any city/state
   - Just create new CSV files

## Support

If crawler fails on a domain:
- Check if domain actually exists
- Visit it in browser manually
- Verify DNS resolves
- Check if site requires special headers (WAF, proxies)

Most small business sites will verify without issues.
