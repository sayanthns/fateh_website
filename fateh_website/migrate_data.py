"""
One-time migration script to import existing JSON data into Frappe Doctypes.

Usage:
  cd frappe-bench
  bench --site your-site.local console
  >>> from fateh_website.migrate_data import migrate_all
  >>> migrate_all("/path/to/Fateh-website-claude-frappe")
"""
import json
import os

import frappe


def migrate_all(project_root):
    """Run all migrations from the old JSON files."""
    print("Starting data migration...")
    migrate_testimonials(os.path.join(project_root, "testimonials.json"))
    migrate_pricing(os.path.join(project_root, "pricing.json"))
    migrate_leads(os.path.join(project_root, "leads.json"))
    migrate_settings(os.path.join(project_root, "settings.json"))
    print("Migration complete!")


def migrate_testimonials(filepath):
    """Import testimonials from testimonials.json."""
    if not os.path.exists(filepath):
        print(f"  Skipping testimonials: {filepath} not found")
        return

    with open(filepath) as f:
        testimonials = json.load(f)

    print(f"  Migrating {len(testimonials)} testimonials...")
    for i, t in enumerate(testimonials):
        doc = frappe.get_doc({
            "doctype": "Website Testimonial",
            "person_name": t.get("name", ""),
            "person_name_ar": t.get("name_ar", ""),
            "role": t.get("role", ""),
            "role_ar": t.get("role_ar", ""),
            "company": t.get("company", ""),
            "company_ar": t.get("company_ar", ""),
            "quote": t.get("quote", ""),
            "quote_ar": t.get("quote_ar", ""),
            "rating": t.get("rating", 5),
            "display_order": i,
        })
        doc.insert(ignore_permissions=True)

    frappe.db.commit()
    print(f"  Done: {len(testimonials)} testimonials imported.")


def migrate_pricing(filepath):
    """Import pricing plans and comparison categories from pricing.json."""
    if not os.path.exists(filepath):
        print(f"  Skipping pricing: {filepath} not found")
        return

    with open(filepath) as f:
        pricing = json.load(f)

    # Migrate plans
    plans = pricing.get("plans", [])
    print(f"  Migrating {len(plans)} pricing plans...")
    for i, plan in enumerate(plans):
        features = []
        features_en = plan.get("features", [])
        features_ar = plan.get("features_ar", [])

        for j, feat_en in enumerate(features_en):
            feat_ar = features_ar[j] if j < len(features_ar) else ""
            features.append({
                "feature": feat_en,
                "feature_ar": feat_ar,
            })

        doc = frappe.get_doc({
            "doctype": "Website Pricing Plan",
            "plan_name": plan.get("name", ""),
            "plan_name_ar": plan.get("name_ar", ""),
            "price": plan.get("price", ""),
            "price_ar": plan.get("price_ar", ""),
            "period": plan.get("period", ""),
            "period_ar": plan.get("period_ar", ""),
            "description": plan.get("description", ""),
            "description_ar": plan.get("description_ar", ""),
            "is_popular": 1 if plan.get("popular") else 0,
            "cta_text": plan.get("cta", "Get Started"),
            "cta_text_ar": plan.get("cta_ar", ""),
            "display_order": i,
            "features": features,
        })
        doc.insert(ignore_permissions=True)

    # Migrate comparison categories
    categories = pricing.get("comparisonCategories", [])
    order = 0
    for cat in categories:
        cat_name = cat.get("name", "")
        cat_name_ar = cat.get("name_ar", "")
        for feat in cat.get("features", []):
            doc = frappe.get_doc({
                "doctype": "Website Pricing Comparison",
                "category_name": cat_name,
                "category_name_ar": cat_name_ar,
                "feature_name": feat.get("name", ""),
                "feature_name_ar": feat.get("name_ar", ""),
                "in_starter": 1 if feat.get("starter") else 0,
                "in_professional": 1 if feat.get("professional") else 0,
                "in_enterprise": 1 if feat.get("enterprise") else 0,
                "display_order": order,
            })
            doc.insert(ignore_permissions=True)
            order += 1

    frappe.db.commit()
    print(f"  Done: {len(plans)} plans, {order} comparison features imported.")


def migrate_leads(filepath):
    """Import existing leads from leads.json."""
    if not os.path.exists(filepath):
        print(f"  Skipping leads: {filepath} not found")
        return

    with open(filepath) as f:
        leads = json.load(f)

    # Filter out trashed leads
    active_leads = [l for l in leads if l.get("status") != "Trash"]
    print(f"  Migrating {len(active_leads)} leads (skipping trashed)...")

    for lead in active_leads:
        doc = frappe.get_doc({
            "doctype": "Website Lead",
            "lead_name": lead.get("name", "Unknown"),
            "business_name": lead.get("businessName", ""),
            "phone_number": lead.get("phoneNumber", ""),
            "location": lead.get("location", ""),
            "source": lead.get("source", "Website Form"),
            "status": lead.get("status", "New"),
            "comment": lead.get("comment", ""),
        })
        doc.insert(ignore_permissions=True)

    frappe.db.commit()
    print(f"  Done: {len(active_leads)} leads imported.")


def migrate_settings(filepath):
    """Import settings from settings.json."""
    if not os.path.exists(filepath):
        print(f"  Skipping settings: {filepath} not found")
        return

    with open(filepath) as f:
        settings = json.load(f)

    doc = frappe.get_single("Fateh Website Settings")
    doc.calendly_url = settings.get("calendlyUrl", "")
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    print("  Done: Settings imported.")
