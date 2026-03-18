"""
One-time migration: Move CMS data from JSON blob to individual Frappe doctypes.

Usage:
    bench --site mysite.local execute fateh_website.enfono_migrate.migrate_cms_to_doctypes
"""

import frappe
import json


def migrate_cms_to_doctypes():
    """Read cms_data JSON from Enfono Website Settings and create individual doctype records."""
    settings = frappe.get_single("Enfono Website Settings")

    if not settings.cms_data:
        print("No cms_data found in Enfono Website Settings. Nothing to migrate.")
        return

    try:
        cms = json.loads(settings.cms_data)
    except (json.JSONDecodeError, TypeError):
        print("ERROR: cms_data is not valid JSON.")
        return

    print("Starting CMS data migration...")

    # 1. Hero section → Settings fields
    hero = cms.get("hero", {})
    if hero:
        settings.hero_heading = hero.get("heading", "")
        settings.hero_subtext = hero.get("subtext", "")
        settings.hero_cta_primary = hero.get("cta_primary", "")
        settings.hero_cta_secondary = hero.get("cta_secondary", "")
        settings.hero_booking_url = hero.get("booking_url", "")
        print("  ✓ Hero section migrated")

    # 2. Services hero → Settings fields
    services_hero = cms.get("services_hero", {})
    if services_hero:
        settings.services_heading = services_hero.get("heading", "")
        settings.services_subtext = services_hero.get("subtext", "")
        settings.services_cta_primary = services_hero.get("cta_primary", "")
        settings.services_cta_url = services_hero.get("cta_url", "")
        print("  ✓ Services hero migrated")

    # 3. AI CTA → Settings fields
    ai_cta = cms.get("ai_cta", {})
    if ai_cta:
        settings.ai_cta_heading = ai_cta.get("heading", "")
        settings.ai_cta_subtext = ai_cta.get("subtext", "")
        settings.ai_cta_btn_primary_txt = ai_cta.get("btn_primary_txt", "")
        settings.ai_cta_btn_primary_url = ai_cta.get("btn_primary_url", "")
        settings.ai_cta_btn_secondary_txt = ai_cta.get("btn_secondary_txt", "")
        settings.ai_cta_btn_secondary_url = ai_cta.get("btn_secondary_url", "")
        print("  ✓ AI CTA section migrated")

    # 4. Contact info → Settings fields (may already be set)
    contact = cms.get("contact", {})
    if contact:
        if not settings.whatsapp:
            settings.whatsapp = contact.get("whatsapp", "")
        if not settings.phone:
            settings.phone = contact.get("phone", "")
        if not settings.email:
            settings.email = contact.get("email", "")
        print("  ✓ Contact info migrated")

    # 5. Stats → child table
    stats = cms.get("stats", [])
    if stats:
        settings.stats = []
        for s in stats:
            settings.append("stats", {
                "label": s.get("label", ""),
                "stat_value": str(s.get("value", "")),
                "suffix": s.get("suffix", ""),
            })
        print(f"  ✓ {len(stats)} stats migrated")

    # 6. About section
    about = cms.get("about", {})
    if about:
        who_we_are = about.get("who_we_are", {})
        if who_we_are:
            settings.about_heading = who_we_are.get("heading", "")
            settings.about_subtext = who_we_are.get("subtext", "")

            about_stats = who_we_are.get("stats", [])
            if about_stats:
                settings.about_stats = []
                for s in about_stats:
                    settings.append("about_stats", {
                        "label": s.get("label", ""),
                        "stat_value": str(s.get("end", s.get("value", ""))),
                        "suffix": s.get("suffix", ""),
                    })
            print("  ✓ About - Who We Are migrated")

        # Journey milestones
        journey = about.get("journey", [])
        for j in journey:
            if not frappe.db.exists("Enfono Journey Milestone", {"year": j.get("year"), "title": j.get("title")}):
                frappe.get_doc({
                    "doctype": "Enfono Journey Milestone",
                    "year": j.get("year", ""),
                    "title": j.get("title", ""),
                    "description": j.get("desc", ""),
                    "display_order": journey.index(j) + 1,
                }).insert(ignore_permissions=True)
        if journey:
            print(f"  ✓ {len(journey)} journey milestones migrated")

        # Team members
        team = about.get("team", [])
        for t in team:
            if not frappe.db.exists("Enfono Team Member", {"member_name": t.get("name")}):
                frappe.get_doc({
                    "doctype": "Enfono Team Member",
                    "member_name": t.get("name", ""),
                    "role": t.get("role", ""),
                    "display_order": t.get("order", 0),
                    "initials": t.get("initials", ""),
                }).insert(ignore_permissions=True)
        if team:
            print(f"  ✓ {len(team)} team members migrated")

        # Offices
        offices = about.get("offices", [])
        for o in offices:
            if not frappe.db.exists("Enfono Office", {"city": o.get("city"), "country": o.get("country")}):
                frappe.get_doc({
                    "doctype": "Enfono Office",
                    "country": o.get("country", ""),
                    "flag": o.get("flag", ""),
                    "office_type": o.get("type", ""),
                    "city": o.get("city", ""),
                    "address": o.get("address", ""),
                    "phone": o.get("phone", ""),
                    "office_email": o.get("email", ""),
                    "color": o.get("color", ""),
                }).insert(ignore_permissions=True)
        if offices:
            print(f"  ✓ {len(offices)} offices migrated")

    # 7. Work categories → child table
    work_categories = cms.get("our_work_categories", [])
    if work_categories:
        settings.our_work_categories = []
        for cat in work_categories:
            settings.append("our_work_categories", {
                "category_name": cat if isinstance(cat, str) else cat.get("name", ""),
            })
        print(f"  ✓ {len(work_categories)} work categories migrated")

    # Save settings with all the new fields
    settings.save(ignore_permissions=True)

    # 8. Blogs
    blogs = cms.get("blogs", [])
    for b in blogs:
        slug = b.get("slug", "")
        if slug and not frappe.db.exists("Enfono Blog Post", slug):
            # Parse date - handle formats like "March 4, 2026" or "2026-03-04"
            date_val = None
            raw_date = b.get("date", "")
            if raw_date:
                from datetime import datetime
                for fmt in ("%B %d, %Y", "%b %d, %Y", "%Y-%m-%d", "%d %b %Y", "%d/%m/%Y"):
                    try:
                        date_val = datetime.strptime(raw_date.strip(), fmt).strftime("%Y-%m-%d")
                        break
                    except ValueError:
                        continue

            frappe.get_doc({
                "doctype": "Enfono Blog Post",
                "title": b.get("title", ""),
                "slug": slug,
                "category": b.get("category", ""),
                "tags": ", ".join(b.get("tags", [])) if isinstance(b.get("tags"), list) else b.get("tags", ""),
                "read_time": b.get("read_time", ""),
                "date": date_val,
                "featured": 1 if b.get("featured") else 0,
                "cover_image": b.get("cover_image", ""),
                "excerpt": b.get("excerpt", ""),
                "content": b.get("content", ""),
            }).insert(ignore_permissions=True)
    if blogs:
        print(f"  ✓ {len(blogs)} blog posts migrated")

    # 9. Careers
    careers = cms.get("careers", [])
    for c in careers:
        if not frappe.db.exists("Enfono Career", {"job_title": c.get("title")}):
            frappe.get_doc({
                "doctype": "Enfono Career",
                "job_title": c.get("title", ""),
                "department": c.get("dept", ""),
                "location": c.get("location", ""),
                "job_type": c.get("type", ""),
                "description": c.get("desc", ""),
                "apply_url": c.get("apply_url", ""),
                "published": 1,
            }).insert(ignore_permissions=True)
    if careers:
        print(f"  ✓ {len(careers)} careers migrated")

    # 10. Testimonials
    testimonials = cms.get("testimonials", [])
    for t in testimonials:
        if not frappe.db.exists("Enfono Testimonial", {"person_name": t.get("name")}):
            frappe.get_doc({
                "doctype": "Enfono Testimonial",
                "person_name": t.get("name", ""),
                "role": t.get("role", ""),
                "initials": t.get("initials", ""),
                "quote": t.get("quote", ""),
            }).insert(ignore_permissions=True)
    if testimonials:
        print(f"  ✓ {len(testimonials)} testimonials migrated")

    # 11. Client logos
    client_logos = cms.get("client_logos", [])
    for i, l in enumerate(client_logos):
        client_name = l.get("name", "") if isinstance(l, dict) else str(l)
        if client_name and not frappe.db.exists("Enfono Client Logo", {"client_name": client_name}):
            frappe.get_doc({
                "doctype": "Enfono Client Logo",
                "client_name": client_name,
                "display_order": i + 1,
            }).insert(ignore_permissions=True)
    if client_logos:
        print(f"  ✓ {len(client_logos)} client logos migrated")

    # 12. Brands
    brands = cms.get("brands", [])
    for b in brands:
        if not frappe.db.exists("Enfono Brand", {"brand_name": b.get("name")}):
            doc = frappe.get_doc({
                "doctype": "Enfono Brand",
                "brand_name": b.get("name", ""),
                "icon": b.get("icon", ""),
                "tag": b.get("tag", ""),
                "headline": b.get("headline", ""),
                "description": b.get("desc", ""),
                "color": b.get("color", ""),
                "status": b.get("status", ""),
                "link": b.get("link", ""),
            })
            for feat in b.get("features", []):
                doc.append("features", {"label": feat})
            doc.insert(ignore_permissions=True)
    if brands:
        print(f"  ✓ {len(brands)} brands migrated")

    # 13. Case studies / Our Work
    our_work = cms.get("our_work", [])
    for w in our_work:
        if not frappe.db.exists("Enfono Case Study", {"title": w.get("title")}):
            doc = frappe.get_doc({
                "doctype": "Enfono Case Study",
                "title": w.get("title", ""),
                "category": w.get("category", ""),
                "country": w.get("country", ""),
                "flag": w.get("flag", ""),
                "subtitle": w.get("subtitle", ""),
                "outcome": w.get("outcome", ""),
                "metric": w.get("metric", ""),
                "image": w.get("image", ""),
                "logo": w.get("logo", ""),
                "url": w.get("url", ""),
                "icon": w.get("icon", ""),
                "duration": w.get("duration", ""),
                "users": w.get("users", ""),
            })
            for bullet in w.get("bullets", []):
                doc.append("bullets", {"label": bullet})
            for module in w.get("modules", []):
                doc.append("modules", {"label": module})
            doc.insert(ignore_permissions=True)
    if our_work:
        print(f"  ✓ {len(our_work)} case studies migrated")

    # 14. Media events
    media_events = cms.get("media_events", [])
    for e in media_events:
        if not frappe.db.exists("Enfono Media Event", {"title": e.get("title")}):
            doc = frappe.get_doc({
                "doctype": "Enfono Media Event",
                "title": e.get("title", ""),
                "event_date": None,  # date format in CMS is "12 SEP", hard to parse reliably
                "description": e.get("desc", ""),
                "image": e.get("image", ""),
            })
            for tag in e.get("tags", []):
                doc.append("tags", {
                    "text": tag.get("text", ""),
                    "icon": tag.get("icon", ""),
                })
            for btn in e.get("buttons", []):
                doc.append("buttons", {
                    "label": btn.get("label", ""),
                    "url": btn.get("url", ""),
                    "button_type": btn.get("type", ""),
                })
            doc.insert(ignore_permissions=True)
    if media_events:
        print(f"  ✓ {len(media_events)} media events migrated")

    frappe.db.commit()
    print("\n✅ Migration complete! All CMS data moved to individual doctypes.")
    print("   The old cms_data JSON blob is preserved but hidden in Settings.")
