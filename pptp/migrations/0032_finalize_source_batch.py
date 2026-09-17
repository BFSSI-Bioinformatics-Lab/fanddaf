from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("pptp", "0031_add_source_batch_fk"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="product",
            name="source_batch",
        ),
        migrations.RenameField(
            model_name="product",
            old_name="source_batch_fk",
            new_name="source_batch",
        ),
    ]
