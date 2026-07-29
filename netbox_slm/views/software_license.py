from netbox.views import generic
from django.utils.translation import gettext_lazy as _
from netbox_slm import filtersets, forms, tables
from netbox_slm.models import SoftwareLicense
from utilities.views import register_model_view


class EmailNotificationPermissionMixin:
    """Prevent users without the dedicated permission from changing SMTP delivery."""

    email_permission = "netbox_slm.manage_softwarelicense_email_notifications"

    def dispatch(self, request, *args, **kwargs):
        form_attribute = "model_form" if hasattr(self, "model_form") else "form"
        base_form = getattr(self, form_attribute)
        can_manage_email = request.user.has_perm(self.email_permission)

        class PermissionAwareForm(base_form):
            def __init__(self, *form_args, **form_kwargs):
                super().__init__(*form_args, **form_kwargs)
                if not can_manage_email and "email_notifications" in self.fields:
                    field = self.fields["email_notifications"]
                    field.disabled = True
                    field.help_text = _(
                        "Only administrators or explicitly authorized users can change this setting."
                    )

        setattr(self, form_attribute, PermissionAwareForm)
        return super().dispatch(request, *args, **kwargs)


@register_model_view(SoftwareLicense, "list", path="", detail=False)
class SoftwareLicenseListView(generic.ObjectListView):
    queryset = SoftwareLicense.objects.all()
    filterset = filtersets.SoftwareLicenseFilterSet
    filterset_form = forms.SoftwareLicenseFilterForm
    table = tables.SoftwareLicenseTable


@register_model_view(SoftwareLicense)
class SoftwareLicenseView(generic.ObjectView):
    queryset = SoftwareLicense.objects.all()


@register_model_view(SoftwareLicense, "add", detail=False)
@register_model_view(SoftwareLicense, "edit")
class SoftwareLicenseEditView(EmailNotificationPermissionMixin, generic.ObjectEditView):
    queryset = SoftwareLicense.objects.all()
    form = forms.SoftwareLicenseForm


@register_model_view(SoftwareLicense, "delete")
class SoftwareLicenseDeleteView(generic.ObjectDeleteView):
    queryset = SoftwareLicense.objects.all()


@register_model_view(SoftwareLicense, "bulk_import", detail=False)
class SoftwareLicenseBulkImportView(EmailNotificationPermissionMixin, generic.BulkImportView):
    queryset = SoftwareLicense.objects.all()
    model_form = forms.SoftwareLicenseBulkImportForm


@register_model_view(SoftwareLicense, "bulk_edit", path="edit", detail=False)
class SoftwareLicenseBulkEditView(EmailNotificationPermissionMixin, generic.BulkEditView):
    queryset = SoftwareLicense.objects.all()
    filterset = filtersets.SoftwareLicenseFilterSet
    table = tables.SoftwareLicenseTable
    form = forms.SoftwareLicenseBulkEditForm


@register_model_view(SoftwareLicense, "bulk_delete", path="delete", detail=False)
class SoftwareLicenseBulkDeleteView(generic.BulkDeleteView):
    queryset = SoftwareLicense.objects.all()
    filterset = filtersets.SoftwareLicenseFilterSet
    table = tables.SoftwareLicenseTable
