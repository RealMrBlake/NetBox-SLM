import django.core.validators
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("netbox_slm", "0012_softwarelicense_renewal_and_credentials"),
    ]

    operations = [
        migrations.AddField(
            model_name="softwarelicense",
            name="expiration_notifications_enabled",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="softwarelicense",
            name="default_notification_intervals",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="softwarelicense",
            name="custom_notification_interval",
            field=models.PositiveIntegerField(
                blank=True, null=True, validators=[django.core.validators.MinValueValidator(1)]
            ),
        ),
        migrations.AddField(
            model_name="softwarelicense",
            name="custom_notification_interval_unit",
            field=models.CharField(
                blank=True,
                choices=[("days", "Days"), ("weeks", "Weeks"), ("months", "Months")],
                max_length=8,
            ),
        ),
        migrations.AddField(
            model_name="softwarelicense",
            name="email_notifications",
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name="SoftwareLicenseNotificationLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("expiration_date", models.DateField()),
                ("notification_date", models.DateField()),
                ("netbox_sent_at", models.DateTimeField(blank=True, null=True)),
                ("email_sent_at", models.DateTimeField(blank=True, null=True)),
                (
                    "license",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notification_logs",
                        to="netbox_slm.softwarelicense",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="softwarelicensenotificationlog",
            constraint=models.UniqueConstraint(
                fields=("license", "user", "expiration_date", "notification_date"),
                name="netbox_slm_license_notification_unique",
            ),
        ),
    ]
