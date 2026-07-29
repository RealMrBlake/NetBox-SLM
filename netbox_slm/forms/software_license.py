from django.forms import CharField, DateField, ChoiceField, IntegerField, NullBooleanField, Textarea
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm, NetBoxModelImportForm, NetBoxModelBulkEditForm
from netbox_slm.models import (
    SoftwareProduct,
    SoftwareProductVersion,
    SoftwareProductInstallation,
    SoftwareLicense,
    RenewalIntervalUnits,
    NotificationIntervalUnits,
    spdx_license_names,
)
from tenancy.models import Tenant, TenantGroup
from utilities.forms.constants import BOOLEAN_WITH_BLANK_CHOICES
from utilities.forms.fields import (
    CommentField,
    DynamicModelChoiceField,
    TagFilterField,
    LaxURLField,
    DynamicModelMultipleChoiceField,
)
from utilities.forms.rendering import FieldSet
from utilities.forms.widgets import APISelect, DatePicker


class SoftwareLicenseForm(NetBoxModelForm):
    comments = CommentField()
    fieldsets = (
        FieldSet(
            "name",
            "description",
            "software_product",
            "version",
            "installation",
            name=_("Software License"),
        ),
        FieldSet("tenant_group", "tenant", name=_("Tenancy")),
        FieldSet(
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
            name=_("License Details"),
        ),
        FieldSet("license_file", "license_key", "provider_portal_url", name=_("License Credentials")),
        FieldSet(
            "expiration_notifications_enabled",
            "default_notification_intervals",
            "custom_notification_interval",
            "custom_notification_interval_unit",
            "email_notifications",
            name=_("Expiration Notifications"),
        ),
        FieldSet("tags", name=_("Tags")),
    )

    spdx_expression = ChoiceField(required=False, choices=spdx_license_names(), label=_("SPDX expression"))
    stored_location_url = LaxURLField(required=False)
    start_date = DateField(required=False, widget=DatePicker())
    expiration_date = DateField(required=False, widget=DatePicker())
    renewal_interval = IntegerField(required=False, min_value=1)
    license_key = CharField(required=False, widget=Textarea(attrs={"rows": 3}))
    provider_portal_url = LaxURLField(required=False)
    custom_notification_interval = IntegerField(required=False, min_value=1)

    software_product = DynamicModelChoiceField(
        queryset=SoftwareProduct.objects.all(),
        required=True,
        label=_("Software Product"),
    )
    version = DynamicModelChoiceField(
        queryset=SoftwareProductVersion.objects.all(),
        required=False,
        widget=APISelect(attrs={"data-url": reverse_lazy("plugins-api:netbox_slm-api:softwareproductversion-list")}),
        query_params=dict(software_product="$software_product"),
    )
    installation = DynamicModelChoiceField(
        queryset=SoftwareProductInstallation.objects.all(),
        required=False,
        widget=APISelect(
            attrs={"data-url": reverse_lazy("plugins-api:netbox_slm-api:softwareproductinstallation-list")}
        ),
        query_params=dict(software_product="$software_product"),
    )
    tenant_group = DynamicModelChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False,
        label=_("Tenant Group"),
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        query_params={"group_id": "$tenant_group"},
        label=_("Tenant"),
    )

    class Meta:
        model = SoftwareLicense
        fields = (
            "name",
            "description",
            "software_product",
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
            "expiration_notifications_enabled",
            "default_notification_intervals",
            "custom_notification_interval",
            "custom_notification_interval_unit",
            "email_notifications",
            "version",
            "installation",
            "tenant_group",
            "tenant",
            "tags",
            "comments",
        )


class SoftwareLicenseFilterForm(NetBoxModelFilterSetForm):
    model = SoftwareLicense
    fieldsets = (
        FieldSet("q", "filter_id", "tag"),
        FieldSet(
            "name",
            "description",
            "type",
            "spdx_expression",
            "stored_location",
            "support",
            "lifetime",
            "renewal_interval",
            "renewal_interval_unit",
            "expiration_notifications_enabled",
            "email_notifications",
            "software_product_id",
            "version_id",
            "installation_id",
            "tenant_group_id",
            "tenant_id",
        ),
    )
    selector_fields = ("q", "filter_id", "name")

    tag = TagFilterField(model)

    name = CharField(required=False)
    description = CharField(required=False)
    type = CharField(required=False)
    spdx_expression = CharField(required=False, label=_("SPDX expression"))
    stored_location = CharField(required=False)
    support = ChoiceField(required=False, choices=BOOLEAN_WITH_BLANK_CHOICES)
    lifetime = ChoiceField(required=False, choices=BOOLEAN_WITH_BLANK_CHOICES)
    renewal_interval = IntegerField(required=False, min_value=1)
    renewal_interval_unit = ChoiceField(required=False, choices=RenewalIntervalUnits.choices)
    expiration_notifications_enabled = ChoiceField(required=False, choices=BOOLEAN_WITH_BLANK_CHOICES)
    email_notifications = ChoiceField(required=False, choices=BOOLEAN_WITH_BLANK_CHOICES)

    software_product_id = DynamicModelMultipleChoiceField(
        queryset=SoftwareProduct.objects.all(),
        required=False,
        label=_("Software Product"),
    )
    version_id = DynamicModelMultipleChoiceField(
        queryset=SoftwareProductVersion.objects.all(),
        required=False,
        label=_("Version"),
    )
    installation_id = DynamicModelMultipleChoiceField(
        queryset=SoftwareProductInstallation.objects.all(),
        required=False,
        label=_("Installation"),
    )
    tenant_group_id = DynamicModelMultipleChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False,
        label=_("Tenant Group"),
    )
    tenant_id = DynamicModelMultipleChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        query_params={"group_id": "$tenant_group_id"},
        label=_("Tenant"),
    )


class SoftwareLicenseBulkImportForm(NetBoxModelImportForm):
    support = NullBooleanField(
        required=False, help_text=_("Support (values other than 'True' and 'False' are ignored)")
    )

    class Meta:
        model = SoftwareLicense
        fields = (
            "name",
            "description",
            "software_product",
            "type",
            "spdx_expression",
            "stored_location",
            "start_date",
            "expiration_date",
            "lifetime",
            "renewal_interval",
            "renewal_interval_unit",
            "support",
            "license_amount",
            "license_key",
            "provider_portal_url",
            "expiration_notifications_enabled",
            "default_notification_intervals",
            "custom_notification_interval",
            "custom_notification_interval_unit",
            "email_notifications",
            "version",
            "installation",
            "tenant_group",
            "tenant",
            "tags",
        )


class SoftwareLicenseBulkEditForm(NetBoxModelBulkEditForm):
    model = SoftwareLicense
    fieldsets = (
        FieldSet(
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
            "license_key",
            "provider_portal_url",
            "expiration_notifications_enabled",
            "default_notification_intervals",
            "custom_notification_interval",
            "custom_notification_interval_unit",
            "email_notifications",
            "software_product",
            "version",
            "installation",
            "tenant_group",
            "tenant",
        ),
    )
    nullable_fields = (
        "type",
        "spdx_expression",
        "stored_location",
        "stored_location_url",
        "start_date",
        "expiration_date",
        "renewal_interval",
        "renewal_interval_unit",
        "support",
        "license_amount",
        "license_key",
        "provider_portal_url",
        "custom_notification_interval",
        "custom_notification_interval_unit",
        "version",
        "installation",
        "tenant_group",
        "tenant",
    )

    tag = TagFilterField(model)
    comments = CommentField()

    type = CharField(required=False)
    spdx_expression = ChoiceField(required=False, choices=spdx_license_names(), label=_("SPDX expression"))
    stored_location = CharField(required=False)
    stored_location_url = LaxURLField(required=False)
    start_date = DateField(required=False, widget=DatePicker())
    expiration_date = DateField(required=False, widget=DatePicker())
    lifetime = ChoiceField(required=False, choices=BOOLEAN_WITH_BLANK_CHOICES)
    renewal_interval = IntegerField(required=False, min_value=1)
    renewal_interval_unit = ChoiceField(required=False, choices=RenewalIntervalUnits.choices)
    support = ChoiceField(required=False, choices=BOOLEAN_WITH_BLANK_CHOICES)
    license_amount = IntegerField(required=False, min_value=0)
    license_key = CharField(required=False, widget=Textarea(attrs={"rows": 3}))
    provider_portal_url = LaxURLField(required=False)
    expiration_notifications_enabled = ChoiceField(required=False, choices=BOOLEAN_WITH_BLANK_CHOICES)
    default_notification_intervals = ChoiceField(required=False, choices=BOOLEAN_WITH_BLANK_CHOICES)
    custom_notification_interval = IntegerField(required=False, min_value=1)
    custom_notification_interval_unit = ChoiceField(required=False, choices=NotificationIntervalUnits.choices)
    email_notifications = ChoiceField(required=False, choices=BOOLEAN_WITH_BLANK_CHOICES)

    software_product = DynamicModelChoiceField(
        queryset=SoftwareProduct.objects.all(),
        required=False,
        label=_("Software Product"),
    )
    version = DynamicModelChoiceField(
        queryset=SoftwareProductVersion.objects.all(),
        required=False,
        widget=APISelect(attrs={"data-url": reverse_lazy("plugins-api:netbox_slm-api:softwareproductversion-list")}),
        query_params=dict(software_product="$software_product"),
    )
    installation = DynamicModelChoiceField(
        queryset=SoftwareProductInstallation.objects.all(),
        required=False,
        widget=APISelect(
            attrs={"data-url": reverse_lazy("plugins-api:netbox_slm-api:softwareproductinstallation-list")}
        ),
        query_params=dict(software_product="$software_product"),
    )
    tenant_group = DynamicModelChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False,
        label=_("Tenant Group"),
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        query_params={"group_id": "$tenant_group"},
        label=_("Tenant"),
    )
