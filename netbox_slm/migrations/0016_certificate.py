import django.core.validators
import django.db.models.deletion
import taggit.managers
from django.conf import settings
from django.db import migrations, models

import netbox_slm.models
import utilities.json


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("dcim", "0001_initial"),
        ("extras", "0001_initial"),
        ("tenancy", "0001_initial"),
        ("virtualization", "0001_initial"),
        ("netbox_slm", "0015_platform_constraint_message"),
    ]

    operations = [
        migrations.CreateModel(
            name="Certificate",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "custom_field_data",
                    models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
                ),
                ("expiration_notifications_enabled", models.BooleanField(default=True)),
                ("default_notification_intervals", models.BooleanField(default=True)),
                (
                    "custom_notification_interval",
                    models.PositiveIntegerField(
                        blank=True, null=True, validators=[django.core.validators.MinValueValidator(1)]
                    ),
                ),
                (
                    "custom_notification_interval_unit",
                    models.CharField(
                        blank=True,
                        choices=[("days", "Days"), ("weeks", "Weeks"), ("months", "Months")],
                        max_length=8,
                    ),
                ),
                ("email_notifications", models.BooleanField(default=False)),
                ("name", models.CharField(max_length=128)),
                ("comments", models.TextField(blank=True)),
                ("description", models.CharField(blank=True, max_length=255)),
                (
                    "type",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("server", "TLS server"),
                            ("client", "TLS client"),
                            ("ca", "Certificate authority"),
                            ("code_signing", "Code signing"),
                            ("email", "S/MIME email"),
                            ("other", "Other"),
                        ],
                        max_length=16,
                    ),
                ),
                ("common_name", models.CharField(blank=True, max_length=255)),
                ("subject_alternative_names", models.TextField(blank=True)),
                ("issuer", models.CharField(blank=True, max_length=255)),
                ("serial_number", models.CharField(blank=True, max_length=128)),
                ("fingerprint", models.CharField(blank=True, max_length=128)),
                ("start_date", models.DateField(blank=True, null=True)),
                ("expiration_date", models.DateField(blank=True, null=True)),
                ("auto_renewal", models.BooleanField(default=False)),
                (
                    "certificate_file",
                    models.FileField(blank=True, null=True, upload_to="netbox_slm/certificates/"),
                ),
                ("stored_location", models.CharField(blank=True, max_length=255)),
                ("stored_location_url", netbox_slm.models.LaxURLField(blank=True, max_length=1024, null=True)),
                ("provider_portal_url", netbox_slm.models.LaxURLField(blank=True, max_length=1024, null=True)),
                (
                    "device",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="certificates",
                        to="dcim.device",
                    ),
                ),
                (
                    "installation",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="certificates",
                        to="netbox_slm.softwareproductinstallation",
                    ),
                ),
                (
                    "software_product",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="certificates",
                        to="netbox_slm.softwareproduct",
                    ),
                ),
                ("tags", taggit.managers.TaggableManager(through="extras.TaggedItem", to="extras.Tag")),
                (
                    "tenant",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="certificates",
                        to="tenancy.tenant",
                    ),
                ),
                (
                    "tenant_group",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="certificates",
                        to="tenancy.tenantgroup",
                    ),
                ),
                (
                    "virtualmachine",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="certificates",
                        to="virtualization.virtualmachine",
                    ),
                ),
            ],
            options={
                "verbose_name": "certificate",
                "verbose_name_plural": "certificates",
                "permissions": [
                    ("manage_certificate_email_notifications", "Can manage certificate email notifications")
                ],
            },
        ),
        migrations.CreateModel(
            name="CertificateNotificationLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("expiration_date", models.DateField()),
                ("notification_date", models.DateField()),
                ("netbox_sent_at", models.DateTimeField(blank=True, null=True)),
                ("email_sent_at", models.DateTimeField(blank=True, null=True)),
                (
                    "certificate",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notification_logs",
                        to="netbox_slm.certificate",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="certificatenotificationlog",
            constraint=models.UniqueConstraint(
                fields=("certificate", "user", "expiration_date", "notification_date"),
                name="netbox_slm_certificate_notification_unique",
            ),
        ),
    ]
