from django.db import migrations

# NetBox ObjectPermission actions are limited to 30 characters.
RENAMES = [
    ("softwarelicense", "manage_softwarelicense_email_notifications", "manage_license_emails"),
    ("certificate", "manage_certificate_email_notifications", "manage_certificate_emails"),
]


def rename_permissions(apps, schema_editor, reverse=False):
    Permission = apps.get_model("auth", "Permission")
    for model, old, new in RENAMES:
        if reverse:
            old, new = new, old
        Permission.objects.filter(content_type__app_label="netbox_slm", content_type__model=model, codename=old).update(
            codename=new
        )


def reverse_rename_permissions(apps, schema_editor):
    rename_permissions(apps, schema_editor, reverse=True)


class Migration(migrations.Migration):
    dependencies = [
        ("auth", "0001_initial"),
        ("netbox_slm", "0016_certificate"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="softwarelicense",
            options={
                "permissions": [("manage_license_emails", "Can manage license email notifications")],
                "verbose_name": "software license",
                "verbose_name_plural": "software licenses",
            },
        ),
        migrations.AlterModelOptions(
            name="certificate",
            options={
                "permissions": [("manage_certificate_emails", "Can manage certificate email notifications")],
                "verbose_name": "certificate",
                "verbose_name_plural": "certificates",
            },
        ),
        migrations.RunPython(rename_permissions, reverse_rename_permissions),
    ]
