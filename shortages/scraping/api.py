from tastypie.resources import ModelResource
from tastypie import fields
from .models import *

class DrugResource(ModelResource):
	suppliers = fields.ToManyField('scraping.api.DrugSupplierResource', 'drugsupplier_set', full=True)
	class Meta:
		queryset = Drug.objects.all()
		resource_name = 'drug'

class DrugSupplierResource(ModelResource):
	products = fields.ToManyField('scraping.api.ProductResource', 'product_set', full=True)
	class Meta:
		queryset = DrugSupplier.objects.all()
		resource_name = 'supplier'

class ProductResource(ModelResource):
	class Meta:
		queryset = Product.objects.all()
		resource_name = 'product'