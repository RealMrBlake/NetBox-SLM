from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django_filters import CharFilter, DateFilter, ModelMultipleChoiceFilter, MultipleChoiceFilter, NumberFilter

from dcim.models import Device, Manufacturer
from netbox.filtersets import NetBoxModelFilterSet
from netbox_slm.models import (
    SoftwareProduct,
    SoftwareProductVersion,
    SoftwareProductInstallation,
    SoftwareLicense,
    SoftwareReleaseTypes,
    Certificate,
    CertificateTypes,
    RenewalIntervalUnits,
)
from virtualization.models import Cluster, VirtualMachine
from tenancy.models import Tenant, TenantGroup


class SoftwareProductFilterSet(NetBoxModelFilterSet):
    """Filter capabilities for SoftwareProduct instances."""

    name = CharFilter(lookup_expr="icontains")
    description = CharFilter(lookup_expr="icontains")

    manufacturer_id = ModelMultipleChoiceFilter(queryset=Manufacturer.objects.all())

    class Meta:
        model = SoftwareProduct
        fields = tuple()

    def search(self, queryset, name, value):
        """Perform the filtered search."""
        if not value.strip():
            return queryset
        qs_filter = (
            Q(name__icontains=value)
            | Q(description__icontains=value)
            | Q(manufacturer__name__icontains=value)
            | Q(comments__icontains=value)
        )
        return queryset.filter(qs_filter)


class SoftwareProductVersionFilterSet(NetBoxModelFilterSet):
    """Filter capabilities for SoftwareProductVersion instances."""

    name = CharFilter(lookup_expr="icontains")
    description = CharFilter(lookup_expr="icontains")
    filename = CharFilter(lookup_expr="icontains")

    release_type = MultipleChoiceFilter(choices=SoftwareReleaseTypes.choices)

    manufacturer_id = ModelMultipleChoiceFilter(
        field_name="software_product__manufacturer",
        queryset=Manufacturer.objects.all(),
    )

    software_product_id = ModelMultipleChoiceFilter(
        queryset=SoftwareProduct.objects.all(),
        label=_("Software Product"),
    )

    class Meta:
        model = SoftwareProductVersion
        fields = tuple()

    def search(self, queryset, name, value):
        """Perform the filtered search."""
        if not value.strip():
            return queryset
        qs_filter = (
            Q(name__icontains=value)
            | Q(description__icontains=value)
            | Q(software_product__name__icontains=value)
            | Q(software_product__manufacturer__name__icontains=value)
            | Q(comments__icontains=value)
        )
        return queryset.filter(qs_filter)


class SoftwareProductInstallationFilterSet(NetBoxModelFilterSet):
    """Filter capabilities for SoftwareProductInstallation instances."""

    device_id = ModelMultipleChoiceFilter(queryset=Device.objects.all())
    virtualmachine_id = ModelMultipleChoiceFilter(
        queryset=VirtualMachine.objects.all(),
        label=_("Virtual Machine"),
    )
    cluster_id = ModelMultipleChoiceFilter(queryset=Cluster.objects.all())
    software_product_id = ModelMultipleChoiceFilter(
        queryset=SoftwareProduct.objects.all(),
        label=_("Software Product"),
    )
    version_id = ModelMultipleChoiceFilter(queryset=SoftwareProductVersion.objects.all())

    class Meta:
        model = SoftwareProductInstallation
        fields = tuple()

    def search(self, queryset, name, value):
        """Perform the filtered search."""
        if not value.strip():
            return queryset
        qs_filter = (
            Q(software_product__name__icontains=value)
            | Q(software_product__manufacturer__name__icontains=value)
            | Q(version__name__icontains=value)
            | Q(comments__icontains=value)
        )
        return queryset.filter(qs_filter)


class SoftwareLicenseFilterSet(NetBoxModelFilterSet):
    """Filter capabilities for SoftwareLicense instances."""

    name = CharFilter(lookup_expr="icontains")
    description = CharFilter(lookup_expr="icontains")
    type = CharFilter(lookup_expr="icontains")
    spdx_expression = CharFilter(lookup_expr="icontains", label=_("SPDX expression"))
    stored_location = CharFilter(lookup_expr="icontains")
    renewal_interval = NumberFilter()
    renewal_interval_unit = MultipleChoiceFilter(choices=RenewalIntervalUnits.choices)

    software_product_id = ModelMultipleChoiceFilter(
        queryset=SoftwareProduct.objects.all(),
        label=_("Software Product"),
    )
    version_id = ModelMultipleChoiceFilter(queryset=SoftwareProductVersion.objects.all())
    installation_id = ModelMultipleChoiceFilter(queryset=SoftwareProductInstallation.objects.all())
    tenant_group_id = ModelMultipleChoiceFilter(queryset=TenantGroup.objects.all(), label=_("Tenant Group"))
    tenant_id = ModelMultipleChoiceFilter(queryset=Tenant.objects.all(), label=_("Tenant"))

    class Meta:
        model = SoftwareLicense
        fields = ("support", "lifetime", "expiration_notifications_enabled", "email_notifications")

    def search(self, queryset, name, value):
        """Perform the filtered search."""
        if not value.strip():
            return queryset
        qs_filter = (
            Q(name__icontains=value)
            | Q(description__icontains=value)
            | Q(software_product__name__icontains=value)
            | Q(version__name__icontains=value)
            | Q(installation__device__name__icontains=value)
            | Q(installation__virtualmachine__name__icontains=value)
            | Q(installation__cluster__name__icontains=value)
            | Q(tenant_group__name__icontains=value)
            | Q(tenant__name__icontains=value)
            | Q(comments__icontains=value)
        )
        return queryset.filter(qs_filter)


class CertificateFilterSet(NetBoxModelFilterSet):
    """Filter capabilities for Certificate instances."""

    name = CharFilter(lookup_expr="icontains")
    description = CharFilter(lookup_expr="icontains")
    type = MultipleChoiceFilter(choices=CertificateTypes.choices)
    common_name = CharFilter(lookup_expr="icontains")
    issuer = CharFilter(lookup_expr="icontains")
    serial_number = CharFilter(lookup_expr="icontains")
    expiration_date__lte = DateFilter(field_name="expiration_date", lookup_expr="lte")
    expiration_date__gte = DateFilter(field_name="expiration_date", lookup_expr="gte")

    software_product_id = ModelMultipleChoiceFilter(
        queryset=SoftwareProduct.objects.all(),
        label=_("Software Product"),
    )
    installation_id = ModelMultipleChoiceFilter(queryset=SoftwareProductInstallation.objects.all())
    device_id = ModelMultipleChoiceFilter(queryset=Device.objects.all())
    virtualmachine_id = ModelMultipleChoiceFilter(queryset=VirtualMachine.objects.all(), label=_("Virtual Machine"))
    tenant_group_id = ModelMultipleChoiceFilter(queryset=TenantGroup.objects.all(), label=_("Tenant Group"))
    tenant_id = ModelMultipleChoiceFilter(queryset=Tenant.objects.all(), label=_("Tenant"))

    class Meta:
        model = Certificate
        fields = ("auto_renewal", "expiration_notifications_enabled", "email_notifications")

    def search(self, queryset, name, value):
        """Perform the filtered search."""
        if not value.strip():
            return queryset
        qs_filter = (
            Q(name__icontains=value)
            | Q(description__icontains=value)
            | Q(common_name__icontains=value)
            | Q(subject_alternative_names__icontains=value)
            | Q(issuer__icontains=value)
            | Q(serial_number__icontains=value)
            | Q(fingerprint__icontains=value)
            | Q(device__name__icontains=value)
            | Q(virtualmachine__name__icontains=value)
            | Q(tenant__name__icontains=value)
            | Q(comments__icontains=value)
        )
        return queryset.filter(qs_filter)
