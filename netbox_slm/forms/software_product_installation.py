from django.forms import ValidationError
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from dcim.models import Device
from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm, NetBoxModelImportForm, NetBoxModelBulkEditForm
from netbox_slm.models import SoftwareProductInstallation, SoftwareProduct, SoftwareProductVersion
from utilities.forms.fields import (
    CommentField,
    DynamicModelChoiceField,
    TagFilterField,
    DynamicModelMultipleChoiceField,
)
from utilities.forms.rendering import FieldSet
from utilities.forms.widgets import APISelect
from virtualization.models import Cluster, VirtualMachine


class SoftwareProductInstallationForm(NetBoxModelForm):
    comments = CommentField()
    fieldsets = (
        FieldSet("device", "virtualmachine", "cluster", name=_("Platform Destination (select exactly one)")),
        FieldSet("software_product", "version", name=_("Software")),
        FieldSet("tags", name=_("Tags")),
    )

    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        help_text=_("Select either a device, a virtual machine, or a cluster."),
    )
    virtualmachine = DynamicModelChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        label=_("Virtual Machine"),
        help_text=_("Leave empty when another platform destination is selected."),
    )
    cluster = DynamicModelChoiceField(
        queryset=Cluster.objects.all(),
        required=False,
        help_text=_("Leave empty when another platform destination is selected."),
    )
    software_product = DynamicModelChoiceField(
        queryset=SoftwareProduct.objects.all(),
        required=True,
        label=_("Software Product"),
    )
    version = DynamicModelChoiceField(
        queryset=SoftwareProductVersion.objects.all(),
        required=True,
        widget=APISelect(attrs={"data-url": reverse_lazy("plugins-api:netbox_slm-api:softwareproductversion-list")}),
        query_params=dict(software_product="$software_product"),
    )

    class Meta:
        model = SoftwareProductInstallation
        fields = (
            "device",
            "virtualmachine",
            "cluster",
            "software_product",
            "version",
            "tags",
            "comments",
        )

    def clean_version(self):
        version = self.cleaned_data["version"]
        software_product = self.cleaned_data["software_product"]
        if version not in software_product.softwareproductversion_set.all():
            raise ValidationError(
                _("Version '%(version)s' does not belong to %(product)s. Select a compatible version.")
                % {"version": version, "product": software_product}
            )
        return version

    def clean(self):
        cleaned_data = super().clean()
        destinations = [
            cleaned_data.get("device"),
            cleaned_data.get("virtualmachine"),
            cleaned_data.get("cluster"),
        ]
        if sum(destination is not None for destination in destinations) != 1:
            raise ValidationError(_("Select exactly one platform destination: device, virtual machine, or cluster."))
        return cleaned_data


class SoftwareProductInstallationFilterForm(NetBoxModelFilterSetForm):
    model = SoftwareProductInstallation
    fieldsets = (
        FieldSet("q", "filter_id", "tag"),
        FieldSet("device_id", "virtualmachine_id", "cluster_id", "software_product_id", "version_id"),
    )
    selector_fields = ("filter_id", "q")

    tag = TagFilterField(model)

    device_id = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        label=_("Device"),
    )
    virtualmachine_id = DynamicModelMultipleChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        label=_("Virtual Machine"),
    )
    cluster_id = DynamicModelMultipleChoiceField(
        queryset=Cluster.objects.all(),
        required=False,
        label=_("Cluster"),
    )
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


class SoftwareProductInstallationBulkImportForm(NetBoxModelImportForm):
    class Meta:
        model = SoftwareProductInstallation
        fields = (
            "device",
            "virtualmachine",
            "cluster",
            "software_product",
            "version",
            "tags",
        )


class SoftwareProductInstallationBulkEditForm(NetBoxModelBulkEditForm):
    model = SoftwareProductInstallation
    fieldsets = (FieldSet("device", "virtualmachine", "cluster", "software_product", "version"),)
    nullable_fields = ("device", "virtualmachine", "cluster", "comments")

    tag = TagFilterField(model)
    comments = CommentField()

    device = DynamicModelChoiceField(queryset=Device.objects.all(), required=False)
    virtualmachine = DynamicModelChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        label=_("Virtual Machine"),
    )
    cluster = DynamicModelChoiceField(queryset=Cluster.objects.all(), required=False)
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
