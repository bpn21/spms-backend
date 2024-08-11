from django.db import models
from django.utils import timezone
from uuid import uuid4
from django.template.defaultfilters import slugify
from django.conf import settings

# Create your models here.


class Client(models.Model):
    # slave model
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, null=True, blank=True)

    PROVINCES = [('Province1', 'Province1'), ('Province2',
                                              'Province2'), ('Proviance3', 'Proviance3')]

    # Basic Fields
    client_name = models.CharField(max_length=255)
    address_line_1 = models.CharField(max_length=200)
    client_logo = models.ImageField(
        default='default_logo.jpg', upload_to='company_logos')
    # this will create new folder called company logos.
    # we do this because we do not want to upload everything into same place.
    province = models.CharField(choices=PROVINCES, blank=True, max_length=100)
    postal_code = models.CharField(null=True, blank=True, max_length=100)
    # Slug is very important because  it helps in routing and its good for seo.
    slug = models.SlugField(null=True, blank=True, max_length=10)
    contact_number = models.CharField(max_length=255)
    email_addrress = models.CharField(null=True, blank=True, max_length=100)
    pan_number = models.CharField(max_length=255)
    vat_number = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(
        choices=(('Active', 'Active'), ('Inactive', 'Inactive')), max_length=255)
    # Utility Fields
    unique_id = models.CharField(null=True, blank=True, max_length=200)
    remarks = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = "tbl_client_informations"
        verbose_name = "Client Information"
        ordering = ('-created_at',)

    def get_absolute_url(self):
        return reverse('client-detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if self.created_at is None:
            created_at = timezone.localtime(timezone.now())
        if self.unique_id is None:
            self.unique = str(uuid4()).split('-')[4]
        self.slug = slugify('')
        # every time we save we will be re recreating out slug and updated_at
        # This is very neat way to keep track of date created and date updated
        self.updated_at = timezone.localtime(timezone.now())

        super(Client, self).save(*args, **kwargs)

    def __str__(self):
        return '{}{}{}'.format(self.client_name, self.province, self.unique_id)


class License(models.Model):
    license_no = models.CharField(max_length=255)
    front_image = models.ImageField(upload_to='employee_image', blank=True)
    back_image = models.ImageField(upload_to='employee_image', blank=True)

    class Meta:
        verbose_name = "License Information"


class Citizenship(models.Model):
    citizenship_no = models.CharField(max_length=255)
    front_image = models.ImageField(upload_to='employee_image', blank=True)
    back_image = models.ImageField(upload_to='employee_image', blank=True)

    class Meta:
        verbose_name = "Citizenship Information"


class Employee(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, null=True, blank=True)
    pin_number = models.IntegerField(blank=True, null=True)
    full_name = models.CharField(max_length=255)
    role = models.IntegerField(null=True, default=2, blank=True)
    contact_number = models.CharField(max_length=255)
    alt_contact_number = models.CharField(max_length=255, blank=True)
    emergency_contact_number = models.CharField(max_length=255)
    degination = models.CharField(max_length=255)
    image = models.ImageField(
        upload_to='employee_image', null=True, blank=True)
    license_info = models.OneToOneField(
        'License', on_delete=models.DO_NOTHING, blank=True, null=True)
    citizenship_info = models.OneToOneField(
        'Citizenship', on_delete=models.DO_NOTHING, blank=True, null=True)
    address = models.CharField(max_length=255)
    blood_group = models.CharField(max_length=255, blank=True, null=True)
    email_addrress = models.EmailField(max_length=255, blank=True, null=True)
    material_status = models.CharField(max_length=255, blank=True, null=True)
    employee_status = models.CharField(choices=(
        ('Active', 'Active'), ('Inactive', 'Inactive')), max_length=255, null=True, blank=True)

    class Meta:
        db_table = "sales_employee"
        verbose_name = "Employee Information"

    def __str__(self):
        return '{}'.format(self.full_name)
