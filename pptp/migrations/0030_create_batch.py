from django.db import migrations, models


LEGACY_BATCHES = [
    ("2026_fish_seafood", "2026 Fish and Seafood Collection"),
    ("2026_meat_alternatives", "2026 Meat and Alternatives Collection"),
    ("2026_frozen_refrig_apps", "2026 Frozen and Refrigerated Appetizers Collection"),
    ("2026_refrig_sides_entrees", "2026 Refrigerated Sides and Entrees Collection"),
    ("2025_snapcan", "SNAP-CAN 2025"),
    ("2026_baked_goods", "2026 Baked Goods Collection"),
    ("2026_snack_foods", "2026 Snack Foods Collection"),
    ("tds", "Total Diet Study"),
    ("2025_supp_food", "2025 Supplemented Food Collection"),
    ("2025_frozen_entrees", "2025 Frozen Entrees Collection"),
]


def populate_batches(apps, schema_editor):
    Batch = apps.get_model("pptp", "Batch")
    for code, label in LEGACY_BATCHES:
        Batch.objects.get_or_create(code=code, defaults={"label": label})


def clear_batches(apps, schema_editor):
    Batch = apps.get_model("pptp", "Batch")
    Batch.objects.filter(code__in=[code for code, _ in LEGACY_BATCHES]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("pptp", "0029_alter_product_source_batch"),
    ]

    operations = [
        migrations.CreateModel(
            name="Batch",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "code",
                    models.SlugField(
                        help_text="Short unique identifier, e.g. '2026_fish_seafood'",
                        max_length=50,
                        unique=True,
                    ),
                ),
                (
                    "label",
                    models.CharField(
                        help_text="Display name shown in the batch dropdown",
                        max_length=255,
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Uncheck to hide from the dropdown for new products without deleting existing data",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Batches",
                "ordering": ["id"],
            },
        ),
        migrations.RunPython(populate_batches, clear_batches),
    ]
