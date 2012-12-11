from tastypie.resources import ModelResource, ALL
from tastypie import fields
from .models import *

class DrugResource(ModelResource):
    suppliers = fields.ToManyField('scraping.api.DrugSupplierResource', 'drugsupplier_set', full=True)

    class Meta:
        queryset = Drug.objects.all()
        resource_name = 'drug'
        ordering = ['name']
        filtering = {
            'name': ALL
        }


class DrugSupplierResource(ModelResource):
    products = fields.ToManyField('scraping.api.ProductResource', 'product_set', full=True)

    class Meta:
        queryset = DrugSupplier.objects.order_by('name').all()
        resource_name = 'supplier'


class ProductResource(ModelResource):
    class Meta:
        queryset = Product.objects.order_by('name').all()
        resource_name = 'product'