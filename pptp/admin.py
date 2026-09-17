from django.contrib import admin
from .models.products import Batch, Product, Barcode, NutritionFacts, Ingredients, ProductImage


@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ['label', 'code', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'label']
    prepopulated_fields = {'code': ('label',)}


admin.site.register(Product)
admin.site.register(Barcode)
admin.site.register(NutritionFacts)
admin.site.register(Ingredients)
admin.site.register(ProductImage)
