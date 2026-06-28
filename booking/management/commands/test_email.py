from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
import sys

class Command(BaseCommand):
    help = 'Verify email settings by sending a test email to a specified address.'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Recipient email address for the test')

    def handle(self, *args, **options):
        recipient = options['email']
        self.stdout.write(self.style.MIGRATE_HEADING("=== TravelEase Email Diagnostics ==="))
        self.stdout.write(f"EMAIL_BACKEND      : {settings.EMAIL_BACKEND}")
        self.stdout.write(f"EMAIL_HOST         : {settings.EMAIL_HOST}")
        self.stdout.write(f"EMAIL_PORT         : {settings.EMAIL_PORT}")
        self.stdout.write(f"EMAIL_USE_TLS      : {settings.EMAIL_USE_TLS}")
        self.stdout.write(f"EMAIL_HOST_USER    : {settings.EMAIL_HOST_USER}")
        self.stdout.write(f"DEFAULT_FROM_EMAIL : {settings.DEFAULT_FROM_EMAIL}")
        
        # Obfuscate password for security when displaying
        pwd = settings.EMAIL_HOST_PASSWORD
        pwd_display = f"{pwd[:2]}...{pwd[-2:]} (Length: {len(pwd)})" if pwd else "None/Empty"
        self.stdout.write(f"EMAIL_HOST_PASSWORD: {pwd_display}")
        self.stdout.write("=====================================\n")

        self.stdout.write(f"Attempting to send test email to {recipient}...")
        try:
            sent_count = send_mail(
                subject='TravelEase - Test Email Connection',
                message=(
                    'Hello!\n\n'
                    'This is a diagnostic test email from the TravelEase Django application.\n'
                    'If you received this, your email configuration is working perfectly!\n\n'
                    'Regards,\n'
                    'TravelEase Diagnostics'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                fail_silently=False,
            )
            if sent_count > 0:
                self.stdout.write(self.style.SUCCESS(f"Success! Test email sent successfully to {recipient}."))
            else:
                self.stdout.write(self.style.WARNING("Warning: send_mail returned 0 (no email sent)."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error: Email sending failed! Detail: {str(e)}"))
            self.stdout.write(self.style.WARNING(
                "\nTroubleshooting tips:\n"
                "1. If using Gmail, make sure you generated an 'App Password', NOT your primary password.\n"
                "2. Ensure EMAIL_HOST_USER matches your Gmail address exactly.\n"
                "3. If credentials are empty and DEBUG=True, Django falls back to the console backend.\n"
                "4. Check your network connection. Replit might sometimes block external SMTP ports on free tiers or require TLS/SSL settings config."
            ))
            sys.exit(1)
