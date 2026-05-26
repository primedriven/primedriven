from uuid import uuid4

from django.conf import settings
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

EMAIL_ADMIN = settings.DEFAULT_FROM_EMAIL


def gen_random_ids():
    code = str(uuid4()).replace(" ", "-").upper()[:8]
    return code


# utils/email.py

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings


def send_html_email(
    subject,
    receiver_email,
    template_name,
    context=None,
    from_email=None,
):
    """
    Send HTML email with plain text fallback.

    Args:
        subject (str): Email subject
        receiver_email (str | list): Receiver email(s)
        template_name (str): HTML template path
        context (dict): Template context
        from_email (str): Optional sender email
    """

    try:
        context = context or {}

        # Render HTML template
        html_message = render_to_string(template_name, context)

        # Create plain text version
        plain_message = strip_tags(html_message)

        # Default sender
        from_email = from_email or (f"Prime Driven Ev <{settings.DEFAULT_FROM_EMAIL}>")

        try:
            validate_email(receiver_email)
        except ValidationError:
            return {"success": False, "message": "Invalid email address"}

        # Convert single email to list
        if isinstance(receiver_email, str):
            receiver_email = [receiver_email]

        # Create email
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=from_email,
            to=receiver_email,
        )

        # Attach HTML version
        email.attach_alternative(html_message, "text/html")

        # Send email
        email.send(fail_silently=False)

        return {
            "success": True,
            "message": "Email sent successfully",
        }

    except Exception as e:
        return {
            "success": False,
            "message": str(e),
        }
