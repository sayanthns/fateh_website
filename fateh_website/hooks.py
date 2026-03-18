app_name = "fateh_website"
app_title = "Fateh Website"
app_publisher = "Fateh ERP"
app_description = "Fateh ERP Marketing Website"
app_email = "dev@fateherp.com"
app_license = "MIT"

# Fixtures — auto-loaded on bench migrate
fixtures = [
    {"dt": "Website Testimonial"},
    {"dt": "Website Pricing Plan"},
    {"dt": "Website Pricing Comparison"},
    {"dt": "Fateh Website Settings"},
]

# Install
after_install = "fateh_website.install.after_install"

# Website — home_page removed since frontends are hosted separately on VPS
# home_page = "fateh"
# website_route_rules = [
#     {"from_route": "/pricing", "to_route": "fateh"},
#     {"from_route": "/404", "to_route": "fateh"},
# ]

# Scheduled Tasks
scheduler_events = {
    "daily": [
        "fateh_website.tasks.purge_trashed_leads",
        "fateh_website.tasks.sync_ga4_analytics",
    ]
}

# CORS — Allow website frontends to call Frappe APIs
allow_cors = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "https://enfono.com",
    "https://www.enfono.com",
    "https://fateherp.com",
    "https://www.fateherp.com",
]
