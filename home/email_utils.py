from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from django.contrib.sites.shortcuts import get_current_site
from django.utils import timezone
from django.templatetags.static import static
from django.conf import settings

import logging
logger = logging.getLogger(__name__)

def send_transfer_email(subject, template_name, context, recipient, connection=None):
    """
    Helper function to send individual transfer-related emails
    """
    try:
        # Render HTML message
        html_message = render_to_string(template_name, context)
        
        # Create email message
        email = EmailMultiAlternatives(
            subject=subject,
            body='Please enable HTML to view this email',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient],
            connection=connection
        )
        
        # Attach HTML version
        email.attach_alternative(html_message, "text/html")
        
        # Send email
        email.send()
        logger.info(f"Email sent successfully to {recipient}")
        
    except Exception as e:
        logger.error(f"Failed to send email to {recipient}: {str(e)}", exc_info=True)
        raise
