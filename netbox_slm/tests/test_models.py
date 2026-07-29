from datetime import date, timedelta
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.test import override_settings
from django.utils import timezone
from django.utils.translation import gettext, override
from extras.models import Notification, Subscription

from netbox_slm.forms import SoftwareLicenseForm, SoftwareProductInstallationForm
from netbox_slm.jobs import LicenseExpirationNotificationJob
from netbox_slm.models import (
    NotificationIntervalUnits,
    RenewalIntervalUnits,
    SoftwareLicense,
    SoftwareLicenseNotificationLog,
)
from tenancy.models import Tenant, TenantGroup

from .base import SlmBaseTestCase


class ModelTestCase(SlmBaseTestCase):
    """Test basic model functionality and custom overrides"""

    def test_model_name(self):
        self.assertEqual(self.p_name, str(self.software_product))
        self.assertEqual(self.v_name, str(self.software_product_version))
        self.assertTrue(str(self.software_product_installation)[0].isdigit())  # starts with PK
        self.assertEqual(self.l_name, str(self.software_license))

    def test_absolute_url(self):
        self.assertEqual(
            f"/plugins/slm/software-products/{self.software_product.pk}/", self.software_product.get_absolute_url()
        )
        self.assertEqual(
            f"/plugins/slm/versions/{self.software_product_version.pk}/",
            self.software_product_version.get_absolute_url(),
        )
        self.assertEqual(
            f"/plugins/slm/installations/{self.software_product_installation.pk}/",
            self.software_product_installation.get_absolute_url(),
        )
        self.assertEqual(f"/plugins/slm/licenses/{self.software_license.pk}/", self.software_license.get_absolute_url())

    def test_get_installation_count(self):
        self.assertEqual(
            f"<a href='/plugins/slm/installations/?software_product_id={self.software_product.pk}'>1</a>",
            self.software_product.get_installation_count(),
        )
        self.assertEqual(
            f"<a href='/plugins/slm/installations/?version_id={self.software_product_version.pk}'>1</a>",
            self.software_product_version.get_installation_count(),
        )

    def test_product_installation_methods(self):
        self.assertEqual("virtualmachine", self.software_product_installation.render_type())
        self.assertEqual(self.vm, self.software_product_installation.platform)

        self.software_product_installation.virtualmachine = None
        self.software_product_installation.device = self.device
        self.software_product_installation.save()
        self.assertEqual("device", self.software_product_installation.render_type())
        self.assertEqual(self.device, self.software_product_installation.platform)

        self.software_product_installation.device = None
        self.software_product_installation.cluster = self.cluster
        self.software_product_installation.save()
        self.assertEqual("cluster", self.software_product_installation.render_type())
        self.assertEqual(self.cluster, self.software_product_installation.platform)

    def test_installation_form_requires_exactly_one_platform_destination(self):
        base_data = {
            "software_product": self.software_product.pk,
            "version": self.software_product_version.pk,
        }

        no_destination_form = SoftwareProductInstallationForm(data=base_data)
        self.assertFalse(no_destination_form.is_valid())
        self.assertIn("Select exactly one platform destination", str(no_destination_form.non_field_errors()))

        one_destination_form = SoftwareProductInstallationForm(data={**base_data, "device": self.device.pk})
        self.assertTrue(one_destination_form.is_valid(), one_destination_form.errors)

        multiple_destinations_form = SoftwareProductInstallationForm(
            data={**base_data, "device": self.device.pk, "cluster": self.cluster.pk}
        )
        self.assertFalse(multiple_destinations_form.is_valid())
        self.assertIn("Select exactly one platform destination", str(multiple_destinations_form.non_field_errors()))

    def test_software_license_stored_location_txt(self):
        self.assertEqual("Link", self.software_license.stored_location_txt)

        self.software_license.stored_location = "GitHub"
        self.software_license.save()
        self.assertEqual("GitHub", self.software_license.stored_location_txt)

    def test_software_license_tenancy(self):
        self.assertEqual(self.tenant_group, self.software_license.tenant_group)
        self.assertEqual(self.tenant, self.software_license.tenant)

    def test_software_license_form_renders_tenancy_fields(self):
        form = SoftwareLicenseForm(instance=self.software_license)
        self.assertIn("tenant_group", form.fields)
        self.assertIn("tenant", form.fields)
        self.assertTrue(
            any("tenant_group" in fieldset.items and "tenant" in fieldset.items for fieldset in form.fieldsets)
        )

    def test_software_license_form_contains_renewal_and_credentials(self):
        form = SoftwareLicenseForm(instance=self.software_license)
        for field_name in (
            "lifetime",
            "renewal_interval",
            "renewal_interval_unit",
            "license_file",
            "license_key",
            "provider_portal_url",
        ):
            self.assertIn(field_name, form.fields)

    def test_software_license_accepts_optional_type_and_renewal_interval(self):
        license = SoftwareLicense(
            name="renewable license",
            software_product=self.software_product,
            renewal_interval=12,
            renewal_interval_unit=RenewalIntervalUnits.MONTHS,
        )
        license.full_clean()

    def test_software_license_requires_renewal_interval_and_unit_together(self):
        license = SoftwareLicense(
            name="invalid renewable license",
            software_product=self.software_product,
            renewal_interval=12,
        )
        with self.assertRaisesMessage(ValidationError, "must be specified together"):
            license.full_clean()

    def test_lifetime_license_rejects_expiration(self):
        license = SoftwareLicense(
            name="invalid lifetime license",
            software_product=self.software_product,
            lifetime=True,
            expiration_date="2030-01-01",
        )
        with self.assertRaisesMessage(ValidationError, "cannot have a renewal interval or expiration date"):
            license.full_clean()

    def test_license_notification_dates(self):
        license = SoftwareLicense(
            name="expiring license",
            software_product=self.software_product,
            expiration_date=date(2027, 3, 31),
            custom_notification_interval=6,
            custom_notification_interval_unit=NotificationIntervalUnits.MONTHS,
        )
        self.assertEqual(
            [date(2026, 9, 30), date(2027, 2, 28), date(2027, 3, 24)],
            license.get_notification_dates(),
        )

    @override_settings(SERVER_EMAIL="netbox@example.com", EMAIL_HOST_USER="smtp-user")
    @patch("netbox_slm.jobs.send_mail")
    def test_expiration_job_notifies_subscribers_on_every_run(self, send_mail):
        user = get_user_model().objects.create_user(
            username="license-recipient",
            email="recipient@example.com",
        )
        license = SoftwareLicense.objects.create(
            name="expiring subscribed license",
            software_product=self.software_product,
            expiration_date=timezone.localdate() + timedelta(days=1),
            default_notification_intervals=False,
            custom_notification_interval=1,
            custom_notification_interval_unit=NotificationIntervalUnits.DAYS,
            email_notifications=True,
        )
        Subscription.objects.create(
            user=user,
            object_type=ContentType.objects.get_for_model(license),
            object_id=license.pk,
        )
        runner = LicenseExpirationNotificationJob.__new__(LicenseExpirationNotificationJob)
        runner.logger = Mock()

        runner.run()
        runner.run()

        notification = Notification.objects.get(user=user, object_id=license.pk)
        self.assertIsInstance(str(notification.event), str)
        self.assertEqual(1, SoftwareLicenseNotificationLog.objects.filter(user=user, license=license).count())
        self.assertEqual(2, send_mail.call_count)
        self.assertEqual("netbox@example.com", send_mail.call_args.args[2])

    def test_german_translation(self):
        with override("de"):
            self.assertEqual("Softwarelizenz", gettext("Software License"))
            self.assertEqual("Mandantengruppe", gettext("Tenant Group"))
            self.assertEqual("Lizenzen", gettext("Licenses"))

    def test_software_license_rejects_tenant_from_other_group(self):
        other_group = TenantGroup.objects.create(name="other group", slug="other-group")
        other_tenant = Tenant.objects.create(name="other tenant", slug="other-tenant", group=other_group)
        self.software_license.tenant = other_tenant

        with self.assertRaisesMessage(ValidationError, "does not belong to the selected tenant group"):
            self.software_license.full_clean()
