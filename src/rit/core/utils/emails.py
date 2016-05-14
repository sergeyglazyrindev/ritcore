from wheezy.core.mail import MailMessage, SMTPClient

from rit.app.conf import settings

from rit.core.monkeypatches import patch_ssl

patch_ssl()


def send_email(subject, from_addr, to_addrs, html):
    if settings.INST_TYPE == 'dev':
        to_addrs = list(settings.DEBUG_EMAILS)
    message = MailMessage(
        subject=subject,
        from_addr=from_addr,
        to_addrs=to_addrs,
        content=html,
        content_type='text/html'
    )
    client = SMTPClient(
        host=settings.EMAIL_HOST,
        port=settings.EMAIL_PORT,
        username=settings.EMAIL_HOST_USER,
        password=settings.EMAIL_HOST_PASSWORD,
        use_tls=settings.EMAIL_USE_TLS
    )
    client.send(message)
