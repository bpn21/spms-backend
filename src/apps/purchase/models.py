from django.db import models
# Create your models here.
from django.conf import settings

class Products(models.Model):
    # port = models.ForeignKey(UniqueUserId, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    # Slave Model
    name = models.CharField(max_length=255)
    
    status = models.BooleanField(default=True)
    
    # Utility fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        managed = True
        # db_table = "tbl_purchase_product"
        verbose_name = "Product Information"
        ordering = ('-created_at',)
        constraints = [
            models.UniqueConstraint(fields=['name', 'user'], name='unique_purchase_product_per_user')
        ]
class Purchase(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,null=True,blank=True)

    product = models.ForeignKey('Products',on_delete=models.DO_NOTHING,null=False,blank=False)
    company_name = models.CharField(max_length=100)
    price = models.FloatField()
    pan_number = models.IntegerField()

    # utitlity field
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta :
        managed = True
        # db_table = 'tbl_purchase'
        verbose_name = 'Purchase Information'
        ordering = ('-created_at',)
        constraints = [models.UniqueConstraint(fields=['user','product'],name='unique_purchase_per_user')]
