#!/usr/bin/env python3
"""
Enhanced OSINT Information Gathering
Uses all available Kali Linux tools and OSINT methods to gather company information
"""

import subprocess
import json
import socket
import sys
import os
from urllib.parse import urlparse
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class KaliToolGatherer:
    """Gathers company info using all available Kali tools"""

    @staticmethod
    def whois_lookup(domain: str) -> dict:
        """WHOIS information - registrant details, registrar, nameservers"""
        logger.info(f"  Running WHOIS lookup for {domain}")
        try:
            result = subprocess.run(['whois', domain], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                whois_data = {
                    "registrant": None,
                    "registrar": None,
                    "nameservers": [],
                    "creation_date": None,
                    "expiration_date": None,
                }
                for line in lines:
                    if 'Registrant' in line or 'Registrant Name' in line:
                        whois_data["registrant"] = line.split(':', 1)[-1].strip()
                    if 'Registrar' in line:
                        whois_data["registrar"] = line.split(':', 1)[-1].strip()
                    if 'Name Server' in line:
                        ns = line.split(':', 1)[-1].strip()
                        if ns and ns not in whois_data["nameservers"]:
                            whois_data["nameservers"].append(ns)
                    if 'Creation Date' in line:
                        whois_data["creation_date"] = line.split(':', 1)[-1].strip()
                    if 'Expiration' in line:
                        whois_data["expiration_date"] = line.split(':', 1)[-1].strip()

                if any([whois_data["registrant"], whois_data["registrar"], whois_data["nameservers"]]):
                    logger.info(f"    ✓ Found WHOIS data")
                    return whois_data
        except Exception as e:
            logger.debug(f"WHOIS error: {e}")
        return {}

    @staticmethod
    def dns_enumeration(domain: str) -> dict:
        """DNS enumeration - A, AAAA, MX, TXT, NS records"""
        logger.info(f"  Running DNS enumeration for {domain}")
        dns_data = {
            "a_records": [],
            "aaaa_records": [],
            "mx_records": [],
            "txt_records": [],
            "ns_records": [],
            "cname_records": [],
        }

        # A Records
        try:
            result = subprocess.run(['dig', domain, '+short'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line and not line.startswith(';'):
                        dns_data["a_records"].append(line.strip())
        except:
            pass

        # MX Records
        try:
            result = subprocess.run(['dig', domain, 'MX', '+short'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line and not line.startswith(';'):
                        dns_data["mx_records"].append(line.strip())
        except:
            pass

        # TXT Records
        try:
            result = subprocess.run(['dig', domain, 'TXT', '+short'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line and not line.startswith(';'):
                        dns_data["txt_records"].append(line.strip())
        except:
            pass

        # NS Records
        try:
            result = subprocess.run(['dig', domain, 'NS', '+short'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line and not line.startswith(';'):
                        dns_data["ns_records"].append(line.strip())
        except:
            pass

        if any([dns_data["a_records"], dns_data["mx_records"], dns_data["txt_records"], dns_data["ns_records"]]):
            logger.info(f"    ✓ Found DNS records")
            return dns_data
        return {}

    @staticmethod
    def reverse_dns(ip: str) -> dict:
        """Reverse DNS lookup - what domain(s) resolve to this IP"""
        logger.info(f"  Running reverse DNS for {ip}")
        try:
            hostname = socket.gethostbyaddr(ip)
            logger.info(f"    ✓ Found reverse DNS")
            return {"hostname": hostname[0], "aliases": hostname[1]}
        except:
            return {}

    @staticmethod
    def nmap_scan(domain: str) -> dict:
        """Port scanning - find open ports and services"""
        logger.info(f"  Running nmap scan for {domain}")
        nmap_data = {
            "open_ports": [],
            "services": [],
            "os_detection": None,
        }

        try:
            # Quick scan of common ports
            result = subprocess.run(
                ['nmap', '-p', '80,443,22,21,25,3306,5432', '-sV', '--script', 'banner', domain],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'open' in line.lower():
                        nmap_data["open_ports"].append(line.strip())
                    if 'Version' in line or 'Product' in line:
                        nmap_data["services"].append(line.strip())

                if nmap_data["open_ports"]:
                    logger.info(f"    ✓ Found open ports: {len(nmap_data['open_ports'])}")
                    return nmap_data
        except subprocess.TimeoutExpired:
            logger.debug("Nmap scan timed out")
        except Exception as e:
            logger.debug(f"Nmap error: {e}")

        return {}

    @staticmethod
    def web_header_analysis(url: str) -> dict:
        """Analyze HTTP headers - server info, technologies, security headers"""
        logger.info(f"  Analyzing HTTP headers for {url}")
        header_data = {
            "server": None,
            "powered_by": None,
            "x_powered_by": None,
            "technologies": [],
            "security_headers": {},
        }

        try:
            result = subprocess.run(['curl', '-I', '-A', 'Mozilla/5.0', url], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    line_lower = line.lower()
                    if line.startswith('Server:'):
                        header_data["server"] = line.split(':', 1)[-1].strip()
                    if 'x-powered-by' in line_lower:
                        header_data["x_powered_by"] = line.split(':', 1)[-1].strip()
                    if 'powered-by' in line_lower:
                        header_data["powered_by"] = line.split(':', 1)[-1].strip()
                    if any(sec in line_lower for sec in ['strict-transport', 'content-security', 'x-frame-options']):
                        key = line.split(':', 1)[0].strip()
                        val = line.split(':', 1)[-1].strip()
                        header_data["security_headers"][key] = val

                if header_data["server"] or header_data["powered_by"]:
                    logger.info(f"    ✓ Found server info: {header_data['server']}")
                    return header_data
        except Exception as e:
            logger.debug(f"Header analysis error: {e}")

        return {}

    @staticmethod
    def nikto_scan(url: str) -> dict:
        """Nikto web vulnerability scanning"""
        logger.info(f"  Running Nikto scan for {url}")
        nikto_data = {
            "vulnerabilities": [],
            "interesting_files": [],
            "server_info": None,
        }

        try:
            result = subprocess.run(
                ['nikto', '-h', url, '-o', '/tmp/nikto_output.txt'],
                capture_output=True,
                text=True,
                timeout=30
            )

            # Read output file
            try:
                with open('/tmp/nikto_output.txt', 'r') as f:
                    for line in f:
                        if '+ OSVDB' in line or '+ Server' in line or '+ /admin' in line:
                            nikto_data["vulnerabilities"].append(line.strip())

                if nikto_data["vulnerabilities"]:
                    logger.info(f"    ✓ Found Nikto results")
                    return nikto_data
            except:
                pass
        except subprocess.TimeoutExpired:
            logger.debug("Nikto scan timed out")
        except Exception as e:
            logger.debug(f"Nikto error: {e}")

        return {}

    @staticmethod
    def shodan_query(query: str) -> dict:
        """Query Shodan for device/service information"""
        logger.info(f"  Querying Shodan for {query}")

        try:
            import shodan
            # Note: Requires SHODAN_API_KEY env var
            api_key = os.environ.get('SHODAN_API_KEY')
            if not api_key:
                logger.debug("SHODAN_API_KEY not set")
                return {}

            api = shodan.Shodan(api_key)
            results = api.search(query)

            if results['matches']:
                logger.info(f"    ✓ Found {len(results['matches'])} Shodan results")
                return {
                    "total": results['total'],
                    "matches": results['matches'][:5],  # Top 5 results
                }
        except Exception as e:
            logger.debug(f"Shodan error: {e}")

        return {}

    @staticmethod
    def dnsrecon_scan(domain: str) -> dict:
        """DNSRecon - comprehensive DNS enumeration"""
        logger.info(f"  Running dnsrecon for {domain}")
        dnsrecon_data = {
            "hosts": [],
            "zones": [],
            "records": [],
        }

        try:
            result = subprocess.run(
                ['dnsrecon', '-d', domain, '-t', 'std'],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if '[A]' in line or '[MX]' in line or '[NS]' in line:
                        dnsrecon_data["records"].append(line.strip())

                if dnsrecon_data["records"]:
                    logger.info(f"    ✓ Found dnsrecon data")
                    return dnsrecon_data
        except Exception as e:
            logger.debug(f"dnsrecon error: {e}")

        return {}

    @staticmethod
    def fierce_scan(domain: str) -> dict:
        """Fierce DNS enumeration - find subdomains"""
        logger.info(f"  Running fierce for {domain}")
        fierce_data = {
            "subdomains": [],
            "ips": [],
        }

        try:
            result = subprocess.run(
                ['fierce', '--domain', domain],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if line.strip() and '.' in line:
                        fierce_data["subdomains"].append(line.strip())

                if fierce_data["subdomains"]:
                    logger.info(f"    ✓ Found {len(fierce_data['subdomains'])} subdomains")
                    return fierce_data
        except Exception as e:
            logger.debug(f"Fierce error: {e}")

        return {}


def gather_all_osint(domain: str, url: str = None) -> dict:
    """Gather all available OSINT data on a domain"""

    if url is None:
        url = f"https://{domain}"

    if not domain.startswith('http'):
        domain_only = domain.replace('www.', '')
    else:
        parsed = urlparse(domain)
        domain_only = parsed.netloc.replace('www.', '')

    logger.info(f"\n{'='*70}")
    logger.info(f"Gathering OSINT for: {domain_only}")
    logger.info(f"{'='*70}\n")

    osint_data = {
        "domain": domain_only,
        "url": url,
        "whois": {},
        "dns": {},
        "dns_reverse": {},
        "nmap": {},
        "headers": {},
        "nikto": {},
        "dnsrecon": {},
        "fierce": {},
        "shodan": {},
    }

    gatherer = KaliToolGatherer()

    # Extract IP if possible
    try:
        ip = socket.gethostbyname(domain_only)
        logger.info(f"  Resolved to IP: {ip}")
        osint_data["ip"] = ip
        osint_data["dns_reverse"] = gatherer.reverse_dns(ip)
    except:
        pass

    # Run all tools
    osint_data["whois"] = gatherer.whois_lookup(domain_only)
    osint_data["dns"] = gatherer.dns_enumeration(domain_only)
    osint_data["nmap"] = gatherer.nmap_scan(domain_only)
    osint_data["headers"] = gatherer.web_header_analysis(url)
    osint_data["nikto"] = gatherer.nikto_scan(url)
    osint_data["dnsrecon"] = gatherer.dnsrecon_scan(domain_only)
    osint_data["fierce"] = gatherer.fierce_scan(domain_only)

    # Count results
    total_data = sum(1 for v in osint_data.values() if v and isinstance(v, dict) and len(v) > 0)

    logger.info(f"\n{'='*70}")
    logger.info(f"OSINT Gathering Complete - {total_data} data sources found")
    logger.info(f"{'='*70}\n")

    return osint_data


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 enhanced_osint_gathering.py <domain> [url]")
        print("Example: python3 enhanced_osint_gathering.py example.com https://example.com")
        sys.exit(1)

    domain = sys.argv[1]
    url = sys.argv[2] if len(sys.argv) > 2 else None

    osint_results = gather_all_osint(domain, url)

    # Pretty print results
    print(json.dumps(osint_results, indent=2))
