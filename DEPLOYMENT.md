# 🚀 Deployment Guide - Portfolio Web Application

This document provides clear, step-by-step instructions for deploying Sudeera Hemantha's Portfolio website (`index.html`) to **GitHub Pages** and **Vercel**.

---

## 📌 Architecture & Prerequisites

- **Zero Build Tooling Required**: The application is built using modern HTML5, Tailwind CSS (via CDN), FontAwesome icons, and Vanilla JavaScript. No bundlers (`webpack`, `vite`, `vite build`) or compilation steps are needed.
- **Root Entry Point**: `index.html` is located directly at the root of the repository.
- **GitHub Target URL**: `https://github.com/SudeeraHemantha/Portfolio_Projects`

---

## 🌐 Option 1: Deploying to GitHub Pages (Recommended)

### Step 1: Push Repository to GitHub
Ensure all files are committed and pushed to your GitHub repository:

```bash
git add .
git commit -m "feat: add single-page enterprise portfolio index.html and deployment guide"
git branch -M main
git remote add origin https://github.com/SudeeraHemantha/Portfolio_Projects.git
git push -u origin main
```

### Step 2: Enable GitHub Pages via Settings
1. Open your repository on GitHub: [`https://github.com/SudeeraHemantha/Portfolio_Projects`](https://github.com/SudeeraHemantha/Portfolio_Projects)
2. Click on **Settings** (top navigation bar).
3. On the left sidebar, scroll down and click **Pages** (under Code and automation).
4. Under **Build and deployment**:
   - **Source**: Select `Deploy from a branch`
   - **Branch**: Select `main` and root folder `/ (root)`
5. Click **Save**.

### Step 3: Access Live Site
Within 1–2 minutes, GitHub Actions will publish your portfolio at:
👉 **`https://sudeerahemantha.github.io/Portfolio_Projects/`**

---

## ⚡ Option 2: Deploying to Vercel

### Method A: Via Vercel Web Dashboard (Easiest)
1. Go to [vercel.com](https://vercel.com) and log in with your GitHub account.
2. Click **Add New...** -> **Project**.
3. Select and import `SudeeraHemantha/Portfolio_Projects`.
4. Under **Framework Preset**, select **Other** (or Static HTML).
5. Leave **Root Directory** as `./`.
6. Click **Deploy**.
7. Vercel will instantly generate a live production URL (e.g. `https://portfolio-projects-sudeera.vercel.app`).

### Method B: Via Vercel CLI
If you prefer deploying directly from your local terminal:

```bash
# 1. Install Vercel CLI globally
npm install -g vercel

# 2. Login to Vercel
vercel login

# 3. Deploy to Preview
vercel

# 4. Deploy to Production
vercel --prod
```

---

## 🧪 Local Preview & Testing

To test and verify the portfolio locally before pushing changes:

### Using Python HTTP Server:
```bash
python -m http.server 8000
# Open http://localhost:8000 in your browser
```

### Using Node `serve` package:
```bash
npx serve .
# Open http://localhost:3000 in your browser
```

---

## ✅ Deployment Checklist

- [x] `index.html` located at project root.
- [x] All 10 project cards mapped to correct pillar categories.
- [x] Interactive filter tabs verified (All, Infrastructure, AI & Data, Full-Stack Apps, Database & Systems).
- [x] Tech stack badges verified for all 10 projects.
- [x] GitHub profile links pointed to `https://github.com/SudeeraHemantha`.
- [x] Mobile responsiveness checked across small and large screen viewports.
