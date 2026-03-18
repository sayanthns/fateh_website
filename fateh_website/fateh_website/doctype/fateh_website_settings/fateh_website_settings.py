import frappe
from frappe.model.document import Document


class FatehWebsiteSettings(Document):
    @frappe.whitelist()
    def sync_ga4_now(self):
        """Manually trigger GA4 sync for Fateh site."""
        from fateh_website.ga4 import sync_site
        sync_site("Fateh", "Fateh Website Settings")
        frappe.msgprint("GA4 data synced for Fateh (yesterday).")
