from django.core.exceptions import ValidationError
from django.utils.translation import gettext, override
from netbox_slm.forms import SoftwareLicenseForm
from netbox_slm.models import RenewalIntervalUnits, SoftwareLicense
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
