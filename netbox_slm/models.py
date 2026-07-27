from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from license_expression import Licensing, get_spdx_licensing

from netbox.models import NetBoxModel
from utilities.querysets import RestrictedQuerySet
from utilities.validators import EnhancedURLValidator

spdx_licensing: Licensing = get_spdx_licensing()


class LaxURLField(models.URLField):
    """
    NetBox Custom Field approach, based on utilities.forms.fields.LaxURLField
    Overriding default_validators is needed, as they are always added
    """

    default_validators = [EnhancedURLValidator()]


class SoftwareProduct(NetBoxModel):
    name = models.CharField(_("name"), max_length=128)
    comments = models.TextField(_("comments"), blank=True)

    description = models.CharField(_("description"), max_length=255, null=True, blank=True)
    manufacturer = models.ForeignKey(
        to="dcim.Manufacturer", verbose_name=_("manufacturer"), on_delete=models.PROTECT, null=True, blank=True
    )

    objects = RestrictedQuerySet.as_manager()

    class Meta:
        verbose_name = _("software product")
        verbose_name_plural = _("software products")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("plugins:netbox_slm:softwareproduct", kwargs={"pk": self.pk})

    def get_installation_count(self):
        count = SoftwareProductInstallation.objects.filter(software_product_id=self.pk).count()
        search_target = reverse(
            "plugins:netbox_slm:softwareproductinstallation_list", query={"software_product_id": self.pk}
        )
        return format_html("<a href='{}'>{}</a>", search_target, count) if count else "0"


class SoftwareReleaseTypes(models.TextChoices):
    ALPHA = "A", _("Alpha")
    BETA = "B", _("Beta")
    RELEASE_CANDIDATE = "RC", _("Release candidate")
    STABLE = "S", _("Stable release")


class RenewalIntervalUnits(models.TextChoices):
    DAYS = "days", _("Days")
    MONTHS = "months", _("Months")
    YEARS = "years", _("Years")


class SoftwareProductVersion(NetBoxModel):
    name = models.CharField(_("name"), max_length=64)
    comments = models.TextField(_("comments"), blank=True)

    description = models.CharField(_("description"), max_length=255, null=True, blank=True)
    release_date = models.DateField(_("release date"), null=True, blank=True)
    documentation_url = LaxURLField(_("documentation URL"), max_length=1024, null=True, blank=True)
    end_of_support = models.DateField(_("end of support"), null=True, blank=True)
    filename = models.CharField(_("filename"), max_length=64, null=True, blank=True)
    file_checksum = models.CharField(_("file checksum"), max_length=128, null=True, blank=True)
    file_link = LaxURLField(_("file link"), max_length=1024, null=True, blank=True)

    release_type = models.CharField(
        _("release type"),
        max_length=3,
        choices=SoftwareReleaseTypes.choices,
        default=SoftwareReleaseTypes.STABLE,
    )

    software_product = models.ForeignKey(
        to="netbox_slm.SoftwareProduct",
        verbose_name=_("software product"),
        on_delete=models.PROTECT,
    )

    objects = RestrictedQuerySet.as_manager()

    class Meta:
        verbose_name = _("software product version")
        verbose_name_plural = _("software product versions")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("plugins:netbox_slm:softwareproductversion", kwargs={"pk": self.pk})

    def get_installation_count(self):
        count = SoftwareProductInstallation.objects.filter(version_id=self.pk).count()
        search_target = reverse("plugins:netbox_slm:softwareproductinstallation_list", query={"version_id": self.pk})
        return format_html("<a href='{}'>{}</a>", search_target, count) if count else "0"


class SoftwareProductInstallation(NetBoxModel):
    comments = models.TextField(_("comments"), blank=True)

    device = models.ForeignKey(
        to="dcim.Device", verbose_name=_("device"), on_delete=models.PROTECT, null=True, blank=True
    )
    virtualmachine = models.ForeignKey(
        to="virtualization.VirtualMachine",
        verbose_name=_("virtual machine"),
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    cluster = models.ForeignKey(
        to="virtualization.Cluster", verbose_name=_("cluster"), on_delete=models.PROTECT, null=True, blank=True
    )
    software_product = models.ForeignKey(
        to="netbox_slm.SoftwareProduct", verbose_name=_("software product"), on_delete=models.PROTECT
    )
    version = models.ForeignKey(
        to="netbox_slm.SoftwareProductVersion", verbose_name=_("version"), on_delete=models.PROTECT
    )

    objects = RestrictedQuerySet.as_manager()

    def __str__(self):
        return f"{self.pk} ({self.platform})"

    class Meta:
        verbose_name = _("software product installation")
        verbose_name_plural = _("software product installations")
        constraints = [
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_platform",
                condition=(
                    models.Q(device__isnull=False, virtualmachine__isnull=True, cluster__isnull=True)
                    | models.Q(device__isnull=True, virtualmachine__isnull=False, cluster__isnull=True)
                    | models.Q(device__isnull=True, virtualmachine__isnull=True, cluster__isnull=False)
                ),
                violation_error_message=_("Installation requires exactly one platform destination."),
            )
        ]

    def get_absolute_url(self):
        return reverse("plugins:netbox_slm:softwareproductinstallation", kwargs={"pk": self.pk})

    @property
    def platform(self):
        return self.device or self.virtualmachine or self.cluster

    def render_type(self):
        if self.device:
            return "device"
        if self.virtualmachine:
            return "virtualmachine"
        return "cluster"


def spdx_license_names():
    names = [(item[0], item[0]) for item in spdx_licensing.known_symbols.items() if not item[1].is_exception]
    names.sort()
    names.insert(0, ("", "---------"))  # set default value
    return names


def validate_spdx_expression(value):
    expression_info = spdx_licensing.validate(value)
    if expression_info.errors:
        raise ValidationError(_("%(value)s is not a known SPDX license expression") % {"value": value})


class SoftwareLicense(NetBoxModel):
    name = models.CharField(_("name"), max_length=128)
    comments = models.TextField(_("comments"), blank=True)

    description = models.CharField(_("description"), max_length=255, null=True, blank=True)
    type = models.CharField(_("type"), max_length=128, blank=True)
    spdx_expression = models.CharField(
        _("SPDX expression"), max_length=64, null=True, blank=True, validators=[validate_spdx_expression]
    )
    stored_location = models.CharField(_("stored location"), max_length=255, null=True, blank=True)
    stored_location_url = LaxURLField(_("stored location URL"), max_length=1024, null=True, blank=True)
    start_date = models.DateField(_("start date"), null=True, blank=True)
    expiration_date = models.DateField(_("expiration date"), null=True, blank=True)
    support = models.BooleanField(_("support"), default=None, null=True, blank=True)
    license_amount = models.PositiveIntegerField(_("license amount"), default=None, null=True, blank=True)
    lifetime = models.BooleanField(_("lifetime license"), default=False)
    renewal_interval = models.PositiveIntegerField(
        _("renewal interval"), null=True, blank=True, validators=[MinValueValidator(1)]
    )
    renewal_interval_unit = models.CharField(
        _("renewal interval unit"), max_length=8, choices=RenewalIntervalUnits.choices, blank=True
    )
    license_file = models.FileField(_("license file"), upload_to="netbox_slm/licenses/", null=True, blank=True)
    license_key = models.TextField(_("license key"), blank=True)
    provider_portal_url = LaxURLField(_("provider portal URL"), max_length=1024, null=True, blank=True)

    software_product = models.ForeignKey(
        to="netbox_slm.SoftwareProduct", verbose_name=_("software product"), on_delete=models.PROTECT
    )
    version = models.ForeignKey(
        to="netbox_slm.SoftwareProductVersion",
        verbose_name=_("version"),
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    installation = models.ForeignKey(
        to="netbox_slm.SoftwareProductInstallation",
        verbose_name=_("installation"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    tenant_group = models.ForeignKey(
        to="tenancy.TenantGroup",
        verbose_name=_("tenant group"),
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="software_licenses",
    )
    tenant = models.ForeignKey(
        to="tenancy.Tenant",
        verbose_name=_("tenant"),
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="software_licenses",
    )

    objects = RestrictedQuerySet.as_manager()

    class Meta:
        verbose_name = _("software license")
        verbose_name_plural = _("software licenses")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("plugins:netbox_slm:softwarelicense", kwargs={"pk": self.pk})

    def clean(self):
        super().clean()
        if self.tenant_group and self.tenant and self.tenant.group_id != self.tenant_group_id:
            raise ValidationError(
                {"tenant": _("The selected tenant does not belong to the selected tenant group.")}
            )
        if bool(self.renewal_interval) != bool(self.renewal_interval_unit):
            raise ValidationError(
                {"renewal_interval": _("Renewal interval and unit must be specified together.")}
            )
        if self.lifetime and (self.renewal_interval or self.renewal_interval_unit or self.expiration_date):
            raise ValidationError(
                {"lifetime": _("A lifetime license cannot have a renewal interval or expiration date.")}
            )

    @property
    def stored_location_txt(self):
        if self.stored_location_url and not self.stored_location:
            return _("Link")
        return self.stored_location
