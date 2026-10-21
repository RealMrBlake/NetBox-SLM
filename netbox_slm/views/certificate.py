from netbox.views import generic
from netbox_slm import filtersets, forms, tables
from netbox_slm.models import Certificate
from netbox_slm.views.software_license import EmailNotificationPermissionMixin
from utilities.views import register_model_view


class CertificateEmailNotificationPermissionMixin(EmailNotificationPermissionMixin):
    email_permission = "netbox_slm.manage_certificate_email_notifications"


@register_model_view(Certificate, "list", path="", detail=False)
class CertificateListView(generic.ObjectListView):
    queryset = Certificate.objects.all()
    filterset = filtersets.CertificateFilterSet
    filterset_form = forms.CertificateFilterForm
    table = tables.CertificateTable


@register_model_view(Certificate)
class CertificateView(generic.ObjectView):
    queryset = Certificate.objects.all()


@register_model_view(Certificate, "add", detail=False)
@register_model_view(Certificate, "edit")
class CertificateEditView(CertificateEmailNotificationPermissionMixin, generic.ObjectEditView):
    queryset = Certificate.objects.all()
    form = forms.CertificateForm


@register_model_view(Certificate, "delete")
class CertificateDeleteView(generic.ObjectDeleteView):
    queryset = Certificate.objects.all()


@register_model_view(Certificate, "bulk_import", detail=False)
class CertificateBulkImportView(CertificateEmailNotificationPermissionMixin, generic.BulkImportView):
    queryset = Certificate.objects.all()
    model_form = forms.CertificateBulkImportForm


@register_model_view(Certificate, "bulk_edit", path="edit", detail=False)
class CertificateBulkEditView(CertificateEmailNotificationPermissionMixin, generic.BulkEditView):
    queryset = Certificate.objects.all()
    filterset = filtersets.CertificateFilterSet
    table = tables.CertificateTable
    form = forms.CertificateBulkEditForm


@register_model_view(Certificate, "bulk_delete", path="delete", detail=False)
class CertificateBulkDeleteView(generic.BulkDeleteView):
    queryset = Certificate.objects.all()
    filterset = filtersets.CertificateFilterSet
    table = tables.CertificateTable
