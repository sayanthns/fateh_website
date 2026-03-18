import json
import os
import frappe


def after_install():
    """Import fixture data after app installation."""
    fixtures_dir = os.path.join(os.path.dirname(__file__), "fixtures")
    if not os.path.exists(fixtures_dir):
        return

    fixture_files = [
        "fateh_website_settings.json",
        "website_testimonial.json",
        "website_pricing_plan.json",
        "website_pricing_comparison.json",
    ]

    for filename in fixture_files:
        filepath = os.path.join(fixtures_dir, filename)
        if not os.path.exists(filepath):
            continue

        with open(filepath) as f:
            data = json.load(f)

        for doc_data in data:
            doctype = doc_data.get("doctype")
            if not doctype:
                continue

            # For Single doctypes (like Settings), update the existing doc
            meta = frappe.get_meta(doctype)
            if meta.issingle:
                doc = frappe.get_single(doctype)
                for key, val in doc_data.items():
                    if key != "doctype" and hasattr(doc, key):
                        setattr(doc, key, val)
                doc.save(ignore_permissions=True)
                continue

            # For regular doctypes, check for duplicates by key fields
            doc = frappe.get_doc(doc_data)
            doc.insert(ignore_permissions=True, ignore_if_duplicate=True)

        frappe.db.commit()
        print(f"  Imported {filename}")
