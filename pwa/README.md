# WURA as a home-screen app

`app/` is the ready-to-host app, built from `project/WURA.dc.html`.

## Put it online (GitHub Pages)
1. Push this repo to GitHub (public repo, or a paid plan for private Pages).
2. On GitHub: **Settings → Pages → Source: GitHub Actions**.
3. The `Deploy WURA to GitHub Pages` workflow runs on every push to `main`.
   Your link is `https://<your-username>.github.io/<repo-name>/`.

## Add it to your home screen
- **iPhone (Safari):** open the link → Share → **Add to Home Screen**.
- **Android (Chrome):** open the link → ⋮ menu → **Install app** / **Add to Home screen**.

It opens full-screen and works offline. Everything you write stays on your phone only.

## After a new design export
Replace `project/WURA.dc.html`, then run `python3 pwa/build.py` (needs Pillow) and push.
