from django.db import migrations, models
import django.core.validators
import netbox_slm.models


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_slm", "0011_softwarelicense_tenancy"),
    ]

    operations = [
        migrations.AlterField(
            model_name="softwarelicense",
            name="type",
            field=models.CharField(blank=True, max_length=128),
        ),
        migrations.AddField(
            model_name="softwarelicense",
            name="lifetime",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="softwarelicense",
            name="renewal_interval",
            field=models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AddField(
            model_name="softwarelicense",
            name="renewal_interval_unit",
            field=models.CharField(
                blank=True,
                choices=[("days", "Days"), ("months", "Months"), ("years", "Years")],
                max_length=8,
            ),
        ),
        migrations.AddField(
            model_name="softwarelicense",
            name="license_file",
            field=models.FileField(blank=True, null=True, upload_to="netbox_slm/licenses/"),
        ),
        migrations.AddField(
            model_name="softwarelicense",
            name="license_key",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="softwarelicense",
            name="provider_portal_url",
            field=netbox_slm.models.LaxURLField(blank=True, max_length=1024, null=True),
        ),
    ]
