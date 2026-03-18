import frappe
from frappe.model.document import Document


class EnfonoCaseStudy(Document):
    pass


@frappe.whitelist()
def get_category_options():
    """Return category options from Enfono Website Settings child table."""
    settings = frappe.get_single("Enfono Website Settings")
    categories = [row.category_name for row in (settings.our_work_categories or []) if row.category_name]
    return categories
