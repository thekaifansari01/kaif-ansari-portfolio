<div align="center">

# Kaif Ansari — AI Engineer

### LLM Agents · Voice AI · RAG Systems · Full-Stack Engineering

Production-grade personal portfolio showcasing AI engineering projects, intelligent agent architectures, and a self-hosted admin panel. Built with zero frontend frameworks — pure HTML5, CSS3, and modular vanilla JavaScript, backed by Python serverless functions on Vercel.

[![Live Demo](https://img.shields.io/badge/Live-kaifansari.me-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://kaifansari.me)
[![Admin](https://img.shields.io/badge/Admin-kaifansari.me/admin-c8ff00?style=for-the-badge&logo=vercel&logoColor=black)](https://kaifansari.me/admin)
[![GitHub](https://img.shields.io/badge/GitHub-thekaifansari01-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/thekaifansari01)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-thekaifansari01-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/thekaifansari01)

[![HTML5](https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white)](#)
[![CSS3](https://img.shields.io/badge/CSS3-1572B6?logo=css3&logoColor=white)](#)
[![Vanilla JS](https://img.shields.io/badge/Vanilla_JS-F7DF1E?logo=javascript&logoColor=black)](#)
[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)](#)
[![Redis](https://img.shields.io/badge/Upstash_Redis-DC382D?logo=redis&logoColor=white)](#)
[![Resend](https://img.shields.io/badge/Resend-000000?logo=resend&logoColor=white)](#)
[![Vercel](https://img.shields.io/badge/Vercel-000000?logo=vercel&logoColor=white)](#)
[![MIT License](https://img.shields.io/badge/License-MIT-green)](#)

[Explore Portfolio](https://kaifansari.me) · [Report Bug](https://github.com/thekaifansari01/portfolio/issues) · [Request Feature](https://github.com/thekaifansari01/portfolio/issues)

</div>

---

## Table of Contents

- [Overview](#overview)
- [Highlights](#highlights)
- [Tech Stack](#tech-stack)
- [Directory Structure](#directory-structure)
- [Site Sections](#site-sections)
- [Admin Panel](#admin-panel)
- [Backend Architecture](#backend-architecture)
- [Flagship Projects](#flagship-projects)
- [SEO & Crawler Optimization](#seo--crawler-optimization)
- [Local Development](#local-development)
- [Environment Variables](#environment-variables)
- [Deployment](#deployment)
- [Contact](#contact)
- [License](#license)

---

## Overview

Official repository for **Kaif Ansari** — AI Engineer from Muzaffarnagar, Uttar Pradesh, India. This project combines a production AI engineering portfolio with a **full self-hosted CMS** for managing projects, subscribers, and messages — all without a single external framework.

The site is designed in a **neubrutalist** visual language: thick borders, hard offset shadows, sticker badges, and dual-theme polish. The frontend is hand-crafted HTML/CSS/ES6 — no build step, no bundler. The backend is two consolidated Python serverless functions on Vercel, backed by Upstash Redis and Resend.

---

## Highlights

### Design System
- **Neubrutalist UI** — 2.5px borders, offset hard shadows, sticker-style rotating tags, press-down button physics.
- **Dual-Theme Engine** — Warm cream (light) and warm black (dark) with `localStorage` persistence, consistent across site and admin panel.
- **Custom Typography Trio** — Clash Display / Anton (headings), Fraunces (body), Geist Mono (code/UI).
- **Themed Preloader** — Branded SVG graph animation (nodes → edges → reroute → loop) with theme-aware colors.
- **Grain Overlay** — Subtle SVG noise texture for depth.

### Interaction & Motion
- **5-State Precision Cursor** — Default, link, card, text-input, and image states.
- **Magnetic Buttons** — Primary CTAs subtly pull toward the cursor on hover.
- **Text Scramble** — Nav and footer links scramble glyphs into place on hover.
- **Parallax Hero Photo** — Subtle scroll-driven vertical movement.
- **Reveal-on-Scroll** — IntersectionObserver-based fade-up animations with reduced-motion respect.
- **Infinite Marquee** — Dual-track scrolling feed with pause-on-hover.
- **Live Widgets** — IST clock, animated stat counters.
- **Dynamic Project Rendering** — Cards hydrate from Redis at runtime with static fallback.

### Admin Panel
- **Magic Link Authentication** — Passwordless login via email. Tokens are single-use with 15-minute expiry.
- **Dashboard** — Live stats (subscribers, messages, unread counts) + recent audit trail.
- **Projects CRUD** — Add, edit, delete, reorder, and feature projects. GitHub stars/forks sync.
- **Subscriber Management** — Filter by status, manual add, resend confirmations, CSV export, bulk backfill of unsubscribe tokens.
- **Message Inbox** — Read, reply (threaded via email), mark read/unread/archived/spam, delete.
- **Theme Toggle** — Light/dark switch, persisted per admin session.
- **Audit Trail** — Every admin action logged with actor, target, and IP.

### Security & Infrastructure
- **Cloudflare Turnstile** — Bot mitigation on public forms.
- **Cloudflare Email Routing** — Inbound mail routing for `hello@`, `admin@`, `newsletter@` addresses.
- **Resend API** — Transactional email delivery with per-context sender addresses.
- **Rate Limiting** — Per-IP throttling on contact, newsletter, and admin login endpoints.
- **HttpOnly Session Cookies** — 7-day TTL, backed by Redis, server-side revocation.
- **Accessibility** — `prefers-reduced-motion` respected globally, semantic HTML, ARIA labels, focus traps in modals.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Markup** | HTML5 (semantic, SEO, accessible) |
| **Styling** | CSS3 — custom properties, Grid, Flexbox, `mask-image`, `backdrop-filter` fallbacks |
| **Frontend Logic** | Vanilla JavaScript (ES2020+, modular IIFE scripts) |
| **Backend** | Python 3.11 serverless functions (Vercel) |
| **Storage** | Upstash Redis (REST API) |
| **Email (Outbound)** | Resend API (via custom `mailer_lib.py` wrapper) |
| **Email (Inbound)** | Cloudflare Email Routing |
| **Security** | Cloudflare Turnstile + magic link auth |
| **Fonts** | Anton, Fraunces, Geist Mono |
| **Icons** | Material Icons Round, Font Awesome 6.5.1 |
| **Hosting** | Vercel Edge Network |

No frontend build tools. No bundlers. No frameworks. Deploy as-is.

---

## Directory Structure

```text
portfolio/
├── index.html
├── admin/
│   └── index.html
├── api/
│   ├── admin/
│   │   └── index.py
│   └── portal/
│       └── index.py
├── session_lib.py
├── mailer_lib.py
├── vercel.json
├── requirements.txt
├── robots.txt
├── sitemap.xml
├── README.md
├── google6831778c190e4906.html
├── css/
│   ├── variables.css
│   ├── base.css
│   ├── animations.css
│   ├── brutalist.css
│   ├── components/
│   │   ├── buttons.css
│   │   ├── navbar.css
│   │   ├── preloader.css
│   │   ├── theme-switch.css
│   │   └── newsletter-popup.css
│   ├── sections/
│   │   ├── hero.css
│   │   ├── marquee.css
│   │   ├── work.css
│   │   ├── about.css
│   │   ├── skills.css
│   │   └── contact.css
│   ├── layout/
│   │   └── footer.css
│   └── utils/
│       └── responsive.css
├── modules/
│   ├── avatar-loader.js
│   ├── brutalist.js
│   ├── contact-form.js
│   ├── counters.js
│   ├── cursor.js
│   ├── footer-year.js
│   ├── magnetic.js
│   ├── marquee.js
│   ├── navbar.js
│   ├── newsletter-popup.js
│   ├── parallax.js
│   ├── preloader.js
│   ├── projects-loader.js
│   ├── reveal.js
│   ├── scramble.js
│   ├── smooth-scroll.js
│   └── theme.js
└── assets/
    ├── favicon/
    │   └── favicon.png
    └── images/
        ├── mydp.png
        └── og-image.jpg
```

---

## Site Sections

| Section | Purpose |
|---|---|
| **Hero** | Terminal-style intro, name, tagline, dual CTA, animated stat counters, tape-framed portrait |
| **Live Marquee** | Real-time status feed + scrolling tech stack |
| **Work** | Dynamically rendered project grid — flagship AI projects with metrics, stack tags, live repo links. Falls back to static HTML if API unavailable |
| **About** | Bio, editorial note card, career timeline |
| **Stack** | Grouped technical proficiency (AI/LLM, Languages, Tools) |
| **Contact** | Terminal-style contact card, social links, secure form with Turnstile |
| **Footer** | Stamped copyright note, quick nav |
| **Newsletter Popup** | Delayed / exit-intent triggered double opt-in newsletter signup |

---

## Admin Panel

Accessible at `https://kaifansari.me/admin` — protected by magic link authentication.

### Features

| Tab | Capabilities |
|---|---|
| **Dashboard** | Live stats (confirmed / pending / unsubscribed subscribers, total & unread messages), recent audit log, one-time migration button |
| **Projects** | Add/edit/delete projects · drag-order via up/down buttons · toggle featured cards · GitHub stars/forks sync · auto-invalidation of public cache |
| **Subscribers** | Filter by status · search · manual add (confirmed or pending) · resend confirmation · unsubscribe · re-pend · delete · CSV export · backfill unsubscribe tokens for legacy records |
| **Messages** | Inbox view with unread indicators · reply (threaded email) · mark read/unread/archived/spam · delete · search across name/email/message |

### Authentication Flow

1. `POST /api/admin_login` → generates 32-byte token, stores `admin:magic:{token}` (15 min TTL), sends magic link email
2. User clicks link → `GET /api/admin_verify?token=...` → validates token, creates session, sets `admin_session` cookie (HttpOnly, Secure, SameSite=Lax, 7-day TTL)
3. All admin endpoints call `session_lib.get_session()` → Redis lookup → 401 if missing
4. Logout → `POST /api/admin_logout` → deletes session from Redis, clears cookie

Rate limited to 5 login attempts per IP per 15 minutes.

---

## Backend Architecture

### Two Consolidated Functions

Vercel Hobby plan limits deployments to **12 serverless functions**. To stay within limits, all endpoints are consolidated into two files with `action` query routing:

| Function | Handles |
|---|---|
| `api/admin/index.py` | `login`, `verify`, `logout`, `me`, `dashboard`, `migrate`, `subscribers` (GET/POST/PATCH/DELETE), `messages` (GET/POST/PATCH/DELETE), `projects` (GET/POST/PATCH/DELETE), `projects_sync` |
| `api/portal/index.py` | `send` (contact form), `subscribe`, `confirm`, `unsubscribe`, `projects` (public read) |

### URL Routing

`vercel.json` rewrites preserve old URL structure — frontend code never changes:

```
/api/admin_login            → /api/admin?action=login
/api/admin_subscribers      → /api/admin?action=subscribers
/api/send                   → /api/portal?action=send
/api/subscribe              → /api/portal?action=subscribe
/api/confirm                → /api/portal?action=confirm
/api/unsubscribe            → /api/portal?action=unsubscribe
/api/projects               → /api/portal?action=projects
```

### Shared Libraries

| File | Purpose |
|---|---|
| `session_lib.py` | Redis client, cookie parsing, session helpers, CORS, JSON responses, audit logging |
| `mailer_lib.py` | Resend API wrapper with per-context sender addresses |

Both files live in the project root (not inside `/api`) so Vercel bundles them as imports without creating extra endpoints.

### Redis Schema

| Key | Type | Purpose |
|---|---|---|
| `newsletter:subscribers` | Hash | `{ email: JSON({status, token, unsub_token, subscribed_at, confirmed_at, source, ip}) }` |
| `newsletter:token:{token}` | String | Confirmation token → email |
| `newsletter:unsub_token:{token}` | String | Unsubscribe token → email |
| `contact:messages` | Hash | `{ message_id: JSON({name, email, message, ip, status, created_at, reply, replied_at, email_sent}) }` |
| `contact:order` | List | Message IDs, newest first |
| `contact:unread` | Set | Unread message IDs |
| `projects:list` | Hash | `{ project_id: JSON({id, title, category, status, description, features, stack, github_url, live_url, featured, order, metrics, ...}) }` |
| `projects:cache` | String | 60-second cached public project list |
| `admin:magic:{token}` | String | Magic link token → admin email (15 min TTL) |
| `admin:session:{sid}` | String | Session ID → JSON({email, ip, created}) (7 day TTL) |
| `admin:audit` | List | Last 1000 audit entries |
| `rl:contact:{ip}` | String | Contact form rate limit counter |
| `rl:nl:{ip}` | String | Newsletter rate limit counter |
| `rl:admin-login:{ip}` | String | Admin login rate limit counter |

---

## Flagship Projects

| Project | Category | Highlights | Repo |
|---|---|---|---|
| **J.A.R.V.I.S** | Voice AI Agent | Multi-LLM failover (Groq + Gemini + Deepgram), wake-word detection, PC automation, email & calendar sync | [GitHub](https://github.com/thekaifansari01/jarvis-by-kaif-ansari) |
| **kairos.ai** | AI Workspace | Multi-model chat, in-browser Python via Pyodide, project RAG, Firebase sync | [GitHub](https://github.com/thekaifansari01/kairos.ai) |
| **Nexus** | Browser Extension | Page-aware assistant, real-time scraping, markdown rendering, persistent memory | [GitHub](https://github.com/thekaifansari01/NexusWebAssistant) |
| **GitHub Universe** | Open Source Hub | Growing collection of AI agents, LLM wrappers, scrapers, and automation utilities | [Profile](https://github.com/thekaifansari01) |

---

## SEO & Crawler Optimization

Optimized to rank for **"Kaif Ansari"**, **"AI Engineer"**, and **"LLM Developer"**:

- Complete meta tags — title, description, keywords, canonical
- Open Graph + Twitter Card rich previews
- JSON-LD structured data — `ProfilePage`, `Person`, `ItemList`, `SoftwareSourceCode`
- Semantic heading hierarchy
- `robots.txt` + XML sitemap
- Google Search Console verification
- `theme-color` meta with light/dark sync
- Static project fallback in HTML for no-JS crawlers

---

## Local Development

### Clone

```bash
git clone https://github.com/thekaifansari01/portfolio.git
cd portfolio
```

### Static frontend preview

```bash
python -m http.server 8000
```

Open `http://localhost:8000`. Admin panel and API calls will fail locally without Vercel dev.

### Full stack preview

```bash
npm install -g vercel
pip install -r requirements.txt
vercel dev
```

Open `http://localhost:3000`. All API endpoints, admin panel, and email flows work end-to-end.

### Requirements

`requirements.txt`:
```
requests==2.31.0
```

---

## Environment Variables

Add these in **Vercel Project Settings → Environment Variables**:

| Variable | Purpose |
|---|---|
| `SITE_URL` | Canonical site URL (e.g. `https://kaifansari.me`) |
| `ALLOWED_ORIGINS` | Comma-separated CORS allowlist |
| `UPSTASH_REDIS_REST_URL` | Upstash Redis REST endpoint |
| `UPSTASH_REDIS_REST_TOKEN` | Upstash Redis auth token |
| `RESEND_API_KEY` | Resend API key (`re_...`) |
| `NEWSLETTER_FROM` | Sender for newsletter confirmations (e.g. `Kaif Ansari <newsletter@kaifansari.me>`) |
| `CONTACT_FROM` | Sender for contact form notifications (e.g. `Kaif Ansari <hello@kaifansari.me>`) |
| `ADMIN_FROM` | Sender for admin magic links (e.g. `Kaif Ansari <admin@kaifansari.me>`) |
| `TO_EMAIL` | Destination inbox for contact form notifications |
| `ADMIN_EMAIL` | Single allowed admin email for magic link login |
| `TURNSTILE_SECRET_KEY` | Cloudflare Turnstile secret key |
| `GITHUB_TOKEN` | *(Optional)* GitHub PAT — raises API rate limit from 60 to 5000 req/hr for project sync |

---

## Deployment

Deploy to Vercel:

```bash
vercel --prod
```

### Pre-deploy checklist

1. **Resend domain verified** — Add SPF, DKIM, DMARC records in your DNS provider
2. **Cloudflare Email Routing active** (optional) — For `hello@`, `admin@`, `newsletter@` inbound
3. **Upstash Redis database created** — Copy REST URL and token
4. **Turnstile widget created** — Add site key to `index.html`, secret to Vercel env
5. **All env vars set** in Vercel Project Settings
6. **`vercel.json` rewrites present** — Verifies consolidated routing works

### Post-deploy checklist

1. Site loads at `https://kaifansari.me`
2. `/api/projects` returns JSON
3. Contact form sends email + stores in Redis
4. Newsletter signup triggers confirmation email
5. Admin magic link works at `/admin`
6. Dashboard shows correct stats
7. Projects render dynamically on homepage

---

## Contact

**Kaif Ansari** — AI Engineer

Muzaffarnagar, Uttar Pradesh, India

- **Email**: [hello@kaifansari.me](mailto:hello@kaifansari.me)
- **Phone**: [+91 92860 12879](tel:+919286012879)
- **GitHub**: [github.com/thekaifansari01](https://github.com/thekaifansari01)
- **LinkedIn**: [linkedin.com/in/thekaifansari01](https://linkedin.com/in/thekaifansari01)
- **X**: [x.com/thekaifansari01](https://x.com/thekaifansari01)

---

## License

Released under the **MIT License**. Designed, built, and maintained by **Kaif Ansari** ([@thekaifansari01](https://github.com/thekaifansari01)).