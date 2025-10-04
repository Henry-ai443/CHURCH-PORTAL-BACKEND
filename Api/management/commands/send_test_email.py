from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    help = "Send a test email to verify email settings"

    def handle(self, *args, **kwargs):
        subject = "Test Email from Django"
        message = "This is a test email sent from Django to verify email configuration."
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [settings.EMAIL_HOST_USER]  # You can change this to any email you want to test to

        try:
            send_mail(subject, message, from_email, recipient_list)
            self.stdout.write(self.style.SUCCESS("Test email sent successfully!"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Failed to send test email: {e}"))
