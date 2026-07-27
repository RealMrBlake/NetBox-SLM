from rest_framework import serializers
from rest_framework.serializers import SerializerMethodField, HyperlinkedIdentityField
from django.utils.translation import gettext_lazy as _

from netbox.api.serializers import NetBoxModelSerializer
from netbox_slm.models import SoftwareProduct, SoftwareProductVersion, SoftwareProductInstallation, SoftwareLicense


class SoftwareLicenseSerializer(NetBoxModelSerializer):
    display = SerializerMethodField()
    url = HyperlinkedIdentityField(view_name="plugins-api:netbox_slm-api:softwarelicense-detail")

    class Meta:
        model = SoftwareLicense
        fields = (
            "id",
            "display",
            "url",
            "name",
            "description",
            "type",
            "spdx_expression",
            "stored_location",
            "stored_location_url",
            "start_date",
            "expiration_date",
            "lifetime",
            "renewal_interval",
            "renewal_interval_unit",
            "support",
            "license_amount",
            "license_file",
            "license_key",
            "provider_portal_url",
            "software_product",
            "version",
            "installation",
            "tenant_group",
            "tenant",
            "tags",
            "comments",
            "custom_field_data",
            "created",
            "last_updated",
        )
        brief_fields = ("id", "display", "url", "name", "description")

    def get_display(self, obj):
        return f"{obj}"

    def validate(self, attrs):
        tenant_group = attrs.get("tenant_group", getattr(self.instance, "tenant_group", None))
        tenant = attrs.get("tenant", getattr(self.instance, "tenant", None))
        if tenant_group and tenant and tenant.group_id != tenant_group.pk:
            raise serializers.ValidationError(
                {"tenant": _("The selected tenant does not belong to the selected tenant group.")}
            )
        lifetime = attrs.get("lifetime", getattr(self.instance, "lifetime", False))
        renewal_interval = attrs.get("renewal_interval", getattr(self.instance, "renewal_interval", None))
        renewal_interval_unit = attrs.get(
            "renewal_interval_unit", getattr(self.instance, "renewal_interval_unit", "")
        )
        expiration_date = attrs.get("expiration_date", getattr(self.instance, "expiration_date", None))
        if bool(renewal_interval) != bool(renewal_interval_unit):
            raise serializers.ValidationError(
                {"renewal_interval": _("Renewal interval and unit must be specified together.")}
            )
        if lifetime and (renewal_interval or renewal_interval_unit or expiration_date):
            raise serializers.ValidationError(
                {"lifetime": _("A lifetime license cannot have a renewal interval or expiration date.")}
            )
        return attrs


class SoftwareProductSerializer(NetBoxModelSerializer):
    display = SerializerMethodField()
    url = HyperlinkedIdentityField(view_name="plugins-api:netbox_slm-api:softwareproduct-detail")

    class Meta:
        model = SoftwareProduct
        fields = (
            "id",
            "display",
            "url",
            "name",
            "description",
            "manufacturer",
            "description",
            "tags",
            "comments",
            "custom_field_data",
            "created",
            "last_updated",
        )
        brief_fields = ("id", "display", "url", "name", "description")

    def get_display(self, obj):
        return f"{obj}"


class SoftwareProductInstallationSerializer(NetBoxModelSerializer):
    display = SerializerMethodField()
    url = HyperlinkedIdentityField(view_name="plugins-api:netbox_slm-api:softwareproductinstallation-detail")

    class Meta:
        model = SoftwareProductInstallation
        fields = (
            "id",
            "display",
            "url",
            "device",
            "virtualmachine",
            "cluster",
            "software_product",
            "version",
            "tags",
            "comments",
            "custom_field_data",
            "created",
            "last_updated",
        )
        brief_fields = ("id", "display", "url")

    def get_display(self, obj):
        return f"{obj}"


class SoftwareProductVersionSerializer(NetBoxModelSerializer):
    display = SerializerMethodField()
    url = HyperlinkedIdentityField(view_name="plugins-api:netbox_slm-api:softwareproductversion-detail")

    class Meta:
        model = SoftwareProductVersion
        fields = (
            "id",
            "display",
            "url",
            "name",
            "description",
            "release_date",
            "documentation_url",
            "end_of_support",
            "filename",
            "file_checksum",
            "file_link",
            "release_type",
            "software_product",
            "tags",
            "comments",
            "custom_field_data",
            "created",
            "last_updated",
        )
        brief_fields = ("id", "display", "url", "name", "description")

    def get_display(self, obj):
        return f"{obj}"
