from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.translation import gettext as _

from core.choices import JobIntervalChoices
from extras.models import Notification
from netbox.jobs import JobRunner, system_job

from netbox_slm.events import LICENSE_EXPIRING
from netbox_slm.models import SoftwareLicense, SoftwareLicenseNotificationLog


@system_job(interval=JobIntervalChoices.INTERVAL_DAILY)
class LicenseExpirationNotificationJob(JobRunner):
    class Meta:
        name = "Software License Expiration Notifications"

    def run(self, *args, **kwargs):
        today = timezone.localdate()
        licenses = SoftwareLicense.objects.filter(
            expiration_notifications_enabled=True,
            lifetime=False,
            expiration_date__gte=today,
        ).prefetch_related("subscriptions__user")

        for license in licenses:
            due_dates = [date for date in license.get_notification_dates() if date <= today]
            if not due_dates:
                continue

            for subscription in license.subscriptions.all():
                user = subscription.user
                if not user.is_active:
                    continue
                # If notifications were enabled late, send only the most recent reminder instead of one per elapsed
                # interval. Normally this still produces one reminder at each configured threshold.
                self._notify(license, user, max(due_dates))

    def _notify(self, license, user, notification_date):
        log, _ = SoftwareLicenseNotificationLog.objects.get_or_create(
            license=license,
            user=user,
            expiration_date=license.expiration_date,
            notification_date=notification_date,
        )
        now = timezone.now()

        if log.netbox_sent_at is None:
            object_type = ContentType.objects.get_for_model(license)
            Notification.objects.update_or_create(
                object_type=object_type,
                object_id=license.pk,
                user=user,
                defaults={
                    "object_repr": Notification.get_object_repr(license),
                    "event_type": LICENSE_EXPIRING,
                    "read": None,
                },
            )
            log.netbox_sent_at = now
            log.save(update_fields=("netbox_sent_at",))
            self.logger.info(f"Created NetBox expiration notification for license {license.pk} and user {user}")

        if license.email_notifications and user.email and log.email_sent_at is None:
            subject = _("License %(license)s expires on %(date)s") % {
                "license": license,
                "date": license.expiration_date,
            }
            body = _(
                "The software license '%(license)s' for '%(product)s' expires on %(date)s."
            ) % {
                "license": license,
                "product": license.software_product,
                "date": license.expiration_date,
            }
            if license.tenant:
                body += "\n" + _("Tenant: %(tenant)s") % {"tenant": license.tenant}
            if license.provider_portal_url:
                body += "\n" + _("Provider portal: %(url)s") % {"url": license.provider_portal_url}

            try:
                send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
            except Exception:
                self.logger.exception(f"Failed to send expiration email for license {license.pk} to user {user}")
            else:
                log.email_sent_at = now
                log.save(update_fields=("email_sent_at",))
                self.logger.info(f"Sent expiration email for license {license.pk} to user {user}")
