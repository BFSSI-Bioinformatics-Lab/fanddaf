from django.db import migrations

# FLAIME matches a batch to its collection by label, so the labels must equal the FLAIME
# collection names exactly.
RENAMES = {
    "tds": ("Total Diet Study", "2025 Total Diet Study"),
    "tds_2026": ("Total Diet Study 2026", "2026 Total Diet Study"),
}


def forwards(apps, schema_editor):
    Batch = apps.get_model("pptp", "Batch")
    for code, (_, new) in RENAMES.items():
        Batch.objects.filter(code=code).update(label=new)


def backwards(apps, schema_editor):
    Batch = apps.get_model("pptp", "Batch")
    for code, (old, _) in RENAMES.items():
        Batch.objects.filter(code=code).update(label=old)


class Migration(migrations.Migration):
    dependencies = [
        ("pptp", "0033_add_store"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
