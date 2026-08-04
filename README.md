<div align="center">

# Kaif Ansari — Portfolio

### AI Engineer & Creative Developer

A production-grade personal portfolio website built with vanilla HTML, CSS, and JavaScript — no frameworks, no build tools, just clean engineering.

[![Made with HTML](https://img.shields.io/badge/Made%20with-HTML5-E34F26?logo=html5&logoColor=white)]()
[![CSS3](https://img.shields.io/badge/Styled%20with-CSS3-1572B6?logo=css3&logoColor=white)]()
[![JavaScript](https://img.shields.io/badge/Powered%20by-Vanilla%20JS-F7DF1E?logo=javascript&logoColor=black)]()
[![Deployed on Vercel](https://img.shields.io/badge/Deployed%20on-Vercel-000000?logo=vercel&logoColor=white)]()
[![License](https://img.shields.io/badge/License-MIT-green)]()

[Live Demo](#) · [Report Bug](https://github.com/thekaifansari01) · [Request Feature](https://github.com/thekaifansari01)

</div>

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Sections](#sections)
- [Getting Started](#getting-started)
- [Deployment](#deployment)
- [Showcased Projects](#showcased-projects)
- [Contact](#contact)
- [License](#license)

---

## Overview

This is the personal portfolio of **Kaif Ansari**, an AI Engineer from Muzaffarnagar, UP, India. The portfolio showcases four major projects — **JARVIS**, **Kairos.ai**, **GitHub Universe**, and **Nexus AI** — along with a detailed about section, categorized skill bars, and a secure contact form.

The entire site is built with **zero frameworks** — pure HTML5, CSS3 (with custom properties), and vanilla ES6+ JavaScript. It features a custom design system, light/dark theme toggle, particle effects, custom cursor, and a fully responsive layout that adapts from desktop floating pill navbar to mobile bottom navigation.

---

## Features

### Design & UX
- **Light / Dark Theme** — Toggle with `localStorage` persistence, smooth transitions
- **Custom Cursor** — Follower ring + precision dot, desktop only
- **Preloader** — Animated ring with "KA" monogram branding
- **Particle Background** — Powered by tsparticles on the hero section (disabled on mobile for performance)
- **AOS Animations** — Scroll-triggered fade/slide reveals across all sections
- **Parallax Effects** — Hero image floating badges with mouse-driven parallax
- **Smooth Scrolling** — Native smooth scroll with section navigation

### Navigation
- **Desktop: Floating Pill Navbar** — Glassmorphic floating navigation with Material Icons
- **Mobile: Bottom Navigation** — Touch-optimized bottom tab bar with ripple effects and safe-area insets
- **Active Section Tracking** — Navbar highlights current section on scroll

### Interactions
- **Auto-Scrolling Work Carousel** — Infinite scroll with hover-to-pause
- **Skill Bars** — Animated progress bars with shimmer effect on scroll-into-view
- **Animated Counters** — Stats counters that animate when scrolled into view
- **Work Card Tilt** — 3D tilt effect on project cards
- **Theme Switch** — Animated toggle with sun/moon icons

### Security
- **Cloudflare Turnstile CAPTCHA** — Spam protection on contact form
- **Serverless Backend** — Python API endpoint (`/api/send`) for form submission with token verification
- **Toast Notifications** — User-friendly success/error feedback

### Responsive Design
- Breakpoints at **968px**, **768px**, **640px**, and **480px**
- Desktop navbar swaps to mobile bottom nav automatically
- tsparticles disabled on mobile for performance
- `backdrop-filter` with `@supports not` fallback for cross-browser compatibility
- Touch ripple effects on mobile navigation

---

## Tech Stack

| Category | Technology |
|----------|-----------|
| **Markup** | HTML5 (Semantic) |
| **Styling** | CSS3 (Custom Properties, Grid, Flexbox) |
| **Logic** | Vanilla JavaScript (ES6+ Modules) |
| **Fonts** | Space Grotesk (Headings) + Plus Jakarta Sans (Body) |
| **Icons** | Material Icons Round, Material Symbols Rounded, Font Awesome 6.5.1 |
| **Animations** | AOS 2.3.1 (Animate On Scroll) |
| **Particles** | tsparticles 3.0.3 |
| **Security** | Cloudflare Turnstile CAPTCHA |
| **Backend** | Python Serverless Function (Vercel) |
| **Hosting** | Vercel |
| **Build Tools** | None — zero dependencies, zero build step |

---

## Project Structure

```
portfolio/
├── index.html                  # Main HTML entry point (682 lines)
├── README.md                    # You are here
├── requirements.txt             # Python dependencies for serverless API
├── .vercel/                     # Vercel deployment config
│   ├── project.json
│   └── README.txt
├── api/
│   └── send.py                  # Serverless contact form handler
├── css/
│   ├── variables.css            # Design tokens (colors, shadows, spacing, themes)
│   ├── base.css                 # Reset, typography, global styles
│   ├── animations.css           # Keyframe animations
│   ├── components/
│   │   ├── buttons.css          # Button styles (primary, outline, CTA)
│   │   ├── cursor.css           # Custom cursor (follower + dot)
│   │   ├── navbar.css           # Desktop floating pill navbar
│   │   ├── preloader.css        # Loading screen with "KA" branding
│   │   └── theme-switch.css     # Light/dark theme toggle
│   ├── sections/
│   │   ├── hero.css             # Hero section + particle canvas
│   │   ├── marquee.css          # Scrolling marquee text
│   │   ├── work.css             # Projects showcase carousel
│   │   ├── about.css            # About + experience timeline
│   │   ├── skills.css           # Categorized skill bars
│   │   └── contact.css          # Contact form + Turnstile
│   ├── layout/
│   │   └── footer.css           # Footer with social links
│   └── utils/
│       └── responsive.css       # Media queries (968px / 768px / 640px / 480px)
├── modules/
│   ├── avatar-loader.js          # Hero avatar image loader
│   ├── contact-form.js           # Form validation + Turnstile + API submission
│   ├── counters.js               # Animated number counters
│   ├── cursor.js                 # Custom cursor movement logic
│   ├── footer-year.js            # Auto-update footer year
│   ├── hero-prallax.js           # Mouse-driven parallax on hero badges
│   ├── navbar.js                 # Navbar scroll state + active section tracking
│   ├── particles.js              # tsparticles configuration
│   ├── preloader.js              # Preloader hide on load
│   ├── skills-animation.js      # Skill bar fill animation on scroll
│   ├── smooth-scroll.js          # Smooth anchor scrolling
│   ├── theme.js                  # Theme toggle + localStorage persistence
│   └── work-tilt.js              # 3D tilt effect on work cards
└── assets/
    └── favicon/
        └── favicon.png           # Site favicon
```

---

## Sections

### Home (Hero)
- Animated particle background (tsparticles)
- Name, title, and tagline
- Floating badges with parallax effect
- CTA buttons (View Work, Get in Touch)

### Work
- Auto-scrolling infinite carousel with hover-to-pause
- 4 project cards with 3D tilt effect
- Each card: category, title, description, tech stack tags, GitHub links
- Overlay with quick links on hover

### About
- Bio: AI Engineer from Muzaffarnagar, UP
- Education: BCA at Shree Ram Group of College
- 3+ years coding experience (Python, JS, C++)
- Experience timeline with milestones
- Personal quote

### Skills
- Categorized tech stack with animated progress bars
- Shimmer effect on bar fill
- Scroll-triggered animation

### Contact
- Name, Email, Message fields
- Cloudflare Turnstile CAPTCHA
- Serverless API submission (`/api/send`)
- Toast notifications for success/error feedback

---

## Getting Started

### Prerequisites

- A modern web browser (Chrome, Firefox, Edge, Safari)
- Python 3.9+ (only if running the contact form API locally)
- [Vercel CLI](https://vercel.com/docs/cli) (optional, for local serverless dev)

### Local Development

**Option 1: Static (Frontend only)**

```bash
# Clone the repository
git clone https://github.com/thekaifansari01/portfolio.git

# Navigate to project directory
cd portfolio

# Open index.html in your browser
# Or use a local server:
python -m http.server 8000
```

Then visit `http://localhost:8000` in your browser.

**Option 2: With Serverless API (Full stack)**

```bash
# Install Vercel CLI
npm i -g vercel

# Install Python dependencies
pip install -r requirements.txt

# Run dev server with serverless functions
vercel dev
```

### Environment Variables

For the contact form to work, set up the following:

| Variable | Description |
|----------|-------------|
| `TURNSTILE_SECRET_KEY` | Cloudflare Turnstile secret key for CAPTCHA verification |
| `SMTP_CONFIG` | Email configuration for sending form submissions |

---

## Deployment

This project is deployed on **Vercel** with serverless Python functions.

### Deploy to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# From project root
vercel

# Follow the prompts, then deploy to production
vercel --prod
```

The `api/send.py` file is automatically detected as a serverless function by Vercel. No additional configuration needed.

---

## Showcased Projects

| Project | Category | Description | Tech |
|---------|----------|-------------|------|
| [**JARVIS**](https://github.com/thekaifansari01) | AI Voice Assistant | Autonomous AI assistant with voice recognition, memory, and multi-tool execution | Python, LLM, Voice AI |
| [**Kairos.ai**](https://github.com/thekaifansari01) | Web Chatbot | Interactive web-based chatbot application | Python, FastAPI, LLM |
| [**GitHub Universe**](https://github.com/thekaifansari01) | Open Source | Open-source hub with AI agents, automation tools, and security tools | Python, LLM Ops, Agentic |
| [**Nexus AI**](https://github.com/thekaifansari01/NexusWebAssistant) | AI Chat Assistant | Page-aware AI assistant with real-time content scraping and persistent memory | Groq API, Llama 4, IndexedDB |

---

## Contact

<div align="center">

**Kaif Ansari** — AI Engineer & Creative Developer

Muzaffarnagar, Uttar Pradesh, India

[![GitHub](https://img.shields.io/badge/GitHub-thekaifansari01-181717?logo=github&logoColor=white)](https://github.com/thekaifansari01)
[![Email](https://img.shields.io/badge/Email-Contact%20Me-D14836?logo=gmail&logoColor=white)](#contact)

</div>

---

## License

This project is licensed under the **MIT License** — feel free to use it as inspiration for your own portfolio, but please don't copy the content directly.

<div align="center">

<sub>Built with passion by Kaif Ansari — no frameworks, no build tools, just clean code.</sub>

</div>
