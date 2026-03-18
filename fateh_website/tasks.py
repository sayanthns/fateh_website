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
