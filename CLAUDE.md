# buendialegal — Landing Page

Plain HTML/CSS/JS landing page for Buendia Legal, deployed via GitHub Pages from the `main` branch root.

## Project structure

```
/
├── index.html        # Main entry point (GitHub Pages root)
├── css/
│   └── styles.css    # Global styles
├── js/
│   └── main.js       # Any interactivity
└── assets/
    ├── images/       # Images and icons
    └── fonts/        # Self-hosted fonts (if any)
```

## Constraints

- No build step, no frameworks, no dependencies — pure HTML5/CSS3/vanilla JS only.
- GitHub Pages serves directly from the `main` branch root; `index.html` must stay at the root.
- Keep all paths relative so the site works both locally (file://) and on GitHub Pages.

## Deployment

Push to `main`. GitHub Pages picks up changes automatically once the Pages source is set to `main / (root)` in the repo settings.

## Local preview

Open `index.html` directly in a browser, or run a simple server:

```sh
python3 -m http.server 8080
```
