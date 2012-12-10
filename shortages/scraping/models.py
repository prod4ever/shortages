from django.db import models

# Create your models here.
class Drug(models.Model):
	name = models.CharField(max_length=255)
	url = models.CharField(max_length=255)

class DrugSupplier(models.Model):
	drug = models.ForeignKey(Drug)
	name = models.TextField(null=True)
	related_info = models.TextField(null=True)
	reason = models.TextField(null=True)
	availability = models.TextField(null=True)
	reverified = models.DateTimeField(null=True)

class Product(models.Model):
	supplier = models.ForeignKey(DrugSupplier)
	name = models.CharField(max_length=255)
	availability = models.TextField(null=True)
