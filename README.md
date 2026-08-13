# Resuma.pk — Pakistan's Job Search Engine

Resuma.pk is a modern, mobile-first job search engine built for the Pakistani market.
It connects job seekers with employers across Karachi, Lahore, Islamabad and beyond, with a
premium, world-class product experience (fast, accessible, and beautiful by default).

> **Original design** — Resuma uses a bespoke visual language (deep emerald, ink and gold),
> not a clone of any existing portal.

## Stack

| Layer        | Choice                                              |
|--------------|-----------------------------------------------------|
| Backend      | Django 5.2 (LTS), class-based + function views     |
| Database     | SQLite in dev · PostgreSQL in production (via `DATABASE_URL`) |
| Styling      | Tailwind CSS v4 (build step → single minified file) |
| Interactivity| Minimal vanilla JS (fetch/AJAX, modals, menus)     |
| Static files | WhiteNoise + `CompressedManifestStaticFilesStorage` |
| Deploy       | Vercel (serverless) · Render / Railway (recommended) |

## Features

- **Job listings** with keyword + city + job-type + experience + category filters, pagination and sorting.
- **Company profiles** with logo, description, industry, website and a list of open roles.
- **Two roles**: Job Seekers (register, upload resume, save jobs, apply) and Employers
  (company profile, post/manage jobs, track applicants).
- **Homepage** with hero search, featured jobs, categories, latest jobs and top companies.
- **Static pages**: About, Contact, Privacy, Terms, FAQ, 404, 500.
- **Security & performance**: CSRF, HTTPS redirects, `select_related`/`prefetch_related`,
  lazy-loaded images, SEO meta tags, ARIA labels, hashed/compressed static assets.
- **Tests**: 15 automated tests covering auth, job search, applications and employer flows.

## Quick start (local)

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows  (use: source .venv/bin/activate on macOS/Linux)

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install Node deps (for Tailwind) — one time
npm install

# 4. Build the CSS (or run `npm run watch:css` during development)
npm run build:css

# 5. Configure environment variables
cp .env.example .env
#   edit .env and set a strong SECRET_KEY (generate one with the command below)

# 6. Run migrations + create your admin account
python manage.py migrate
python manage.py createsuperuser

# 7. (Optional) Load SAMPLE data to preview the UI
python manage.py seed_sample

# 8. Start the dev server
python manage.py runserver
```

Open <http://127.0.0.1:8000/> — admin at <http://127.0.0.1:8000/admin/>.

Generate a secret key:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Project layout

```
config/            Django settings, URLs, WSGI
accounts/          Custom User model, registration/login, seeker & employer profiles
jobs/              Company, Job, Application, SavedJob models + views + forms + filters
templates/         Base layout, partials (icons, job card, pagination), and all pages
static/            Tailwind source + built CSS, JS, favicon, logo
jobs/management/   seed_sample management command (clearly-marked sample data)
```

## CSS / Tailwind — why a build step?

We compile Tailwind with the official CLI into a **single minified stylesheet**
(`static/css/tailwind.css`) instead of using the CDN. Reasons:

- The CDN JIT-compiles CSS **in the browser at runtime** → slower first paint and extra JS.
- A pre-built file is ~10–20 KB, cached, and served gzipped/brotli by WhiteNoise → far faster.
- No external JS dependency; works offline; better for SEO and privacy.

To rebuild after editing `input.css` or templates: `npm run build:css`.

## Environment variables (production)

| Variable               | Purpose                                          |
|------------------------|--------------------------------------------------|
| `SECRET_KEY`           | Django secret key (never commit)                 |
| `DEBUG`                | `False` in production                            |
| `ALLOWED_HOSTS`        | Comma list, e.g. `www.resuma.pk,resuma.pk`       |
| `CSRF_TRUSTED_ORIGINS` | `https://www.resuma.pk,https://resuma.pk`        |
| `DATABASE_URL`         | Full PostgreSQL URL (psycopg v3)                 |
| `EMAIL_*`              | SMTP credentials for application notifications    |

## Deploying

### Option A — Vercel (serverless)

1. `vercel.json` + `vercel-build` hook handle the build (Tailwind → collectstatic → migrate).
2. Import the repo in Vercel, set the environment variables above.
3. **Use an external Postgres** (Neon / Supabase free tier) and set `DATABASE_URL` —
   Vercel's filesystem is ephemeral, so SQLite **will not persist** and uploaded files
   (logos/resumes) need external object storage (Cloudflare R2 / S3).
4. `vercel deploy --prod`

### Option B — Render / Railway (recommended)

For a real production database, persistent disk and simpler Postgres, use Render or Railway:

- `render.example.yaml` + `Procfile.example` + `build.sh` are provided as a ready-to-use template.
- On Render: create a Web Service from the repo, add a Postgres instance, and it auto-wires `DATABASE_URL`.
- `gunicorn config.wsgi:application` is the entrypoint.

> Both platforms auto-detect `requirements.txt` and `runtime.txt`.

## Testing

```bash
python manage.py test
```

## Notes for production

- Uploaded media does not persist on serverless platforms; wire `DEFAULT_FILE_STORAGE`
  to S3/R2 (e.g. via `django-storages`) before accepting real uploads.
- Set `SECURE_SSL_REDIRECT` is enabled automatically when `DEBUG=False`.
- Replace the `(Sample)` companies/jobs from `seed_sample` with real data before launch.

## License

MIT — see repository. Built with care in Pakistan.
