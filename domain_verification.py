#!/usr/bin/env python3
"""
Domain Verification Module
CRITICAL: Makes actual HTTP requests to verify domains exist before analysis
No guessing, no fake data - only real, verified websites
"""

import requests
import socket
from typing import Tuple, Dict, Any
from urllib.parse import urlparse
import time

class DomainVerifier:
    """Verify domain existence through actual HTTP requests"""

    def __init__(self, timeout=5, retries=2):
        self.timeout = timeout
        self.retries = retries
        self.cache = {}  # Cache results to avoid repeated requests

    def get_domain_from_url(self, url: str) -> str:
        """Extract domain from URL"""
        if not url:
            return None

        # Add protocol if missing
        if not url.startswith(('http://', 'https://', '//')):
            url = f"http://{url}"

        try:
            parsed = urlparse(url)
            return parsed.netloc or parsed.path
        except:
            return None

    def domain_has_dns(self, domain: str) -> Tuple[bool, str]:
        """
        Check if domain has valid DNS resolution
        Returns: (success, ip_address or error_message)
        """
        if not domain:
            return False, "Empty domain"

        try:
            ip = socket.gethostbyname(domain)
            return True, ip
        except socket.gaierror:
            return False, f"DNS resolution failed"
        except Exception as e:
            return False, f"DNS error: {str(e)}"

    def domain_responds_to_http(self, domain: str) -> Tuple[bool, int, str]:
        """
        Make actual HTTP request to verify domain is live
        Returns: (success, status_code, server_header or error_message)
        """
        if not domain:
            return False, None, "Empty domain"

        # Check cache first
        cache_key = f"http_check:{domain}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        # Try both http and https
        urls_to_try = [
            f"https://{domain}",
            f"http://{domain}"
        ]

        for url in urls_to_try:
            for attempt in range(self.retries):
                try:
                    response = requests.head(
                        url,
                        timeout=self.timeout,
                        allow_redirects=True,
                        verify=False  # Skip SSL verification for now
                    )

                    server = response.headers.get('Server', 'Unknown')
                    result = (True, response.status_code, server)
                    self.cache[cache_key] = result
                    return result

                except requests.exceptions.Timeout:
                    if attempt == self.retries - 1:
                        continue
                    time.sleep(0.5)
                except requests.exceptions.ConnectionError:
                    continue
                except Exception as e:
                    continue

        # All attempts failed
        result = (False, None, "No HTTP response")
        self.cache[cache_key] = result
        return result

    def verify_domain(self, domain: str, require_dns=True, require_http=True) -> Dict[str, Any]:
        """
        Comprehensive domain verification

        Args:
            domain: Domain to verify (e.g., "example.com" or "http://example.com")
            require_dns: Must have valid DNS resolution
            require_http: Must respond to HTTP request

        Returns:
            {
                'verified': bool,
                'domain': str,
                'dns_valid': bool,
                'dns_ip': str,
                'http_responds': bool,
                'http_status': int,
                'server': str,
                'error': str
            }
        """
        result = {
            'verified': False,
            'domain': domain,
            'dns_valid': False,
            'dns_ip': None,
            'http_responds': False,
            'http_status': None,
            'server': None,
            'error': None
        }

        if not domain:
            result['error'] = "Empty domain"
            return result

        # Extract clean domain
        clean_domain = self.get_domain_from_url(domain)
        if not clean_domain:
            result['error'] = "Invalid domain format"
            return result

        result['domain'] = clean_domain

        # Check DNS
        if require_dns:
            dns_ok, dns_info = self.domain_has_dns(clean_domain)
            result['dns_valid'] = dns_ok
            if dns_ok:
                result['dns_ip'] = dns_info
            else:
                result['error'] = dns_info
                return result  # Stop here if DNS fails

        # Check HTTP
        if require_http:
            http_ok, status_code, server_info = self.domain_responds_to_http(clean_domain)
            result['http_responds'] = http_ok

            if http_ok:
                result['http_status'] = status_code
                result['server'] = server_info
                result['verified'] = True  # SUCCESS
            else:
                result['error'] = server_info
                return result  # Stop here if HTTP fails

        return result

    def verify_multiple_domains(self, domains: list) -> list:
        """Verify list of domains, return only verified ones with full details"""
        verified = []

        for domain in domains:
            if not domain or not isinstance(domain, str):
                continue

            result = self.verify_domain(domain)
            if result['verified']:
                verified.append(result)

        return verified


def verify_website_from_company(company_name: str, website_url: str = None) -> Dict[str, Any]:
    """
    Verify a website for a company

    Strategy:
    1. If website provided, verify that first
    2. If no website or website fails, try guessing common patterns
    3. Only return verified results
    """
    verifier = DomainVerifier()

    # Try provided website first
    if website_url:
        result = verifier.verify_domain(website_url)
        if result['verified']:
            return result

    # Try common domain patterns
    patterns = [
        company_name.lower().replace(' ', ''),  # companyname
        company_name.lower().replace(' ', '-'),  # company-name
        company_name.lower().split()[0],  # firstname only
    ]

    for pattern in patterns:
        for tld in ['com', 'net', 'org', 'biz']:
            domain = f"{pattern}.{tld}"
            result = verifier.verify_domain(domain)
            if result['verified']:
                return result

    # No verification succeeded
    return {
        'verified': False,
        'domain': None,
        'error': f"Could not verify domain for {company_name}"
    }


if __name__ == '__main__':
    # Test the verifier
    verifier = DomainVerifier()

    test_domains = [
        'google.com',
        'westsidetransmission.com',
        'fakefakefake999.com',
        'cossatotriver.com',
        'doesnotexist-at-all.com'
    ]

    print("Domain Verification Test")
    print("=" * 80)

    for domain in test_domains:
        result = verifier.verify_domain(domain)
        status = "✓ VERIFIED" if result['verified'] else "✗ FAILED"
        print(f"\n{domain:40} | {status}")
        if result['verified']:
            print(f"  DNS: {result['dns_ip']}")
            print(f"  HTTP: {result['http_status']}")
            print(f"  Server: {result['server']}")
        else:
            print(f"  Error: {result['error']}")
