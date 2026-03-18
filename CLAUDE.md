# fateh_website — Frappe Custom App

## Overview
Shared Frappe v15 custom app serving as the backend for both fateherp.com and enfono.com. Handles CMS content, lead management, analytics, AI chatbot, and Google Analytics integration.

## Related Repos
- **This repo**: `sayanthns/fateh_website` (branch: `master`) — Frappe app
- **Fateh frontend**: `sayanthns/Fatheherp-website` — fateherp.com
- **Enfono frontend**: `sayanthns/enfono-website-v2` — enfono.com

## Server
- **IP**: 156.67.105.6
- **SSH**: `root` / `enfono123`, then `su - v15`
- **Bench path**: `/home/v15/frappe-bench/`
- **App path**: `/home/v15/frappe-bench/apps/fateh_website/`
- **Site**: `enfono-office-new` (office.enfonoerp.com)
- **Git remote on server**: `upstream` → this repo
- **Other sites**: `katcherp`, `spice`, `office` — DO NOT TOUCH

## Modules

### Fateh Website (`fateh_website/fateh_website/`)
Doctypes: Fateh Website Settings, Website Lead, Website Testimonial, Website Pricing Plan, Website Pricing Comparison, Website Pricing Feature, Website Analytics, GA4 Analytics Data

### Enfono Website (`fateh_website/enfono_website/`)
Doctypes: Enfono Website Settings (50 fields), Enfono Lead, Enfono Blog Post, Enfono Case Study, Enfono Brand, Enfono Client Logo, Enfono Testimonial, Enfono Career, Enfono Team Member, Enfono Office, Enfono Media Event, Enfono Journey Milestone, Enfono Stat Item, Enfono Work Category

## Key Files
- `hooks.py` — App config, scheduler, CORS, fixtures
- `api.py` — Fateh public API (settings, pricing, leads, analytics)
- `enfono_api.py` — Enfono public API (CMS, leads, AI chatbot, blog)
- `ga4.py` — Google Analytics Data API integration
- `tasks.py` — Daily scheduler tasks

## Scheduler Tasks
- `purge_trashed_leads` — Daily, deletes leads in Trash > 30 days
- `sync_ga4_analytics` — Daily, pulls GA4 metrics for both sites

## GA4 Integration
- Uses `google-auth` + `requests` (REST API, no heavy protobuf library)
- Credentials stored in Settings doctypes as Password fields
- `clean_json_string()` handles Frappe Password field quirks
- Data stored in `GA4 Analytics Data` doctype (per site, per day)

## Deployment
```bash
# Push changes
git add -A && git commit -m "message" && git push origin master

# On server
ssh root@156.67.105.6
su - v15
cd frappe-bench/apps/fateh_website && git pull upstream master
cd ~/frappe-bench && bench --site enfono-office-new migrate
kill -HUP $(ps aux | grep 'gunicorn.*frappe.app' | grep -v grep | head -1 | awk '{print $2}')
```

## Dependencies
- `google-auth` (in setup.py install_requires)
- `requests` (bundled with Frappe)

## CORS
Configured in `hooks.py` — allows localhost:3000-3002, enfono.com, fateherp.com
