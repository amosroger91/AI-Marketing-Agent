#!/usr/bin/env python3
"""
Sales Viability Filter
Uses LLM to assess if a company is a good fit for outreach
Filters out massive corporations, chains, and companies that would hire full-time devs
"""

import subprocess
import json
from typing import Dict, Any, Tuple

class SalesViabilityFilter:
    """Filter companies by sales viability using LLM"""

    # List of obvious non-targets
    EXCLUDE_KEYWORDS = [
        'verizon', 'at&t', 'tmobile', 't-mobile',
        'google', 'amazon', 'microsoft', 'apple', 'facebook', 'meta',
        'dell', 'hp', 'lenovo', 'cisco', 'ibm',
        'fortune 500', 'multinational', 'nasdaq', 'nyse',
        'bank', 'bank of', 'capital one', 'chase', 'wells fargo',
        'mcdonalds', 'walmart', 'target', 'costco', 'target',
        'federal', 'government', 'military', 'defense',
        'tesla', 'uber', 'lyft', 'airbnb'
    ]

    @staticmethod
    def assess_sales_fit(
        company_name: str,
        location: str,
        domain: str,
        osint_findings: int,
        tech_stack: Dict[str, Any],
        sales_signals: Dict[str, Any]
    ) -> Tuple[int, str, list]:
        """
        Assess if company is a good sales target
        Returns: (score 0-100, recommendation, reasons)
        """

        # Quick keyword filter
        company_lower = company_name.lower()
        for keyword in SalesViabilityFilter.EXCLUDE_KEYWORDS:
            if keyword in company_lower:
                return 0, "EXCLUDE", [f"Matches exclusion keyword: {keyword}"]

        # Build context for LLM
        context = f"""
Company: {company_name}
Location: {location}
Domain: {domain}
OSINT Findings: {osint_findings} data points
Tech Stack: {json.dumps(tech_stack, indent=2)}
Sales Signals: {json.dumps(sales_signals, indent=2)}

Assess if this is a good fit for n8n/automation consulting outreach.
Consider:
1. Company size (small/local = good, enterprise = bad)
2. Whether they're likely to hire full-time devs vs contractors
3. Tech debt indicators (outdated tech = opportunity)
4. Budget indicators (small business = likely to need cost-effective solutions)
5. Location (local = good, national chains = bad)
6. OSINT findings (more data = more credible company)

Return JSON with:
{{
  "score": 0-100,
  "recommendation": "CONTACT" or "EXCLUDE",
  "reasons": ["reason1", "reason2", ...],
  "company_size_estimate": "small/medium/large/enterprise",
  "hiring_pattern": "likely to hire contractors/likely to hire full-time/unknown",
  "opportunity_level": "high/medium/low"
}}
"""

        try:
            # Use Gemini to assess fit
            result = subprocess.run(
                ['gemini'],
                input=context,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                try:
                    # Extract JSON from response
                    response_text = result.stdout
                    # Find JSON in response
                    json_start = response_text.find('{')
                    json_end = response_text.rfind('}') + 1
                    if json_start >= 0 and json_end > json_start:
                        json_str = response_text[json_start:json_end]
                        assessment = json.loads(json_str)

                        score = assessment.get('score', 0)
                        recommendation = assessment.get('recommendation', 'EXCLUDE')
                        reasons = assessment.get('reasons', [])

                        return score, recommendation, reasons

                except (json.JSONDecodeError, ValueError):
                    pass

        except Exception as e:
            pass

        # Fallback heuristic-based scoring if LLM fails
        return SalesViabilityFilter._heuristic_score(
            company_name, location, domain, osint_findings,
            tech_stack, sales_signals
        )

    @staticmethod
    def _heuristic_score(
        company_name: str,
        location: str,
        domain: str,
        osint_findings: int,
        tech_stack: Dict[str, Any],
        sales_signals: Dict[str, Any]
    ) -> Tuple[int, str, list]:
        """Fallback heuristic scoring"""
        score = 50  # Start at neutral
        reasons = []
        recommendation = "EXCLUDE"

        # Location scoring
        if location and location.lower() not in ['online', 'unknown']:
            score += 10
            reasons.append(f"Local company: {location}")
        else:
            score -= 20
            reasons.append("No clear local presence")

        # OSINT findings
        if osint_findings > 0:
            score += min(20, osint_findings)  # More data = more confidence
            reasons.append(f"Good OSINT data: {osint_findings} findings")
        else:
            score -= 15
            reasons.append("Minimal OSINT data found")

        # Tech stack indicators
        wp_data = tech_stack.get('wordpress', {})
        if wp_data.get('is_wordpress'):
            score += 15
            reasons.append("Uses WordPress - common platform")

            if wp_data.get('vulnerable_plugins'):
                score += 20
                reasons.append(f"{len(wp_data['vulnerable_plugins'])} vulnerable plugins")

            if wp_data.get('outdated_core'):
                score += 15
                reasons.append("Outdated WordPress - needs attention")

        # Security signals
        if sales_signals.get('has_poor_security'):
            score += 10
            reasons.append("Poor security posture - opportunity")

        if sales_signals.get('has_outdated_server'):
            score += 5
            reasons.append("Outdated server software")

        # Opportunity score from signals
        score += sales_signals.get('opportunity_score', 0)

        # Final recommendation
        if score >= 70:
            recommendation = "CONTACT"
        elif score >= 50:
            recommendation = "MAYBE"
        else:
            recommendation = "EXCLUDE"

        return score, recommendation, reasons
