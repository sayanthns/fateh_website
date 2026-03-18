import frappe
from frappe.model.document import Document


class EnfonoWebsiteSettings(Document):
    @frappe.whitelist()
    def sync_ga4_now(self):
        """Manually trigger GA4 sync for Enfono site."""
        from fateh_website.ga4 import sync_site
        sync_site("Enfono", "Enfono Website Settings")
        frappe.msgprint("GA4 data synced for Enfono (yesterday).")
