from django.conf.urls import patterns, include, url
from django.contrib import admin
from tastypie.api import Api
from scraping.api import *

admin.autodiscover()

v1_api = Api(api_name='v1')
v1_api.register(DrugResource())
v1_api.register(DrugSupplierResource())
v1_api.register(ProductResource())

urlpatterns = patterns('',
    (r'^api/', include(v1_api.urls)),
    url(r'^admin/', include(admin.site.urls)),
)
