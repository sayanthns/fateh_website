import frappe
import json


# ─── Helper functions to fetch data from doctypes ─────────────

def _get_settings():
    return frappe.get_single("Enfono Website Settings")


def _get_blogs():
    blogs = frappe.get_all(
        "Enfono Blog Post",
        fields=["name", "title", "slug", "category", "tags", "read_time",
                "date", "featured", "cover_image", "excerpt", "content"],
        order_by="date DESC",
    )
    result = []
    for i, b in enumerate(blogs):
        result.append({
            "id": i + 1,
            "slug": b.slug,
            "title": b.title,
            "category": b.category or "",
            "tags": [t.strip() for t in (b.tags or "").split(",") if t.strip()],
            "read_time": b.read_time or "",
            "date": str(b.date) if b.date else "",
            "featured": bool(b.featured),
            "excerpt": b.excerpt or "",
            "cover_image": b.cover_image or "",
            "content": b.content or "",
        })
    return result


def _get_brands():
    brands = frappe.get_all(
        "Enfono Brand",
        fields=["name", "brand_name", "icon", "tag", "headline",
                "description", "color", "status", "link"],
        order_by="creation ASC",
    )
    result = []
    for i, b in enumerate(brands):
        features = frappe.get_all(
            "Enfono Text Item",
            filters={"parent": b.name, "parenttype": "Enfono Brand"},
            fields=["label"],
            order_by="idx ASC",
        )
        result.append({
            "id": i + 1,
            "name": b.brand_name,
            "icon": b.icon or "",
            "tag": b.tag or "",
            "headline": b.headline or "",
            "desc": b.description or "",
            "features": [f.label for f in features],
            "color": b.color or "",
            "status": b.status or "",
            "link": b.link or "",
        })
    return result


def _get_case_studies():
    cases = frappe.get_all(
        "Enfono Case Study",
        fields=["name", "title", "category", "country", "flag", "subtitle",
                "outcome", "metric", "image", "logo", "url", "icon",
                "duration", "users"],
        order_by="creation ASC",
    )
    result = []
    for i, c in enumerate(cases):
        bullets = frappe.get_all(
            "Enfono Text Item",
            filters={"parent": c.name, "parenttype": "Enfono Case Study", "parentfield": "bullets"},
            fields=["label"],
            order_by="idx ASC",
        )
        modules = frappe.get_all(
            "Enfono Text Item",
            filters={"parent": c.name, "parenttype": "Enfono Case Study", "parentfield": "modules"},
            fields=["label"],
            order_by="idx ASC",
        )
        result.append({
            "id": i + 1,
            "category": c.category or "",
            "country": c.country or "",
            "flag": c.flag or "",
            "title": c.title,
            "subtitle": c.subtitle or "",
            "outcome": c.outcome or "",
            "metric": c.metric or "",
            "bullets": [b.label for b in bullets],
            "modules": [m.label for m in modules],
            "image": c.image or "",
            "logo": c.logo or "",
            "url": c.url or "",
            "icon": c.icon or "",
            "duration": c.duration or "",
            "users": c.users or "",
        })
    return result


def _get_careers():
    careers = frappe.get_all(
        "Enfono Career",
        filters={"published": 1},
        fields=["name", "job_title", "department", "location", "job_type",
                "description", "apply_url"],
        order_by="creation DESC",
    )
    result = []
    for i, c in enumerate(careers):
        result.append({
            "id": i + 1,
            "title": c.job_title,
            "dept": c.department or "",
            "location": c.location or "",
            "type": c.job_type or "",
            "desc": c.description or "",
            "apply_url": c.apply_url or "",
        })
    return result


def _get_testimonials():
    testimonials = frappe.get_all(
        "Enfono Testimonial",
        fields=["person_name", "role", "initials", "quote"],
        order_by="creation ASC",
    )
    return [
        {
            "name": t.person_name,
            "role": t.role or "",
            "initials": t.initials or "",
            "quote": t.quote or "",
        }
        for t in testimonials
    ]


def _get_team_members():
    members = frappe.get_all(
        "Enfono Team Member",
        fields=["name as doc_name", "member_name", "role", "display_order", "initials", "photo"],
        order_by="display_order ASC",
    )
    result = []
    for i, m in enumerate(members):
        result.append({
            "id": i + 1,
            "name": m.member_name,
            "role": m.role or "",
            "order": m.display_order or 0,
            "initials": m.initials or "",
        })
    return result


def _get_offices():
    offices = frappe.get_all(
        "Enfono Office",
        fields=["country", "flag", "office_type", "city", "address",
                "phone", "office_email", "color"],
        order_by="creation ASC",
    )
    return [
        {
            "country": o.country or "",
            "flag": o.flag or "",
            "type": o.office_type or "",
            "city": o.city or "",
            "address": o.address or "",
            "phone": o.phone or "",
            "email": o.office_email or "",
            "color": o.color or "",
        }
        for o in offices
    ]


def _get_media_events():
    events = frappe.get_all(
        "Enfono Media Event",
        fields=["name", "title", "event_date", "description", "image"],
        order_by="event_date DESC",
    )
    result = []
    for e in events:
        tags = frappe.get_all(
            "Enfono Media Tag",
            filters={"parent": e.name, "parenttype": "Enfono Media Event"},
            fields=["text", "icon"],
            order_by="idx ASC",
        )
        buttons = frappe.get_all(
            "Enfono Media Button",
            filters={"parent": e.name, "parenttype": "Enfono Media Event"},
            fields=["label", "url", "button_type"],
            order_by="idx ASC",
        )
        # Format date as "DD MMM" like the frontend expects
        date_str = ""
        if e.event_date:
            from datetime import datetime
            try:
                dt = datetime.strptime(str(e.event_date), "%Y-%m-%d")
                date_str = dt.strftime("%d %b").upper()
            except Exception:
                date_str = str(e.event_date)

        result.append({
            "title": e.title,
            "date": date_str,
            "desc": e.description or "",
            "image": e.image or "",
            "tags": [{"text": t.text, "icon": t.icon or ""} for t in tags],
            "buttons": [{"label": b.label, "url": b.url or "", "type": b.button_type or ""} for b in buttons],
        })
    return result


def _get_client_logos():
    logos = frappe.get_all(
        "Enfono Client Logo",
        fields=["name", "client_name", "logo_image", "display_order"],
        order_by="display_order ASC, creation ASC",
    )
    return [{"name": l.client_name, "logo": l.logo_image or "", "order": l.display_order or 0} for l in logos]


def _get_journey_milestones():
    milestones = frappe.get_all(
        "Enfono Journey Milestone",
        fields=["year", "title", "description"],
        order_by="display_order ASC",
    )
    return [
        {
            "year": m.year or "",
            "title": m.title or "",
            "desc": m.description or "",
        }
        for m in milestones
    ]


def _assemble_cms_data():
    """Assemble the full CMS JSON from individual doctypes — same shape as the old JSON blob."""
    settings = _get_settings()

    # Build stats from child table
    stats_list = []
    for s in (settings.stats or []):
        stats_list.append({
            "label": s.label,
            "value": s.stat_value,
            "suffix": s.suffix or "",
        })

    # Build about stats from child table
    about_stats_list = []
    for s in (settings.about_stats or []):
        about_stats_list.append({
            "end": int(s.stat_value) if s.stat_value and s.stat_value.isdigit() else 0,
            "suffix": s.suffix or "",
            "label": s.label,
        })

    # Build work categories from child table
    work_categories = [c.category_name for c in (settings.our_work_categories or [])]

    return {
        "hero": {
            "heading": settings.hero_heading or "",
            "subtext": settings.hero_subtext or "",
            "cta_primary": settings.hero_cta_primary or "",
            "cta_secondary": settings.hero_cta_secondary or "",
            "booking_url": settings.hero_booking_url or settings.calendly_url or "",
        },
        "services_hero": {
            "heading": settings.services_heading or "",
            "subtext": settings.services_subtext or "",
            "cta_primary": settings.services_cta_primary or "",
            "cta_url": settings.services_cta_url or "",
        },
        "stats": stats_list,
        "contact": {
            "whatsapp": settings.whatsapp or "",
            "phone": settings.phone or "",
            "email": settings.email or "",
        },
        "chatbot": {
            "provider": settings.chatbot_provider or "openai",
            "training_data": settings.chatbot_training_data or "",
            # api_key intentionally omitted from public response
        },
        "ai_cta": {
            "heading": settings.ai_cta_heading or "",
            "subtext": settings.ai_cta_subtext or "",
            "btn_primary_txt": settings.ai_cta_btn_primary_txt or "",
            "btn_primary_url": settings.ai_cta_btn_primary_url or "",
            "btn_secondary_txt": settings.ai_cta_btn_secondary_txt or "",
            "btn_secondary_url": settings.ai_cta_btn_secondary_url or "",
        },
        "brands": _get_brands(),
        "our_work": _get_case_studies(),
        "our_work_categories": work_categories,
        "media_events": _get_media_events(),
        "blogs": _get_blogs(),
        "careers": _get_careers(),
        "testimonials": _get_testimonials(),
        "client_logos": _get_client_logos(),
        "about": {
            "who_we_are": {
                "heading": settings.about_heading or "",
                "subtext": settings.about_subtext or "",
                "stats": about_stats_list,
            },
            "journey": _get_journey_milestones(),
            "team": _get_team_members(),
            "offices": _get_offices(),
        },
    }


# ─── CMS Endpoints ────────────────────────────────────────────

@frappe.whitelist(allow_guest=True)
def get_cms(key="enfono_cms_data"):
    """Get CMS data — assembles from individual doctypes (backward compatible)."""
    if key == "enfono_cms_data":
        return _assemble_cms_data()
    elif key == "enfono_media_files":
        settings = _get_settings()
        if settings.media_files:
            try:
                return json.loads(settings.media_files)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}
    else:
        frappe.throw(f"Unknown CMS key: {key}", frappe.DoesNotExistError)


@frappe.whitelist()
def update_cms(key="enfono_cms_data", content=None):
    """Update CMS data — legacy endpoint, kept for backward compatibility."""
    settings = _get_settings()

    if isinstance(content, str):
        try:
            json.loads(content)
        except json.JSONDecodeError:
            frappe.throw("Invalid JSON content")
    else:
        content = json.dumps(content)

    if key == "enfono_cms_data":
        settings.cms_data = content
    elif key == "enfono_media_files":
        settings.media_files = content
    else:
        frappe.throw(f"Unknown CMS key: {key}", frappe.DoesNotExistError)

    settings.save(ignore_permissions=True)
    frappe.db.commit()
    return {"success": True}


# ─── Individual Public Endpoints ─────────────────────────────

@frappe.whitelist(allow_guest=True)
def get_blogs(category=None, featured=None, limit=20, offset=0):
    """List blog posts with optional filters."""
    filters = {}
    if category:
        filters["category"] = category
    if featured is not None:
        filters["featured"] = 1

    blogs = frappe.get_all(
        "Enfono Blog Post",
        filters=filters,
        fields=["title", "slug", "category", "tags", "read_time",
                "date", "featured", "cover_image", "excerpt", "content"],
        order_by="date DESC",
        limit_page_length=int(limit),
        start=int(offset),
    )
    return {"success": True, "blogs": blogs}


@frappe.whitelist(allow_guest=True)
def get_blog(slug=None):
    """Get single blog post by slug."""
    if not slug:
        frappe.throw("Slug is required")
    if not frappe.db.exists("Enfono Blog Post", slug):
        frappe.throw("Blog post not found", frappe.DoesNotExistError)
    doc = frappe.get_doc("Enfono Blog Post", slug)
    return {
        "success": True,
        "blog": {
            "title": doc.title,
            "slug": doc.slug,
            "category": doc.category,
            "tags": [t.strip() for t in (doc.tags or "").split(",") if t.strip()],
            "read_time": doc.read_time,
            "date": str(doc.date) if doc.date else "",
            "featured": bool(doc.featured),
            "cover_image": doc.cover_image,
            "excerpt": doc.excerpt,
            "content": doc.content,
        },
    }


@frappe.whitelist(allow_guest=True)
def get_careers():
    """List published career openings."""
    return {"success": True, "careers": _get_careers()}


@frappe.whitelist(allow_guest=True)
def get_case_studies(category=None):
    """List case studies with optional category filter."""
    result = _get_case_studies()
    if category:
        result = [c for c in result if c.get("category") == category]
    return {"success": True, "case_studies": result}


@frappe.whitelist(allow_guest=True)
def get_testimonials():
    """List testimonials."""
    return {"success": True, "testimonials": _get_testimonials()}


@frappe.whitelist(allow_guest=True)
def get_team_members():
    """List team members."""
    return {"success": True, "team": _get_team_members()}


@frappe.whitelist(allow_guest=True)
def get_offices():
    """List offices."""
    return {"success": True, "offices": _get_offices()}


@frappe.whitelist(allow_guest=True)
def get_media_events():
    """List media events."""
    return {"success": True, "events": _get_media_events()}


@frappe.whitelist(allow_guest=True)
def get_client_logos():
    """List client logos."""
    return {"success": True, "logos": _get_client_logos()}


@frappe.whitelist(allow_guest=True)
def get_brands():
    """List brands/products."""
    return {"success": True, "brands": _get_brands()}


@frappe.whitelist(allow_guest=True)
def get_site_settings():
    """Get public-safe site settings (no secrets)."""
    settings = _get_settings()
    stats_list = [
        {"label": s.label, "value": s.stat_value, "suffix": s.suffix or ""}
        for s in (settings.stats or [])
    ]
    return {
        "success": True,
        "settings": {
            "hero": {
                "heading": settings.hero_heading or "",
                "subtext": settings.hero_subtext or "",
                "cta_primary": settings.hero_cta_primary or "",
                "cta_secondary": settings.hero_cta_secondary or "",
                "booking_url": settings.hero_booking_url or settings.calendly_url or "",
            },
            "services_hero": {
                "heading": settings.services_heading or "",
                "subtext": settings.services_subtext or "",
                "cta_primary": settings.services_cta_primary or "",
                "cta_url": settings.services_cta_url or "",
            },
            "ai_cta": {
                "heading": settings.ai_cta_heading or "",
                "subtext": settings.ai_cta_subtext or "",
                "btn_primary_txt": settings.ai_cta_btn_primary_txt or "",
                "btn_primary_url": settings.ai_cta_btn_primary_url or "",
                "btn_secondary_txt": settings.ai_cta_btn_secondary_txt or "",
                "btn_secondary_url": settings.ai_cta_btn_secondary_url or "",
            },
            "stats": stats_list,
            "contact": {
                "whatsapp": settings.whatsapp or "",
                "phone": settings.phone or "",
                "email": settings.email or "",
            },
            "calendly_url": settings.calendly_url or "",
        },
    }


# ─── Leads Endpoints ──────────────────────────────────────────

@frappe.whitelist(allow_guest=True)
def submit_lead(name=None, email=None, phone=None, company=None,
                service=None, country="Saudi Arabia", message=None,
                lead_type="contact_form_lead", source="Contact Form"):
    """Submit a new lead — replaces POST /api/leads"""
    doc = frappe.get_doc({
        "doctype": "Enfono Lead",
        "lead_name": name or "Anonymous",
        "email": email or "",
        "phone": phone or "",
        "company": company or "",
        "service": service or "",
        "country": country or "Saudi Arabia",
        "message": message or "",
        "lead_type": lead_type or "contact_form_lead",
        "source": source or "Contact Form",
        "status": "New",
        "created_date": frappe.utils.now_datetime().strftime("%Y-%m-%d %H:%M:%S"),
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    return {"success": True}


@frappe.whitelist()
def get_leads():
    """Get all leads — admin only"""
    leads = frappe.get_all(
        "Enfono Lead",
        fields=["name", "lead_name", "email", "phone", "company",
                "service", "country", "message", "status", "source",
                "lead_type", "created_date", "creation"],
        order_by="creation DESC",
        ignore_permissions=True,
    )
    return leads


# ─── Chatbot Proxy ────────────────────────────────────────────

@frappe.whitelist(allow_guest=True)
def chat(messages=None, provider="openai"):
    """Proxy chat to OpenAI — replaces POST /api/chat"""
    import requests

    if not messages:
        frappe.throw("No messages provided")

    settings = _get_settings()
    api_key = settings.get_password("chatbot_api_key") if settings.chatbot_api_key else None

    if not api_key:
        frappe.throw("AI API key not configured", frappe.ValidationError)

    if isinstance(messages, str):
        messages = json.loads(messages)

    if provider == "openai":
        try:
            resp = requests.post(
                "https://api.openai.com/v1/chat/completions",
                json={"model": "gpt-4o", "messages": messages},
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                timeout=30,
            )
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            frappe.log_error(f"Chat API error: {e}", "Enfono Chatbot")
            frappe.throw("AI service error", frappe.ValidationError)
    else:
        frappe.throw("Unsupported provider", frappe.ValidationError)


# ─── Email (Contact Form) ────────────────────────────────────

@frappe.whitelist(allow_guest=True)
def send_email(email=None, name=None, phone=None, comment=None):
    """Send notification email"""
    if not email:
        frappe.throw("Email is required")

    settings = _get_settings()
    to_email = settings.email or "contact@enfono.com"

    try:
        frappe.sendmail(
            recipients=[to_email],
            subject=f"Enfono - {'Contact' if name else 'Subscription'} Form",
            message=f"Name: {name}\nEmail: {email}\nPhone: {phone}\nMessage: {comment}",
        )
        return {"status": "success"}
    except Exception as e:
        frappe.log_error(f"Email error: {e}", "Enfono Email")
        return {"status": "fail"}


# ─── File Upload ──────────────────────────────────────────────

@frappe.whitelist()
def upload_file():
    """Handle file upload"""
    files = frappe.request.files
    if "file" not in files:
        frappe.throw("No file uploaded")

    file = files["file"]
    ret = frappe.get_doc({
        "doctype": "File",
        "file_name": file.filename,
        "content": file.read(),
        "is_private": 0,
    })
    ret.save(ignore_permissions=True)
    frappe.db.commit()

    return {
        "url": ret.file_url,
        "name": ret.file_name,
        "type": file.content_type,
    }
