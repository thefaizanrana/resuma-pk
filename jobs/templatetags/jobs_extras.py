import hashlib

from django import template
from django.utils.safestring import mark_safe

register = template.Library()

PALETTE = [
    ("bg-forest-100", "text-forest-700"),
    ("bg-gold-200", "text-gold-700"),
    ("bg-ink-100", "text-ink-700"),
    ("bg-forest-700", "text-white"),
    ("bg-gold-500", "text-ink-950"),
    ("bg-ink-800", "text-white"),
]


@register.filter
def initials(value):
    parts = (value or "").split()
    return "".join(p[0] for p in parts[:2]).upper() or "?"


@register.filter
def avatar_classes(value):
    digest = hashlib.md5((value or "").encode()).hexdigest()
    bg, fg = PALETTE[int(digest[:2], 16) % len(PALETTE)]
    return f"{bg} {fg}"


@register.filter
def salary_short(job):
    if not job.salary_min and not job.salary_max:
        return "Not disclosed"
    if job.salary_min and job.salary_max:
        if job.salary_min == job.salary_max:
            low = f"Rs. {job.salary_min:,}"
            return low
        return f"Rs. {job.salary_min:,} – {job.salary_max:,}"
    low = job.salary_min or job.salary_max
    return f"{'From Rs.' if job.salary_min else 'Up to Rs.'} {low:,}"


@register.simple_tag
def company_logo(company, class_name="h-12 w-12 text-sm"):
    """SVG avatar with initials for a company (zero image weight)."""
    initials_text = company.name.split()
    letters = "".join(w[0] for w in initials_text[:2]).upper()
    digest = hashlib.md5(company.name.encode()).hexdigest()
    hues = [167, 43, 210, 280, 12, 90, 200, 320]
    hue = hues[int(digest[:2], 16) % len(hues)]
    return mark_safe(
        f'<span class="inline-flex {class_name} items-center justify-center rounded-xl font-bold select-none" '
        f'style="background:hsl({hue} 45% 92%);color:hsl({hue} 40% 30%);">{letters}</span>'
    )