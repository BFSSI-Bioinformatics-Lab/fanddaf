import django.db.models.deletion
from django.db import migrations, models


def link_products_to_batches(apps, schema_editor):
    Product = apps.get_model("pptp", "Product")
    Batch = apps.get_model("pptp", "Batch")
    batches_by_code = {batch.code: batch for batch in Batch.objects.all()}
    for product in Product.objects.exclude(source_batch__isnull=True).exclude(source_batch=""):
        batch = batches_by_code.get(product.source_batch)
        if batch is not None:
            product.source_batch_fk = batch
            product.save(update_fields=["source_batch_fk"])


def unlink_products_from_batches(apps, schema_editor):
    Product = apps.get_model("pptp", "Product")
    Product.objects.update(source_batch_fk=None)


class Migration(migrations.Migration):
    dependencies = [
        ("pptp", "0030_create_batch"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="source_batch_fk",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="products",
                to="pptp.batch",
                help_text="Product collection batch",
            ),
        ),
        migrations.RunPython(link_products_to_batches, unlink_products_from_batches),
    ]
