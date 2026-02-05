# 11ty-landing-page

A simple landing page built with 11ty and Tailwind CSS.

> Port of the [Hugo Version](https://github.com/ttntm/hugo-landing-page)

## How to use this template

**Requirements:**

1. Eleventy (developed and tested with version 0.12.1)
2. Tailwind CSS (@2.0.4 - see [#2](https://github.com/ttntm/11ty-landing-page/issues/2))

All other dependencies are either linked from a CDN or included in this repository.

**Setup:**

1. Fork, clone or download
2. `cd` into the root folder
3. run `npm install`
4. run `npm run serve`
5. open a browser and go to `http://localhost:8080`

**Basic configuration:**

1. Eleventy -> `./.eleventy.js`
2. Tailwind -> `./tailwind.config.js`
3. Netlify -> `./netlify.toml`

CSS is built via PostCSS and based on `./src/_includes/css/_page.css`. Building CSS gets triggered by `./src/css/page.11ty.js`.

Please note that this CSS build _does not_ include the `normalize.css` file used for the 2 regular pages (imprint, privacy) - a minified production version is stored in `./src/static/css` and gets included in the build by default.

**Change Content:**

Page content is stored in

- `./src/`
  - `imprint.md`
  - `privacy.md`
- `./src/sections/`
- `./src/_data/features.json`

**Change Templates/Layout:**

Page structure and templates are stored in `./src/_layouts/` and can be edited there.

Best have a look at `./layouts/base.njk` first to understand how it all comes together - the page itself is constructed from partial templates stored in `./src/includes/` and each section has a corresponding template file (`section.**.njk`) stored there.

`index.njk` in `./src/` arranges everything, meaning that sections can be added/re-ordered/removed/... there.

**Change images:**

Images are stored in `./static/img/`; everything in there can be considered a placeholder that should eventually be replaced with your actual production images.

## Python outreach automation bot (web UI)

This repo now includes a Python web app at `automation_bot/` that demonstrates an outreach workflow:

1. Find blue-collar leads by trade + city from a dataset.
2. Build personalized email subject/body templates.
3. Run a campaign in **dry-run** mode (safe) or real SMTP mode.

### Run locally

```bash
cd automation_bot
python -m venv .venv
source .venv/bin/activate
python app.py
```

Open `http://localhost:5050`.

### SMTP configuration (optional for real sends)

Set these environment variables before starting the app:

- `SMTP_HOST`
- `SMTP_PORT` (default `587`)
- `SMTP_USER`
- `SMTP_PASS`
- `SMTP_FROM`

If **Dry run** is enabled in the UI, no emails are sent.
