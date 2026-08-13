from django.conf import settings


def site_defaults(request):
    return {
        "site_name": settings.SITE_NAME,
        "site_tagline": settings.SITE_TAGLINE,
        "site_email": settings.SITE_EMAIL,
        "site_phone": settings.SITE_PHONE,
    }