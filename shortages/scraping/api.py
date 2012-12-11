from tastypie.resources import ModelResource, ALL
from tastypie.paginator import Paginator
from tastypie import fields
from .models import *

class DrugResource(ModelResource):
    suppliers = fields.ToManyField('scraping.api.DrugSupplierResource', 'drugsupplier_set', full=True)

    class Meta:
        queryset = Drug.objects.all()
        resource_name = 'drug'
        ordering = ['name', 'drugsupplier__reverified']
        filtering = {
            'name': ALL,
        }
        paginator_class = Paginator

    def get_object_list(self, request):
        ol = super(DrugResource, self).get_object_list(request)
        if '_order' in request.REQUEST: return ol.filter(drugsupplier__reverified__isnull=False).distinct().order_by('-drugsupplier__reverified')
        else: return ol

    def dehydrate(self, bundle):
        if bundle.obj.drugsupplier_set.count() > 0: bundle.data['last_verified'] = bundle.obj.drugsupplier_set.order_by('-reverified')[0].reverified
        return bundle

class DrugSupplierResource(ModelResource):
    products = fields.ToManyField('scraping.api.ProductResource', 'product_set', full=True)

    class Meta:
        queryset = DrugSupplier.objects.order_by('name').all()
        resource_name = 'supplier'


class ProductResource(ModelResource):
    class Meta:
        queryset = Product.objects.order_by('name').all()
        resource_name = 'product'