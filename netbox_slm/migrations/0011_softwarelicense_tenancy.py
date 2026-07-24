from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("tenancy", "0001_initial"),
        ("netbox_slm", "0010_softwarelicense_spdx_expression"),
    ]

    operations = [
        migrations.AddField(
            model_name="softwarelicense",
            name="tenant_group",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="software_licenses",
                to="tenancy.tenantgroup",
            ),
        ),
        migrations.AddField(
            model_name="softwarelicense",
            name="tenant",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="software_licenses",
                to="tenancy.tenant",
            ),
        ),
    ]
