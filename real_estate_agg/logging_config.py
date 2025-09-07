import logging
import smtplib
import structlog
from email.message import EmailMessage
from config import settings

class EmailNotificationHandler(logging.Handler):
    """
    A logging handler that sends an email notification for critical errors.
    """
    def emit(self, record):
        if not all([settings.EMAIL_HOST, settings.EMAIL_PORT, settings.EMAIL_USER, settings.EMAIL_PASS, settings.EMAIL_FROM, settings.EMAIL_TO]):
            return # Don't send email if not configured

        try:
            msg = EmailMessage()
            msg.set_content(self.format(record))
            msg['Subject'] = f"CRITICAL ERROR in Scraper Application"
            msg['From'] = settings.EMAIL_FROM
            msg['To'] = settings.EMAIL_TO

            with smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
                server.login(settings.EMAIL_USER, settings.EMAIL_PASS)
                server.send_message(msg)
        except Exception as e:
            # Avoid crashing the logger itself
            print(f"Failed to send error notification email: {e}")


def setup_logging():
    """
    Configures structured logging for the application.
    """
    # Configure standard logging to catch logs from other libraries
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=[logging.StreamHandler()],
    )

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Setup email handler for critical errors
    if all([settings.EMAIL_HOST, settings.EMAIL_PORT, settings.EMAIL_USER, settings.EMAIL_PASS, settings.EMAIL_FROM, settings.EMAIL_TO]):
        email_handler = EmailNotificationHandler()
        email_handler.setLevel(logging.CRITICAL)

        # Get the root logger and add the email handler
        root_logger = logging.getLogger()
        root_logger.addHandler(email_handler)

    return structlog.get_logger("real_estate_scraper")
