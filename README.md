<div align="center">

# Kaif Ansari — AI Engineer & Creative Developer

### Autonomous AI Agents | Voice AI | RAG Systems | Full-Stack Engineering

Production-grade personal portfolio website showcasing AI engineering projects, intelligent agent architectures, and full-stack applications. Built with clean vanilla HTML5, CSS3, and modern JavaScript.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-buildwithkaif.vercel.app-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://buildwithkaif.vercel.app)
[![GitHub](https://img.shields.io/badge/GitHub-thekaifansari01-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/thekaifansari01)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-thekaifansari01-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/thekaifansari01)
[![X / Twitter](https://img.shields.io/badge/X-thekaifansari01-000000?style=for-the-badge&logo=x&logoColor=white)](https://x.com/thekaifansari01)

[![Made with HTML5](https://img.shields.io/badge/Made%20with-HTML5-E34F26?logo=html5&logoColor=white)](https://buildwithkaif.vercel.app)
[![Styled with CSS3](https://img.shields.io/badge/Styled%20with-CSS3-1572B6?logo=css3&logoColor=white)](https://buildwithkaif.vercel.app)
[![Powered by Vanilla JS](https://img.shields.io/badge/Powered%20by-Vanilla%20JS-F7DF1E?logo=javascript&logoColor=black)](https://buildwithkaif.vercel.app)
[![Deployed on Vercel](https://img.shields.io/badge/Deployed%20on-Vercel-000000?logo=vercel&logoColor=white)](https://buildwithkaif.vercel.app)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](https://github.com/thekaifansari01)

[Explore Portfolio](https://buildwithkaif.vercel.app) · [Report Bug](https://github.com/thekaifansari01/portfolio/issues) · [Request Feature](https://github.com/thekaifansari01/portfolio/issues)

</div>

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Tech Stack & Architecture](#tech-stack--architecture)
- [Project Directory Structure](#project-directory-structure)
- [Core Portfolio Sections](#core-portfolio-sections)
- [Showcased AI Projects](#showcased-ai-projects)
- [SEO & Crawler Optimization](#seo--crawler-optimization)
- [Local Setup & Development](#local-setup--development)
- [Deployment Guide](#deployment-guide)
- [Connect with Kaif Ansari](#connect-with-kaif-ansari)
- [License](#license)

---

## Overview

Welcome to the official repository for **Kaif Ansari**'s personal portfolio. Kaif Ansari is an **AI Engineer** and developer from Muzaffarnagar, UP, India, specializing in building production-ready LLM agents, intelligent voice assistants, and scalable RAG pipelines.

This portfolio highlights flagship open-source AI projects including **J.A.R.V.I.S**, **Kairos.ai**, **GitHub Universe**, and **Nexus Web Assistant**.

The web application is built with **zero heavy frameworks** to ensure maximum performance, instant load times, and perfect SEO indexability using pure HTML5, CSS3 with custom variables, and modular ES6+ JavaScript.

---

## Key Features

### Design & User Experience
- **Light / Dark Theme Engine** — Dynamic color mode switching with `localStorage` state retention.
- **Custom Precision Cursor** — Interactive custom follower ring and dot optimized for desktop viewports.
- **Branded Preloader** — Custom loading animation featuring the "KA" monogram.
- **Particle System** — GPU-accelerated particle canvas powered by `tsparticles` on desktop viewports.
- **Scroll Animations** — Reveal animations triggered on scroll via AOS (Animate On Scroll).
- **Parallax Visuals** — Mouse-tracked 3D tilt and floating badge movement.

### Navigation Architecture
- **Desktop Floating Pill Navbar** — Glassmorphic floating header with active section tracking.
- **Mobile Bottom Navigation Bar** — Touch-friendly bottom tab interface adhering to mobile UX standards.
- **Smooth Anchor Scrolling** — Native performant scrolling between portfolio sections.

### Interactive Components
- **Infinite Work Marquee** — Continuous tech stack marquee with pause-on-hover interaction.
- **Animated Skill Meters** — Scroll-triggered progress bars with gradient shimmer styling.
- **Live Counter Metrics** — Dynamic experience statistics counters.
- **3D Interactive Cards** — Gyroscope/mouse-driven tilt mechanics on featured work cards.

### Security & Infrastructure
- **Bot Mitigation** — Cloudflare Turnstile CAPTCHA integration protecting contact endpoints.
- **Serverless API Handler** — Python-powered API serverless function (`/api/send`) for contact requests.
- **User Feedback System** — Asynchronous status notifications for user interactions.

---

## Tech Stack & Architecture

| Layer | Technology |
|---|---|
| **Markup & Semantics** | HTML5 (SEO & Accessibility Optimized) |
| **Styling & Design Tokens** | CSS3 (Variables, CSS Grid, Flexbox, Animations) |
| **Client-Side Logic** | Vanilla JavaScript (Modular ES6+) |
| **Typography** | Space Grotesk, Plus Jakarta Sans |
| **Iconography** | Material Icons Round, Material Symbols, Font Awesome 6.5.1 |
| **Libraries** | AOS 2.3.1, tsparticles 3.0.3 |
| **Security & Verification** | Cloudflare Turnstile |
| **Backend Endpoint** | Python Serverless Function (Vercel) |
| **Hosting Platform** | Vercel Edge Network |

---

## Project Directory Structure

```text
portfolio/
├── index.html
├── robots.txt
├── sitemap.xml
├── README.md
├── requirements.txt
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
│   │   ├── cursor.css
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
│   ├── hero-parallax.js
│   ├── navbar.js
│   ├── particles.js
│   ├── preloader.js
│   ├── skills-animation.js
│   ├── smooth-scroll.js
│   ├── theme.js
│   └── work-tilt.js
└── assets/
    └── favicon/
        └── favicon.png
```

---

## Core Portfolio Sections

- **Hero Section** — High-impact introduction highlighting certifications, key capabilities, and call-to-action buttons.
- **Work Showcase** — Interactive grid featuring major AI projects with live preview links and repository connections.
- **About & Experience** — Professional profile of Kaif Ansari, educational background, and technical journey milestones.
- **Skills Matrix** — Categorized technical proficiency in AI/LLM engineering, full-stack backends, and DevOps tooling.
- **Contact Hub** — Secure communication gateway powered by Cloudflare Turnstile and serverless mail delivery.

---

## Showcased AI Projects

| Project | Category | Key Highlights | Repository Link |
|---|---|---|---|
| **J.A.R.V.I.S** | Voice AI Agent | Multi-LLM failover, Llama 3.3, Gemini reasoning, PC automation, wake-word detection | [GitHub Repo](https://github.com/thekaifansari01/jarvis-by-kaif-ansari) |
| **Kairos.ai** | AI Code Interpreter | In-browser Python execution via Pyodide, RAG pipeline, Firebase cloud sync | [GitHub Repo](https://github.com/thekaifansari01/kairos.ai) |
| **GitHub Universe** | Open Source Hub | Ecosystem of AI agents, LLM wrappers, security utilities, and automation scripts | [GitHub Profile](https://github.com/thekaifansari01) |
| **Nexus Web Assistant** | Page-Aware AI Agent | Real-time web content extraction, Llama models, local conversation memory | [GitHub Repo](https://github.com/thekaifansari01/NexusWebAssistant) |

---

## SEO & Crawler Optimization

The portfolio is fully optimized for search engines to rank for **"Kaif Ansari"**, **"AI Engineer"**, and **"LLM Developer"**:

- **Advanced Meta Tags** — Title, description, and keywords strategically placed.
- **Open Graph & Twitter Cards** — Rich social media previews for sharing.
- **JSON-LD Structured Data** — Schema markup for Person, SoftwareApplication (projects), and ItemList.
- **Proper Heading Hierarchy** — H1 for name, H2 for sections, H3 for projects.
- **Canonical URL** — Prevents duplicate content issues.
- **Robots.txt** — Allows all crawlers and points to the sitemap.
- **XML Sitemap** — Ensures Google indexes the main page efficiently.

---

## Local Setup & Development

### Clone Repository

```bash
git clone https://github.com/thekaifansari01/portfolio.git
cd portfolio
```

### Static Frontend Server

```bash
python -m http.server 8000
```

Open `http://localhost:8000` in your web browser.

### Full Stack Dev Server (With Serverless API)

```bash
npm install -g vercel
pip install -r requirements.txt
vercel dev
```

---

## Deployment Guide

Deploy seamlessly on **Vercel** with automatic serverless function detection:

```bash
vercel --prod
```

---

## Connect with Kaif Ansari

**Kaif Ansari** — AI Engineer & Creative Developer

*Building Autonomous AI Agents & Voice Intelligence*

Muzaffarnagar, Uttar Pradesh, India

- **Email**: [kaif.ansari.global@gmail.com](mailto:kaif.ansari.global@gmail.com)
- **Phone**: [+91 99272 72822](tel:+919927272822)
- **GitHub**: [github.com/thekaifansari01](https://github.com/thekaifansari01)
- **LinkedIn**: [linkedin.com/in/thekaifansari01](https://linkedin.com/in/thekaifansari01)
- **Twitter/X**: [x.com/thekaifansari01](https://x.com/thekaifansari01)

---

## License

Distributed under the **MIT License**. Created by **Kaif Ansari** (`thekaifansari01`).