# plainwater-site

The "digital twin" and marketing site for the **PlainWater** app — served at
**https://bpupadhyaya.github.io/plainwater-site/** via GitHub Pages (project site under
`bpupadhyaya`), until/unless a custom domain is purchased.

Design system deliberately reused from `nutrisize-health-site` (Inter, green/blue palette) —
**not** the mobile app's Zoel AI design system (Plus Jakarta Sans, domain-grid cards). Two
distinct visual languages by design: mobile apps share one look, marketing/web sites share
another.

## Structure

| Path | Page |
|------|------|
| `index.html` | Home — hero, module teaser, why-offline, free/premium framing |
| `modules/` | Module/feature browser — the actual "digital twin" (see below) |
| `about/` | About PlainWater and EqualInformation, LLC |
| `privacy/` | Privacy policy (mirrors `bpupadhyaya.github.io/privacy-plainwater.html`) |
| `disclaimer/` | Medical/water-safety disclaimer |
| `support/` | Support contact + donation links |
| `assets/` | `css/style.css` (reused nutrisize tokens), `css/modules.css` (browser-specific), self-hosted Inter font, favicon |

Plain static HTML/CSS, no client-side JS required to read any page. Edit, commit, push to
`main`; GitHub Pages deploys automatically once enabled (see setup checklist below).

## The module/feature browser (`modules/`)

This is the actual "digital twin" — the same 78-feature knowledge base that ships bundled in the
mobile app, laid out for a bigger screen. It is **generated, not hand-written**, from the mobile
app repo's `content/*.json` (the single source of truth for all 78 features):

```bash
# 1. Pull the latest content from the mobile repo (sibling checkout assumed —
#    override with PLAINWATER_MOBILE_REPO if yours differs)
bash scripts/sync-content.sh

# 2. Static-render modules/index.html + modules/<a..h>/index.html from it
python3 scripts/build-modules.py

# 3. Review the diff, then commit modules/**/*.html as normal
git add modules/ && git commit -m "Sync content from mobile repo"
```

Run this whenever the mobile repo's `content/*.json` changes. The generated HTML **is**
committed — this is a repeatable local build step, not a client-side one; every page works with
zero JavaScript.

**Important:** only free-tier features render in full (all entries + citations). Premium-tier
features render title + summary only, plus an "unlock in the app" note — the site never
publishes the full text of paid content. `scripts/sync-content.sh` pulls the raw source JSON
(including full premium text) into `.content-src/`, which is **gitignored and never served** —
only the trimmed, generated HTML in `modules/` is public. Don't change that without re-checking
this constraint.

## One-time setup checklist (not yet done)

1. **GitHub → repo Settings → Pages**: Source = `main` branch, `/ (root)`.
2. No custom domain has been purchased for PlainWater yet (unlike `nutrisize.health`). Until/
   unless one is, the site serves at `bpupadhyaya.github.io/plainwater-site/` — every internal
   link and the `<link rel="canonical">` tags already assume that path. If a custom domain is
   later purchased, follow `nutrisize-health-site/README.md`'s DNS checklist as the template, add
   a `CNAME` file, and update all `canonical`/`og:url` references (currently pointing at the
   `bpupadhyaya.github.io/plainwater-site/` subpath).

## Related

- Mobile app repo (content source of truth): `~/coding_common/pvt/plainwater`
- Portfolio-wide legal/support pages for PlainWater also exist at `bpupadhyaya.github.io`
  (`privacy-plainwater.html`, `app-support-plainwater.html`, `support-plainwater.html`) — this
  site's own `privacy/`/`support/` pages carry the same substantive copy, ported into this site's
  visual style, per the pattern `nutrisize-health-site` also follows (its own app has both a
  portfolio-hub copy and a same-domain copy of its legal pages).
- Status: PlainWater has not yet shipped to the App Store or Google Play — this site is a preview
  of the real, cited content that will ship with the app.
