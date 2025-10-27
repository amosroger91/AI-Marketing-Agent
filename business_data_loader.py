#!/usr/bin/env python3
"""
Business Data Loader - ANY City/State
Handles loading business data from multiple sources

Sources supported:
1. Local CSV files
2. Hardcoded databases
3. Web scraping (requires additional setup)
4. API integrations (BBB, Google Places)

For now, this provides a framework for loading data from CSV files
which you can populate from BBB, Google Maps exports, etc.
"""

import csv
import os
from typing import List, Dict, Any
import json

class BusinessDataLoader:
    """Load business data for any city/state"""

    def __init__(self, data_dir: str = "business_data"):
        self.data_dir = data_dir
        self.ensure_data_dir()

    def ensure_data_dir(self):
        """Create data directory if it doesn't exist"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def get_city_filename(self, city: str, state: str) -> str:
        """Generate standardized filename for city data"""
        city_slug = city.lower().replace(" ", "_")
        state_slug = state.lower().replace(" ", "_")
        return f"{city_slug}_{state_slug}.csv"

    def load_from_csv(self, city: str, state: str) -> List[Dict[str, Any]]:
        """
        Load businesses from CSV file

        CSV format (headers):
        name,address,phone,website

        Example:
        Smith Brothers Auto Repair,"2324 Garrison Avenue, Fort Smith, AR 72901",479-782-5500,smithbrosautoftsmith.com
        """
        filename = self.get_city_filename(city, state)
        filepath = os.path.join(self.data_dir, filename)

        if not os.path.exists(filepath):
            return None

        businesses = []
        try:
            with open(filepath, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    businesses.append({
                        'name': row.get('name', '').strip(),
                        'address': row.get('address', '').strip(),
                        'phone': row.get('phone', '').strip(),
                        'website': row.get('website', '').strip(),
                    })
            return businesses
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return None

    def load_from_json(self, city: str, state: str) -> List[Dict[str, Any]]:
        """
        Load businesses from JSON file

        JSON format:
        [
          {
            "name": "Company Name",
            "address": "123 Main St, City, ST 12345",
            "phone": "123-456-7890",
            "website": "company.com"
          },
          ...
        ]
        """
        filename = self.get_city_filename(city, state).replace('.csv', '.json')
        filepath = os.path.join(self.data_dir, filename)

        if not os.path.exists(filepath):
            return None

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading JSON: {e}")
            return None

    def load_businesses(self, city: str, state: str) -> List[Dict[str, Any]]:
        """
        Load businesses for city/state from available sources

        Tries sources in order:
        1. CSV file (business_data/city_state.csv)
        2. JSON file (business_data/city_state.json)
        3. None if neither exists
        """
        # Try CSV first
        data = self.load_from_csv(city, state)
        if data:
            return data

        # Try JSON second
        data = self.load_from_json(city, state)
        if data:
            return data

        # Nothing found
        return None

    def get_available_cities(self) -> List[tuple]:
        """List all available cities in data directory"""
        if not os.path.exists(self.data_dir):
            return []

        cities = []
        for filename in os.listdir(self.data_dir):
            if filename.endswith('.csv') or filename.endswith('.json'):
                # Parse filename: city_state.ext
                base = filename.rsplit('.', 1)[0]
                parts = base.rsplit('_', 1)
                if len(parts) == 2:
                    city = parts[0].replace('_', ' ').title()
                    state = parts[1].replace('_', ' ').upper()
                    cities.append((city, state))

        return sorted(set(cities))

    def create_sample_csv(self, city: str, state: str):
        """Create sample CSV template for a city"""
        filename = self.get_city_filename(city, state)
        filepath = os.path.join(self.data_dir, filename)

        if os.path.exists(filepath):
            print(f"File already exists: {filepath}")
            return

        sample_data = [
            ['name', 'address', 'phone', 'website'],
            ['Example Company', '123 Main Street, ' + city + ', ' + state + ' 12345', '555-123-4567', 'example.com'],
            ['Another Business', '456 Oak Avenue, ' + city + ', ' + state + ' 12345', '555-987-6543', ''],
        ]

        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(sample_data)
            print(f"Created template: {filepath}")
            print("Now add your business data!")
        except Exception as e:
            print(f"Error creating CSV: {e}")


def show_instructions():
    """Show instructions for adding business data"""
    print("""
================================================================================
HOW TO ADD BUSINESS DATA FOR YOUR CITY/STATE
================================================================================

Option 1: Use CSV Files (Easiest)
----------------------------------
1. Create file: business_data/city_state.csv
   Example: business_data/fayetteville_ar.csv

2. Format (with headers):
   name,address,phone,website
   Smith's Auto Repair,"123 Main St, Fayetteville, AR 72701",479-555-1234,smithsauto.com
   Jones Plumbing,"456 Oak Ave, Fayetteville, AR 72701",479-555-5678,jonesplumbing.com

3. You can get this data from:
   - Google Maps (download list)
   - BBB.org (Better Business Bureau)
   - Local chamber of commerce
   - Yelp business directory
   - Local yellowpages

Option 2: Use JSON Files
------------------------
1. Create file: business_data/city_state.json

2. Format:
   [
     {
       "name": "Company Name",
       "address": "123 Main St, City, ST 12345",
       "phone": "555-123-4567",
       "website": "company.com"
     },
     {
       "name": "Another Company",
       "address": "456 Oak Ave, City, ST 12345",
       "phone": "555-987-6543",
       "website": ""
     }
   ]

Option 3: Export from Google Maps/BBB
--------------------------------------
1. Go to Google Maps or BBB.org
2. Search for businesses in your city
3. Filter by category if needed
4. Export or copy the list
5. Convert to CSV format (name, address, phone, website)
6. Save to business_data/city_state.csv

================================================================================
""")


if __name__ == '__main__':
    import sys

    loader = BusinessDataLoader()

    if len(sys.argv) > 1 and sys.argv[1] == 'list':
        print("Available cities:")
        cities = loader.get_available_cities()
        if cities:
            for city, state in cities:
                data = loader.load_businesses(city, state)
                print(f"  {city}, {state}: {len(data)} businesses")
        else:
            print("  None. Create a CSV file first.")

    elif len(sys.argv) > 2 and sys.argv[1] == 'create':
        city = sys.argv[2]
        state = sys.argv[3] if len(sys.argv) > 3 else 'AR'
        loader.create_sample_csv(city, state)

    else:
        show_instructions()
        print("\nUsage:")
        print("  python3 business_data_loader.py list")
        print("  python3 business_data_loader.py create \"City Name\" ST")
