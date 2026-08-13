#!/usr/bin/env bash
set -o errexit
echo "→ Installing Python dependencies"
pip install -r requirements.txt
echo "→ Building Tailwind CSS"
npm install
npm run build:css
echo "→ Collecting static files"
python manage.py collectstatic --noinput
echo "→ Running migrations"
python manage.py migrate --noinput
echo "✓ Build complete"
