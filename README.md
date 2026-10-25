<div align="center">

# Kaif Ansari — AI Engineer

### LLM Agents · Voice AI · RAG Systems · Full-Stack Engineering

Production-grade personal portfolio showcasing AI engineering projects, intelligent agent architectures, and interactive web experiences. Built with zero frameworks — pure HTML5, CSS3, and modular vanilla JavaScript.

[![Live Demo](https://img.shields.io/badge/Live-kaifansari.me-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://kaifansari.me)
[![GitHub](https://img.shields.io/badge/GitHub-thekaifansari01-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/thekaifansari01)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-thekaifansari01-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/thekaifansari01)
[![X](https://img.shields.io/badge/X-thekaifansari01-000000?style=for-the-badge&logo=x&logoColor=white)](https://x.com/thekaifansari01)

[![HTML5](https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white)](#)
[![CSS3](https://img.shields.io/badge/CSS3-1572B6?logo=css3&logoColor=white)](#)
[![Vanilla JS](https://img.shields.io/badge/Vanilla_JS-F7DF1E?logo=javascript&logoColor=black)](#)
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
- [Flagship Projects](#flagship-projects)
- [SEO & Crawler Optimization](#seo--crawler-optimization)
- [Local Development](#local-development)
- [Deployment](#deployment)
- [Contact](#contact)
- [License](#license)

---

## Overview

Official repository for **Kaif Ansari** — AI Engineer from Muzaffarnagar, Uttar Pradesh, India. This portfolio showcases production AI work including LLM agents, voice assistants, and RAG pipelines, alongside a custom-built interactive frontend.

The site is designed in a **neubrutalist** visual language: thick borders, hard offset shadows, sticker badges, and dual-theme polish. No frameworks, no build step — just hand-crafted CSS and ES6 modules for a tiny footprint and instant loads.

---

## Highlights

### Design System
- **Neubrutalist UI** — 2.5px borders, offset hard shadows, sticker-style rotating tags, press-down button physics.
- **Dual-Theme Engine** — Warm cream (light) and warm black (dark) with `localStorage` persistence. Every component is hand-tuned for both themes.
- **Custom Typography Trio** — Clash Display (headings), Geist (body), Geist Mono (code/UI).
- **Themed Preloader** — Branded SVG graph animation (nodes → edges → reroute → loop) with theme-aware colors.
- **Grain Overlay** — Subtle SVG noise texture for depth.

### Interaction & Motion
- **5-State Precision Cursor** — Default, link, card, text-input, and image states. Monochrome, theme-aware, with click feedback.
- **Magnetic Buttons** — Primary CTAs subtly pull toward the cursor on hover.
- **Text Scramble** — Nav and footer links scramble random glyphs into place on hover.
- **Parallax Hero Photo** — Subtle scroll-driven vertical movement.
- **Reveal-on-Scroll** — IntersectionObserver-based fade-up animations with reduced-motion respect.
- **Section Title Underline** — Animated accent underline that draws in on reveal.
- **Infinite Marquee** — Dual-track scrolling feed (status + tech stack) with dynamic speed based on scroll velocity, pause-on-hover, and tap-to-highlight.
- **Live Widgets** — IST clock, session uptime counter, animated stat counters.
- **Diamond Timeline Markers** — Rotated square nodes that expand and shift color on hover.

### Navigation
- **Fixed Brutalist Navbar** — Thick bottom border + hard shadow, active-section tracking via scroll position.
- **Mobile Bottom Nav** — Touch-friendly pill tab bar with tilted active state, safe-area aware.
- **Smooth Anchor Scrolling** — Native `scrollIntoView` with reduced-motion respect.

### Security & Infrastructure
- **Cloudflare Turnstile** — Bot mitigation on the contact form.
- **Python Serverless API** — `/api/send` verifies Turnstile token and delivers mail via SMTP.
- **Async Toast Feedback** — Non-blocking status notifications.
- **Accessibility** — `prefers-reduced-motion` respected globally, focus-visible orange outlines, semantic HTML, ARIA labels.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Markup** | HTML5 (semantic, SEO, accessible) |
| **Styling** | CSS3 — custom properties, Grid, Flexbox, `color-mix`, `mask-image`, `backdrop-filter` fallbacks |
| **Logic** | Vanilla JavaScript (modular IIFE scripts, ES2020+) |
| **Typography** | Clash Display, Geist, Geist Mono |
| **Iconography** | Material Icons Round, Font Awesome 6.5.1 |
| **Security** | Cloudflare Turnstile |
| **Backend** | Python serverless function (Vercel) |
| **Hosting** | Vercel Edge Network |

No build tools. No bundlers. No frameworks. Deploy as-is.

---

## Directory Structure

```text
portfolio/
├── index.html
├── robots.txt
├── sitemap.xml
├── README.md
├── requirements.txt
├── google6831778c190e4906.html
├── .vercel/
│   ├── project.json
│   └── README.txt
├── api/
│   └── send.py
├── css/
│   ├── variables.css
│   ├── base.css
│   ├── animations.css
│   ├── components/
│   │   ├── buttons.css
│   │   ├── navbar.css
│   │   ├── preloader.css
│   │   └── theme-switch.css
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
│   ├── contact-form.js
│   ├── counters.js
│   ├── cursor.js
│   ├── footer-year.js
│   ├── magnetic.js
│   ├── marquee.js
│   ├── navbar.js
│   ├── parallax.js
│   ├── preloader.js
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
| **Live Marquee** | Real-time status feed (building / reading / listening / last commit) + scrolling tech stack |
| **Work** | Interactive project grid — flagship AI projects with metrics, stack tags, live repo links |
| **About** | Bio, editorial note card, career timeline with diamond markers |
| **Stack** | Grouped technical proficiency (AI/LLM, Languages, Tools) with daily/often/learning status |
| **Contact** | Terminal-style contact card, social links, secure form (Turnstile + serverless mail) |
| **Footer** | Stamped copyright note, quick nav |

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
- JSON-LD structured data — `Person`, `sameAs`, `knowsAbout`, `alumniOf`
- Semantic heading hierarchy (H1 name → H2 sections → H3 projects)
- `robots.txt` allowing all crawlers and pointing to sitemap
- XML sitemap for primary URL
- Google Search Console verification file
- `theme-color` meta for browser chrome

---

## Local Development

### Clone

```bash
git clone https://github.com/thekaifansari01/portfolio.git
cd portfolio
```

### Static preview

```bash
python -m http.server 8000
```

Open `http://localhost:8000`.

### Full stack (with serverless API)

```bash
npm install -g vercel
pip install -r requirements.txt
vercel dev
```

### Environment variables for `/api/send`

| Variable | Purpose |
|---|---|
| `TURNSTILE_SECRET_KEY` | Cloudflare Turnstile secret |
| `SMTP_HOST` | SMTP server (default `smtp.gmail.com`) |
| `SMTP_PORT` | SMTP port (default `587`) |
| `SMTP_USER` | SMTP login |
| `SMTP_PASS` | SMTP password / app password |
| `TO_EMAIL` | Destination inbox |

---

## Deployment

Deploy to Vercel — serverless function is auto-detected from `/api`:

```bash
vercel --prod
```

Post-deploy checklist:

1. Add all environment variables in Vercel Project Settings
2. Verify the Cloudflare Turnstile site key in `index.html` matches the deployed domain
3. Submit the sitemap in Google Search Console
4. Confirm `https://kaifansari.me` resolves and serves the latest deploy

---

## Contact

**Kaif Ansari** — AI Engineer

Muzaffarnagar, Uttar Pradesh, India

- **Email**: [kaif.ansari.global@gmail.com](mailto:kaif.ansari.global@gmail.com)
- **Phone**: [+91 92860 12879](tel:+919286012879)
- **GitHub**: [github.com/thekaifansari01](https://github.com/thekaifansari01)
- **LinkedIn**: [linkedin.com/in/thekaifansari01](https://linkedin.com/in/thekaifansari01)
- **X**: [x.com/thekaifansari01](https://x.com/thekaifansari01)

---

## License

Released under the **MIT License**. Designed and built by **Kaif Ansari** ([@thekaifansari01](https://github.com/thekaifansari01)).