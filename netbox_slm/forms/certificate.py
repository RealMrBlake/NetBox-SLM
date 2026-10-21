from django.core.files.uploadedfile import UploadedFile
from django.forms import CharField, ChoiceField, DateField, IntegerField, MultipleChoiceField, Textarea
from django.utils.translation import gettext_lazy as _

from dcim.models import Device
from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm, NetBoxModelImportForm, NetBoxModelBulkEditForm
from netbox_slm.certificate_parser import CertificateParseError, apply_certificate_file
from netbox_slm.models import (
    Certificate,
    CertificateTypes,
    NotificationIntervalUnits,
    SoftwareProduct,
    SoftwareProductInstallation,
)
from tenancy.models import Tenant, TenantGroup
from utilities.forms import add_blank_choice
from utilities.forms.constants import BOOLEAN_WITH_BLANK_CHOICES
from utilities.forms.fields import (
    CommentField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    LaxURLField,
    TagFilterField,
)
from utilities.forms.rendering import FieldSet
from utilities.forms.widgets import DatePicker
from virtualization.models import VirtualMachine


class CertificateForm(NetBoxModelForm):
    comments = CommentField()
    name = CharField(
        required=False,
        max_length=128,
        label=_("Name"),
        help_text=_("Taken from the certificate's common name if left empty"),
    )
    fieldsets = (
        FieldSet("name", "description", "type", name=_("Certificate")),
        FieldSet("software_product", "installation", "device", "virtualmachine", name=_("Assignment")),
        FieldSet("tenant_group", "tenant", name=_("Tenancy")),
        FieldSet(
            "common_name",
            "subject_alternative_names",
            "issuer",
            "serial_number",
            "fingerprint",
            "start_date",
            "expiration_date",
            "auto_renewal",
            name=_("Certificate Details"),
        ),
        FieldSet(
            "certificate_file",
            "stored_location",
            "stored_location_url",
            "provider_portal_url",
            name=_("Storage"),
        ),
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

    subject_alternative_names = CharField(
        required=False,
        widget=Textarea(attrs={"rows": 3}),
        label=_("Subject alternative names"),
        help_text=_("One DNS name or IP address per line"),
    )
    start_date = DateField(required=False, widget=DatePicker(), label=_("Valid from"))
    expiration_date = DateField(required=False, widget=DatePicker(), label=_("Valid until"))
    stored_location_url = LaxURLField(required=False, label=_("Stored location URL"))
    provider_portal_url = LaxURLField(required=False, label=_("Provider portal URL"))
    custom_notification_interval = IntegerField(required=False, min_value=1)

    software_product = DynamicModelChoiceField(
        queryset=SoftwareProduct.objects.all(),
        required=False,
        label=_("Software Product"),
    )
    installation = DynamicModelChoiceField(
        queryset=SoftwareProductInstallation.objects.all(),
        required=False,
        query_params={"software_product_id": "$software_product"},
        label=_("Installation"),
    )
    device = DynamicModelChoiceField(queryset=Device.objects.all(), required=False, label=_("Device"))
    virtualmachine = DynamicModelChoiceField(
        queryset=VirtualMachine.objects.all(), required=False, label=_("Virtual Machine")
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["certificate_file"].help_text = _(
            "PEM or DER file without private key. Common name, SANs, issuer, serial number, fingerprint and "
            "validity are filled in automatically."
        )

    def clean(self):
        cleaned_data = super().clean()
        uploaded_file = cleaned_data.get("certificate_file")
        if isinstance(uploaded_file, UploadedFile):
            try:
                apply_certificate_file(cleaned_data, uploaded_file)
            except CertificateParseError as error:
                self.add_error("certificate_file", error)
        if not cleaned_data.get("name") and "name" not in self.errors:
            self.add_error("name", _("Enter a name or upload a certificate file."))
        return cleaned_data

    class Meta:
        model = Certificate
        fields = (
            "name",
            "description",
            "type",
            "common_name",
            "subject_alternative_names",
            "issuer",
            "serial_number",
            "fingerprint",
            "start_date",
            "expiration_date",
            "auto_renewal",
            "certificate_file",
            "stored_location",
            "stored_location_url",
            "provider_portal_url",
            "expiration_notifications_enabled",
            "default_notification_intervals",
            "custom_notification_interval",
            "custom_notification_interval_unit",
            "email_notifications",
            "software_product",
            "installation",
            "device",
            "virtualmachine",
            "tenant_group",
            "tenant",
            "tags",
            "comments",
        )


class CertificateFilterForm(NetBoxModelFilterSetForm):
    model = Certificate
    fieldsets = (
        FieldSet("q", "filter_id", "tag"),
        FieldSet(
            "name",
            "type",
            "common_name",
            "issuer",
            "serial_number",
            "auto_renewal",
            "expiration_notifications_enabled",
            "email_notifications",
            name=_("Attributes"),
        ),
        FieldSet(
            "software_product_id",
            "installation_id",
            "device_id",
            "virtualmachine_id",
            "tenant_group_id",
            "tenant_id",
            name=_("Assignment"),
        ),
    )
    selector_fields = ("q", "filter_id", "name")

    tag = TagFilterField(model)

    name = CharField(required=False)
    type = MultipleChoiceField(required=False, choices=CertificateTypes.choices)
    common_name = CharField(required=False)
    issuer = CharField(required=False)
    serial_number = CharField(required=False)
    auto_renewal = ChoiceField(required=False, choices=BOOLEAN_WITH_BLANK_CHOICES)
    expiration_notifications_enabled = ChoiceField(required=False, choices=BOOLEAN_WITH_BLANK_CHOICES)
    email_notifications = ChoiceField(required=False, choices=BOOLEAN_WITH_BLANK_CHOICES)

    software_product_id = DynamicModelMultipleChoiceField(
        queryset=SoftwareProduct.objects.all(), required=False, label=_("Software Product")
    )
    installation_id = DynamicModelMultipleChoiceField(
        queryset=SoftwareProductInstallation.objects.all(), required=False, label=_("Installation")
    )
    device_id = DynamicModelMultipleChoiceField(queryset=Device.objects.all(), required=False, label=_("Device"))
    virtualmachine_id = DynamicModelMultipleChoiceField(
        queryset=VirtualMachine.objects.all(), required=False, label=_("Virtual Machine")
    )
    tenant_group_id = DynamicModelMultipleChoiceField(
        queryset=TenantGroup.objects.all(), required=False, label=_("Tenant Group")
    )
    tenant_id = DynamicModelMultipleChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        query_params={"group_id": "$tenant_group_id"},
        label=_("Tenant"),
    )


class CertificateBulkImportForm(NetBoxModelImportForm):
    class Meta:
        model = Certificate
        fields = (
            "name",
            "description",
            "type",
            "common_name",
            "subject_alternative_names",
            "issuer",
            "serial_number",
            "fingerprint",
            "start_date",
            "expiration_date",
            "auto_renewal",
            "stored_location",
            "stored_location_url",
            "provider_portal_url",
            "expiration_notifications_enabled",
            "default_notification_intervals",
            "custom_notification_interval",
            "custom_notification_interval_unit",
            "email_notifications",
            "software_product",
            "installation",
            "device",
            "virtualmachine",
            "tenant_group",
            "tenant",
            "tags",
        )


class CertificateBulkEditForm(NetBoxModelBulkEditForm):
    model = Certificate
    fieldsets = (
        FieldSet(
            "type",
            "issuer",
            "start_date",
            "expiration_date",
            "auto_renewal",
            "stored_location",
            "stored_location_url",
            "provider_portal_url",
            "expiration_notifications_enabled",
            "default_notification_intervals",
            "custom_notification_interval",
            "custom_notification_interval_unit",
            "email_notifications",
            "software_product",
            "device",
            "virtualmachine",
            "tenant_group",
            "tenant",
        ),
    )
    nullable_fields = (
        "type",
        "issuer",
        "start_date",
        "expiration_date",
        "stored_location",
        "stored_location_url",
        "provider_portal_url",
        "custom_notification_interval",
        "custom_notification_interval_unit",
        "software_product",
        "device",
        "virtualmachine",
        "tenant_group",
        "tenant",
    )

    tag = TagFilterField(model)
    comments = CommentField()

    type = ChoiceField(required=False, choices=add_blank_choice(CertificateTypes.choices))
    issuer = CharField(required=False)
    start_date = DateField(required=False, widget=DatePicker(), label=_("Valid from"))
    expiration_date = DateField(required=False, widget=DatePicker(), label=_("Valid until"))
    auto_renewal = ChoiceField(required=False, choices=BOOLEAN_WITH_BLANK_CHOICES)
    stored_location = CharField(required=False)
    stored_location_url = LaxURLField(required=False)
    provider_portal_url = LaxURLField(required=False)
    expiration_notifications_enabled = ChoiceField(required=False, choices=BOOLEAN_WITH_BLANK_CHOICES)
    default_notification_intervals = ChoiceField(required=False, choices=BOOLEAN_WITH_BLANK_CHOICES)
    custom_notification_interval = IntegerField(required=False, min_value=1)
    custom_notification_interval_unit = ChoiceField(
        required=False, choices=add_blank_choice(NotificationIntervalUnits.choices)
    )
    email_notifications = ChoiceField(required=False, choices=BOOLEAN_WITH_BLANK_CHOICES)

    software_product = DynamicModelChoiceField(
        queryset=SoftwareProduct.objects.all(), required=False, label=_("Software Product")
    )
    device = DynamicModelChoiceField(queryset=Device.objects.all(), required=False, label=_("Device"))
    virtualmachine = DynamicModelChoiceField(
        queryset=VirtualMachine.objects.all(), required=False, label=_("Virtual Machine")
    )
    tenant_group = DynamicModelChoiceField(queryset=TenantGroup.objects.all(), required=False, label=_("Tenant Group"))
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        query_params={"group_id": "$tenant_group"},
        label=_("Tenant"),
    )
