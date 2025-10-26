#!/usr/bin/env python3
"""
Enhanced Tech Stack Detection
Detects server software, CMS versions, outdated packages, and vulnerabilities
Outputs sales-relevant technical intelligence
"""

import json
import subprocess
import re
from typing import Dict, Any
import requests
from datetime import datetime

class TechStackDetector:
    """Detect tech stack and extract sales-relevant vulnerabilities"""

    @staticmethod
    def detect_server_info(url: str) -> Dict[str, Any]:
        """Detect server type and version from HTTP headers"""
        result = {
            "server": None,
            "version": None,
            "outdated": False,
            "framework": None,
            "powered_by": None,
            "security_headers": {}
        }

        try:
            response = requests.head(url, timeout=5, allow_redirects=True)
            headers = response.headers

            # Server detection
            if 'Server' in headers:
                result["server"] = headers['Server']
                # Check if Apache or Nginx versions suggest outdated
                if 'Apache' in headers['Server']:
                    version_match = re.search(r'Apache/(\d+\.\d+)', headers['Server'])
                    if version_match:
                        version = version_match.group(1)
                        result["version"] = version
                        # Apache 2.2 is very outdated
                        if version.startswith('2.2'):
                            result["outdated"] = True

            # X-Powered-By detection
            if 'X-Powered-By' in headers:
                result["powered_by"] = headers['X-Powered-By']
                if 'PHP' in headers['X-Powered-By']:
                    result["framework"] = "PHP"

            # Security headers
            security_header_names = [
                'Strict-Transport-Security',
                'Content-Security-Policy',
                'X-Content-Type-Options',
                'X-Frame-Options',
                'X-XSS-Protection'
            ]

            for header in security_header_names:
                if header in headers:
                    result["security_headers"][header] = headers[header]

            return result

        except Exception as e:
            return result

    @staticmethod
    def detect_wordpress(url: str) -> Dict[str, Any]:
        """Detect WordPress and run WPScan"""
        result = {
            "is_wordpress": False,
            "version": None,
            "plugins": [],
            "vulnerable_plugins": [],
            "themes": [],
            "vulnerabilities": 0,
            "outdated_core": False
        }

        try:
            # Quick check for WordPress indicators
            response = requests.get(url, timeout=5)
            content = response.text.lower()

            wp_indicators = [
                'wp-content',
                'wp-includes',
                '/wp-json/',
                'wordpress',
                '<meta name="generator" content="wordpress'
            ]

            if not any(indicator in content for indicator in wp_indicators):
                return result

            result["is_wordpress"] = True

            # Try to detect version from common locations
            try:
                wp_response = requests.get(f"{url}/wp-includes/version.php", timeout=5)
                version_match = re.search(r"\$wp_version\s*=\s*['\"]([^'\"]+)['\"]", wp_response.text)
                if version_match:
                    result["version"] = version_match.group(1)
            except:
                pass

            # Run WPScan if WordPress detected
            try:
                wpscan_cmd = [
                    'wpscan',
                    '--url', url,
                    '--enumerate', 'vp,ap',
                    '--plugins-detection', 'aggressive',
                    '--format', 'json',
                    '--no-banner',
                    '--disable-tls-checks'
                ]

                wpscan_result = subprocess.run(
                    wpscan_cmd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if wpscan_result.returncode == 0:
                    try:
                        wpscan_json = json.loads(wpscan_result.stdout)

                        # Extract vulnerable plugins
                        if 'plugins' in wpscan_json:
                            for plugin_name, plugin_data in wpscan_json['plugins'].items():
                                if 'vulnerabilities' in plugin_data and plugin_data['vulnerabilities']:
                                    result["vulnerable_plugins"].append({
                                        "name": plugin_name,
                                        "version": plugin_data.get('version', 'Unknown'),
                                        "vulnerabilities": len(plugin_data['vulnerabilities'])
                                    })
                                result["plugins"].append(plugin_name)

                        # Check for outdated WordPress core
                        if 'version' in wpscan_json:
                            wp_version = wpscan_json['version'].get('number')
                            if wp_version:
                                result["version"] = wp_version
                                # Versions older than 5.0 are quite outdated
                                major_version = int(wp_version.split('.')[0])
                                if major_version < 5:
                                    result["outdated_core"] = True

                        result["vulnerabilities"] = len(result["vulnerable_plugins"])

                    except json.JSONDecodeError:
                        pass

            except subprocess.TimeoutExpired:
                pass
            except Exception as e:
                pass

            return result

        except Exception as e:
            return result

    @staticmethod
    def detect_other_cms(url: str) -> Dict[str, Any]:
        """Detect Drupal, Joomla, Magento, etc."""
        result = {
            "cms_type": None,
            "version": None,
            "outdated": False
        }

        try:
            response = requests.get(url, timeout=5)
            content = response.text.lower()

            # Drupal detection
            if 'drupal' in content or 'sites/all/modules' in content:
                result["cms_type"] = "Drupal"
                # Try to find version
                version_match = re.search(r'drupal\s+(\d+\.\d+)', content)
                if version_match:
                    result["version"] = version_match.group(1)

            # Joomla detection
            elif 'joomla' in content or 'administrator/index.php' in content:
                result["cms_type"] = "Joomla"

            # Magento detection
            elif 'magento' in content or 'var/log/system.log' in content:
                result["cms_type"] = "Magento"

            return result

        except Exception as e:
            return result

    @staticmethod
    def analyze_tech_stack(url: str) -> Dict[str, Any]:
        """Comprehensive tech stack analysis"""
        return {
            "server": TechStackDetector.detect_server_info(url),
            "wordpress": TechStackDetector.detect_wordpress(url),
            "other_cms": TechStackDetector.detect_other_cms(url),
            "scan_timestamp": datetime.now().isoformat()
        }

    @staticmethod
    def extract_sales_signals(tech_stack: Dict[str, Any]) -> Dict[str, Any]:
        """Extract sales-relevant signals from tech stack"""
        signals = {
            "has_outdated_server": False,
            "has_outdated_cms": False,
            "has_vulnerable_plugins": False,
            "has_poor_security": False,
            "opportunity_score": 0,
            "pain_points": []
        }

        # Server signals
        if tech_stack.get('server', {}).get('outdated'):
            signals["has_outdated_server"] = True
            signals["pain_points"].append("Outdated server software - security risk")
            signals["opportunity_score"] += 15

        # WordPress signals
        wp_data = tech_stack.get('wordpress', {})
        if wp_data.get('is_wordpress'):
            if wp_data.get('outdated_core'):
                signals["has_outdated_cms"] = True
                signals["pain_points"].append(f"Outdated WordPress {wp_data.get('version')} - needs upgrade")
                signals["opportunity_score"] += 20

            if wp_data.get('vulnerable_plugins'):
                signals["has_vulnerable_plugins"] = True
                count = len(wp_data['vulnerable_plugins'])
                signals["pain_points"].append(f"{count} vulnerable plugins detected")
                signals["opportunity_score"] += 25

        # Security posture
        security_headers = tech_stack.get('server', {}).get('security_headers', {})
        if not security_headers or len(security_headers) < 3:
            signals["has_poor_security"] = True
            signals["pain_points"].append("Missing critical security headers")
            signals["opportunity_score"] += 10

        return signals
