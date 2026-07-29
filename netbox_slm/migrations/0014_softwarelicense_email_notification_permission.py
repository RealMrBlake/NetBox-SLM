from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_slm", "0013_license_expiration_notifications"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="softwarelicense",
            options={
                "permissions": [
                    (
                        "manage_softwarelicense_email_notifications",
                        "Can manage license email notifications",
                    )
                ],
                "verbose_name": "software license",
                "verbose_name_plural": "software licenses",
            },
        ),
    ]
