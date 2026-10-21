from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.translation import gettext as _

from core.choices import JobIntervalChoices
from extras.models import Notification
from netbox.jobs import JobRunner, system_job

from netbox_slm.events import CERTIFICATE_EXPIRING, LICENSE_EXPIRING
from netbox_slm.models import (
    Certificate,
    CertificateNotificationLog,
    SoftwareLicense,
    SoftwareLicenseNotificationLog,
)


class ExpirationNotificationJob(JobRunner):
    """Shared reminder logic; subclasses define the model, log model, event type and email text."""

    model = None
    log_model = None
    log_object_field = None
    event_type = None

    def get_queryset(self, today):
        return self.model.objects.filter(
            expiration_notifications_enabled=True,
            expiration_date__gte=today,
        )

    def get_email(self, obj):
        raise NotImplementedError

    def run(self, *args, **kwargs):
        today = timezone.localdate()
        objects = self.get_queryset(today).prefetch_related("subscriptions__user")

        for obj in objects:
            due_dates = [date for date in obj.get_notification_dates() if date <= today]
            if not due_dates:
                continue

            for subscription in obj.subscriptions.all():
                user = subscription.user
                if not user.is_active:
                    continue
                # If notifications were enabled late, send only the most recent reminder instead of one per elapsed
                # interval. Normally this still produces one reminder at each configured threshold.
                self._notify(obj, user, max(due_dates))

    def _notify(self, obj, user, notification_date):
        log = self.log_model.objects.get_or_create(
            **{self.log_object_field: obj},
            user=user,
            expiration_date=obj.expiration_date,
            notification_date=notification_date,
        )[0]
        now = timezone.now()
        name = self.model._meta.model_name

        object_type = ContentType.objects.get_for_model(obj)
        Notification.objects.update_or_create(
            object_type=object_type,
            object_id=obj.pk,
            user=user,
            defaults={
                "created": now,
                "object_repr": Notification.get_object_repr(obj),
                "event_type": self.event_type,
                "read": None,
            },
        )
        log.netbox_sent_at = now
        log.save(update_fields=("netbox_sent_at",))
        self.logger.info(f"Created NetBox expiration notification for {name} {obj.pk} and user {user}")

        if obj.email_notifications and user.email:
            subject, body = self.get_email(obj)
            try:
                from_email = settings.SERVER_EMAIL or settings.EMAIL_HOST_USER
                send_mail(subject, body, from_email, [user.email], fail_silently=False)
            except Exception:
                self.logger.exception(f"Failed to send expiration email for {name} {obj.pk} to user {user}")
            else:
                log.email_sent_at = now
                log.save(update_fields=("email_sent_at",))
                self.logger.info(f"Sent expiration email for {name} {obj.pk} to user {user}")


@system_job(interval=JobIntervalChoices.INTERVAL_DAILY)
class LicenseExpirationNotificationJob(ExpirationNotificationJob):
    model = SoftwareLicense
    log_model = SoftwareLicenseNotificationLog
    log_object_field = "license"
    event_type = LICENSE_EXPIRING

    class Meta:
        name = "Software License Expiration Notifications"

    def get_queryset(self, today):
        return super().get_queryset(today).filter(lifetime=False)

    def get_email(self, license):
        subject = _("License %(license)s expires on %(date)s") % {
            "license": license,
            "date": license.expiration_date,
        }
        body = _("The software license '%(license)s' for '%(product)s' expires on %(date)s.") % {
            "license": license,
            "product": license.software_product,
            "date": license.expiration_date,
        }
        if license.tenant:
            body += "\n" + _("Tenant: %(tenant)s") % {"tenant": license.tenant}
        if license.provider_portal_url:
            body += "\n" + _("Provider portal: %(url)s") % {"url": license.provider_portal_url}
        return subject, body


@system_job(interval=JobIntervalChoices.INTERVAL_DAILY)
class CertificateExpirationNotificationJob(ExpirationNotificationJob):
    model = Certificate
    log_model = CertificateNotificationLog
    log_object_field = "certificate"
    event_type = CERTIFICATE_EXPIRING

    class Meta:
        name = "Certificate Expiration Notifications"

    def get_email(self, certificate):
        subject = _("Certificate %(certificate)s expires on %(date)s") % {
            "certificate": certificate,
            "date": certificate.expiration_date,
        }
        body = _("The certificate '%(certificate)s' expires on %(date)s.") % {
            "certificate": certificate,
            "date": certificate.expiration_date,
        }
        if certificate.common_name:
            body += "\n" + _("Common name: %(name)s") % {"name": certificate.common_name}
        if certificate.issuer:
            body += "\n" + _("Issuer: %(issuer)s") % {"issuer": certificate.issuer}
        if certificate.tenant:
            body += "\n" + _("Tenant: %(tenant)s") % {"tenant": certificate.tenant}
        if certificate.provider_portal_url:
            body += "\n" + _("Provider portal: %(url)s") % {"url": certificate.provider_portal_url}
        return subject, body
