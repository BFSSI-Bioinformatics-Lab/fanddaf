import django.db.models.deletion
from django.db import migrations, models


INITIAL_STORES = [
    ("costco_on", "Costco, Ontario"),
    ("costco_qc", "Costco, Quebec"),
    ("farm_boy_on", "Farm Boy, Ontario"),
    ("food_basics_on", "Food Basics, Ontario"),
    ("freshco_on", "FreshCo, Ontario"),
    ("iga_iga_extra_qc", "IGA/IGA extra, Quebec"),
    ("loblaws_on", "Loblaws, Ontario"),
    ("maxi_cie_qc", "Maxi & Cie, Quebec"),
    ("metro_on", "Metro, Ontario"),
    ("metro_qc", "Metro, Quebec"),
    ("sobeys_on", "Sobeys, Ontario"),
    ("super_c_qc", "Super C, Quebec"),
    ("superstore_on", "Superstore, Ontario"),
    ("voila_on", "Voila, Ontario"),
    ("walmart_on", "Walmart, Ontario"),
    ("walmart_qc", "Walmart, Quebec"),
    ("nos_on", "Not otherwise specified, Ontario"),
    ("nos_qc", "Not otherwise specified, Quebec"),
]


def populate_stores(apps, schema_editor):
    Store = apps.get_model("pptp", "Store")
    for code, label in INITIAL_STORES:
        Store.objects.get_or_create(code=code, defaults={"label": label})


def clear_stores(apps, schema_editor):
    Store = apps.get_model("pptp", "Store")
    Store.objects.filter(code__in=[code for code, _ in INITIAL_STORES]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("pptp", "0032_finalize_source_batch"),
    ]

    operations = [
        migrations.CreateModel(
            name="Store",
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
                        help_text="Short unique identifier, e.g. 'costco_on'",
                        max_length=50,
                        unique=True,
                    ),
                ),
                (
                    "label",
                    models.CharField(
                        help_text="Display name shown in the store dropdown, e.g. 'Costco, Ontario'",
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
                "verbose_name_plural": "Stores",
                "ordering": ["id"],
            },
        ),
        migrations.RunPython(populate_stores, clear_stores),
        migrations.AddField(
            model_name="product",
            name="store",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="products",
                to="pptp.store",
                help_text="Store the product was sourced from",
            ),
        ),
    ]
