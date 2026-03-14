from uuid import uuid4

from django.conf import settings


EMAIL_ADMIN = settings.DEFAULT_FROM_EMAIL


def gen_random_ids():
    code = str(uuid4()).replace(" ", "-").upper()[:8]
    return code
