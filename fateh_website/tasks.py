import frappe
from frappe.utils import add_days, now_datetime


def purge_trashed_leads():
    """Auto-purge leads in Trash status older than 30 days."""
    cutoff = add_days(now_datetime(), -30)
    leads = frappe.get_all(
        "Website Lead",
        filters={"status": "Trash", "modified": ["<", cutoff]},
        pluck="name",
    )
    for lead in leads:
        frappe.delete_doc("Website Lead", lead, ignore_permissions=True)
    if leads:
        frappe.db.commit()


def sync_ga4_analytics():
    """Pull yesterday's GA4 analytics for both sites."""
    from fateh_website.ga4 import sync_site

    sites = [
        ("Fateh", "Fateh Website Settings"),
        ("Enfono", "Enfono Website Settings"),
    ]

    for site_label, settings_doctype in sites:
        try:
            sync_site(site_label, settings_doctype)
        except Exception:
            frappe.log_error(
                f"GA4 sync failed for {site_label}",
                "GA4 Sync Error",
            )
