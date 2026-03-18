"""
Google Analytics GA4 Data API integration.

Uses raw REST calls with google-auth for lightweight dependency footprint.
"""
import json
import frappe
import requests
from datetime import date, timedelta

GA4_API_BASE = "https://analyticsdata.googleapis.com/v1beta"


def clean_json_string(raw):
    """Clean up JSON from Frappe Password field (may strip braces or add NBSP)."""
    cleaned = raw.replace('\xa0', ' ').strip()
    if not cleaned.startswith('{'):
        cleaned = '{' + cleaned
    if not cleaned.endswith('}'):
        cleaned = cleaned + '}'
    return cleaned


def get_credentials(service_account_json_str):
    """Create google-auth credentials from a service account JSON string."""
    from google.oauth2 import service_account
    import google.auth.transport.requests

    cleaned = clean_json_string(service_account_json_str)
    info = json.loads(cleaned)
    creds = service_account.Credentials.from_service_account_info(
        info, scopes=["https://www.googleapis.com/auth/analytics.readonly"]
    )
    creds.refresh(google.auth.transport.requests.Request())
    return creds


def fetch_report(credentials, property_id, date_str, metrics, dimensions=None, limit=10):
    """
    Call the GA4 Data API runReport endpoint.

    Args:
        credentials: google-auth Credentials with a valid token
        property_id: Numeric GA4 property ID (e.g. "123456789")
        date_str: Date string like "2026-03-18" or "yesterday"
        metrics: List of metric names (e.g. ["sessions", "screenPageViews"])
        dimensions: Optional list of dimension names (e.g. ["pagePath"])
        limit: Max rows for dimensional queries
    Returns:
        Parsed JSON response dict
    """
    url = f"{GA4_API_BASE}/properties/{property_id}:runReport"
    body = {
        "dateRanges": [{"startDate": date_str, "endDate": date_str}],
        "metrics": [{"name": m} for m in metrics],
    }
    if dimensions:
        body["dimensions"] = [{"name": d} for d in dimensions]
        body["limit"] = limit
        body["orderBys"] = [
            {"metric": {"metricName": metrics[0]}, "desc": True}
        ]

    resp = requests.post(
        url,
        json=body,
        headers={
            "Authorization": f"Bearer {credentials.token}",
            "Content-Type": "application/json",
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def parse_aggregate_metrics(report):
    """Extract aggregate metrics from a GA4 report response (no dimensions)."""
    rows = report.get("rows", [])
    if not rows:
        return {}
    values = rows[0].get("metricValues", [])
    headers = [h["name"] for h in report.get("metricHeaders", [])]
    return {headers[i]: values[i]["value"] for i in range(len(headers))}


def parse_dimensional_report(report, dim_key="dimension", metric_key="value"):
    """Extract dimension + metric pairs from a GA4 report response."""
    results = []
    rows = report.get("rows", [])
    for row in rows:
        dim_val = row["dimensionValues"][0]["value"]
        metric_val = row["metricValues"][0]["value"]
        results.append({dim_key: dim_val, metric_key: metric_val})
    return results


def sync_site(site_label, settings_doctype):
    """
    Fetch yesterday's GA4 data for a site and store in GA4 Analytics Data.

    Args:
        site_label: "Fateh" or "Enfono"
        settings_doctype: "Fateh Website Settings" or "Enfono Website Settings"
    """
    settings = frappe.get_single(settings_doctype)

    if not settings.ga4_enabled:
        return

    property_id = settings.ga4_property_id
    sa_json = settings.get_password("ga4_service_account_json")

    if not property_id or not sa_json:
        frappe.log_error(
            f"GA4 sync skipped for {site_label}: missing property ID or service account JSON",
            "GA4 Sync",
        )
        return

    yesterday = (date.today() - timedelta(days=1)).isoformat()

    # Get credentials
    creds = get_credentials(sa_json)

    # Fetch aggregate metrics
    agg = fetch_report(
        creds,
        property_id,
        yesterday,
        ["sessions", "screenPageViews", "totalUsers", "bounceRate", "averageSessionDuration"],
    )
    metrics = parse_aggregate_metrics(agg)

    # Fetch top pages
    pages_report = fetch_report(
        creds, property_id, yesterday,
        ["screenPageViews"], dimensions=["pagePath"], limit=10,
    )
    top_pages = parse_dimensional_report(pages_report, "page", "views")

    # Fetch top sources
    sources_report = fetch_report(
        creds, property_id, yesterday,
        ["sessions"], dimensions=["sessionSource"], limit=10,
    )
    top_sources = parse_dimensional_report(sources_report, "source", "sessions")

    # Create or update the record
    doc_name = f"{site_label}-{yesterday}"
    if frappe.db.exists("GA4 Analytics Data", doc_name):
        doc = frappe.get_doc("GA4 Analytics Data", doc_name)
    else:
        doc = frappe.new_doc("GA4 Analytics Data")
        doc.site = site_label
        doc.date = yesterday

    doc.ga4_property_id = property_id
    doc.sessions = int(metrics.get("sessions", 0))
    doc.page_views = int(metrics.get("screenPageViews", 0))
    doc.users = int(metrics.get("totalUsers", 0))
    doc.bounce_rate = float(metrics.get("bounceRate", 0)) * 100
    doc.avg_session_duration = float(metrics.get("averageSessionDuration", 0))
    doc.top_pages = json.dumps(top_pages)
    doc.top_sources = json.dumps(top_sources)

    doc.save(ignore_permissions=True)
    frappe.db.commit()
