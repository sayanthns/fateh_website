import frappe


@frappe.whitelist(allow_guest=True)
def submit_lead(lead_name, business_name, phone_number, location, source="Website Form", email=None, ad_source=None, ad_campaign=None):
    """Submit a new website lead (public endpoint)."""
    doc = frappe.get_doc({
        "doctype": "Website Lead",
        "lead_name": lead_name,
        "business_name": business_name,
        "phone_number": phone_number,
        "location": location,
        "source": source,
        "email": email or "",
        "ad_source": ad_source or "",
        "ad_campaign": ad_campaign or "",
        "status": "New",
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    return {"success": True, "message": "Lead saved successfully"}


@frappe.whitelist(allow_guest=True)
def get_testimonials():
    """Retrieve all published testimonials (public endpoint)."""
    testimonials = frappe.get_all(
        "Website Testimonial",
        fields=[
            "name as id",
            "person_name as name",
            "person_name_ar as name_ar",
            "role",
            "role_ar",
            "company",
            "company_ar",
            "quote",
            "quote_ar",
            "rating",
        ],
        order_by="display_order asc",
        ignore_permissions=True,
    )
    return {"success": True, "testimonials": testimonials}


@frappe.whitelist(allow_guest=True)
def get_pricing():
    """Retrieve pricing plans and comparison table (public endpoint)."""
    plans_raw = frappe.get_all(
        "Website Pricing Plan",
        fields=[
            "name as id",
            "plan_name",
            "plan_name_ar",
            "price",
            "price_ar",
            "period",
            "period_ar",
            "description",
            "description_ar",
            "is_popular",
            "cta_text",
            "cta_text_ar",
            "display_order",
        ],
        order_by="display_order asc",
        ignore_permissions=True,
    )

    plans = []
    for plan in plans_raw:
        # Get child table features
        features_en = frappe.get_all(
            "Website Pricing Feature",
            filters={"parent": plan.id, "parenttype": "Website Pricing Plan"},
            fields=["feature", "feature_ar"],
            order_by="idx asc",
            ignore_permissions=True,
        )

        plans.append({
            "name": plan.plan_name,
            "name_ar": plan.plan_name_ar,
            "price": plan.price,
            "price_ar": plan.price_ar,
            "period": plan.period,
            "period_ar": plan.period_ar,
            "description": plan.description,
            "description_ar": plan.description_ar,
            "popular": bool(plan.is_popular),
            "cta": plan.cta_text,
            "cta_ar": plan.cta_text_ar,
            "features": [f.feature for f in features_en],
            "features_ar": [f.feature_ar for f in features_en if f.feature_ar],
        })

    # Get comparison categories
    comparisons = frappe.get_all(
        "Website Pricing Comparison",
        fields=[
            "category_name",
            "category_name_ar",
            "feature_name",
            "feature_name_ar",
            "in_starter",
            "in_professional",
            "in_enterprise",
        ],
        order_by="display_order asc",
        ignore_permissions=True,
    )

    # Group by category
    categories = {}
    for row in comparisons:
        cat = row.category_name
        if cat not in categories:
            categories[cat] = {
                "name": cat,
                "name_ar": row.category_name_ar,
                "features": [],
            }
        categories[cat]["features"].append({
            "name": row.feature_name,
            "name_ar": row.feature_name_ar,
            "starter": bool(row.in_starter),
            "professional": bool(row.in_professional),
            "enterprise": bool(row.in_enterprise),
        })

    return {
        "success": True,
        "pricing": {
            "plans": plans,
            "comparisonCategories": list(categories.values()),
        },
    }


@frappe.whitelist(allow_guest=True)
def log_visit(path="/", browser="Unknown", source=None, campaign=None):
    """Log a page visit for analytics (public endpoint)."""
    doc = frappe.get_doc({
        "doctype": "Website Analytics",
        "path": path,
        "browser": (browser or "Unknown")[:500],
        "source": source or "",
        "campaign": campaign or "",
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    return {"success": True}


@frappe.whitelist(allow_guest=True)
def get_settings():
    """Retrieve public website settings (public endpoint)."""
    settings = frappe.get_single("Fateh Website Settings")
    return {
        "success": True,
        "settings": {
            "calendlyUrl": settings.calendly_url or "",
        },
    }
