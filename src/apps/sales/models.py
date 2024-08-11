from django.db import models
from django.utils.translation import gettext as _
from django.template.defaultfilters import slugify
from apps.hrm_system.models import Client, Employee

from apps.sales.port_id.models import UniqueUserId
from django.conf import settings

from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from uuid import uuid4


class Product(models.Model):
    port = models.ForeignKey(
        UniqueUserId,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="user portfolio id",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True
    )
    # Slave Model
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=25, null=True, blank=True)
    size = models.CharField(max_length=10, null=True, blank=True)
    status = models.BooleanField(default=True)
    # Utility fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    unique_id = models.CharField(null=True, blank=True, max_length=100)
    slug = models.SlugField(max_length=500, unique=True, null=True, blank=True)

    class Meta:
        managed = True
        db_table = "tbl_Product_informations"
        verbose_name = "Product Information"
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=["name", "user"], name="unique_product_per_user"
            )
        ]

    def __str__(self):
        return "{}{}".format(self.name, self.unique_id)

    def get_absolute_url(self):
        return reverse("product-detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if self.created_at is None:
            created_at = timezone.localtime(timezone.now())
        if self.unique_id is None:
            self.unique_id = str(uuid4()).split("-")[4]
            self.slug = slugify("{}{}".format(self.name, self.unique_id))
        self.slug = slugify("{}-{}".format(self.name, self.unique_id))
        # Every time we save, we will be recreating our slug and updated_at
        # This is a neat way to keep track of date created and date updated
        self.updated_at = timezone.localtime(timezone.now())

        super(Product, self).save(*args, **kwargs)


# class Bill(models.Model):
#     bill_no = models.IntegerField(unique=True)


class Invoice(models.Model):
    port = models.ForeignKey(
        UniqueUserId, on_delete=models.CASCADE, null=True, blank=True
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True
    )
    # MAIN MODEL , MASTER MODEL
    # who is the client and are the product that fit into it.
    TERMS = [
        ("7 days", "7 days"),
        ("14 days", "14 days"),
        ("30 days", "30 days"),
        ("45 days", "45 days"),
        ("60 days", "60 days"),
        ("90 days", "90 days"),
    ]
    STATUS = [("CURRENT", "CURRENT"), ("OVERDUE", "OVERDUE"), ("PAID", "PAID")]
    # Basic Field
    number = models.CharField(max_length=100, null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    remarks = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payment_terms = models.CharField(
        choices=TERMS, max_length=255, null=True, blank=True, default="7 days"
    )
    payment_status = models.CharField(
        choices=STATUS, max_length=255, null=True, blank=True
    )
    # Related Fields
    client = models.ForeignKey(
        Client, blank=True, null=True, on_delete=models.DO_NOTHING
    )
    employee = models.ForeignKey(Employee, on_delete=models.DO_NOTHING)
    bill_number = models.IntegerField("Bill")

    class Meta:
        managed = True
        db_table = "tbl_invoice"
        verbose_name = "Invoice"
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=["bill_number", "user"], name="unique_bill_number_per_user"
            )
        ]


class InvoiceProduct(models.Model):
    port = models.ForeignKey(
        UniqueUserId, on_delete=models.CASCADE, null=True, blank=True
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True
    )
    # Fields for product details
    product = models.ForeignKey(
        "Product", blank=True, null=True, on_delete=models.DO_NOTHING
    )
    quantity = models.PositiveIntegerField()
    # Foreign Key to Invoice
    invoice = models.ForeignKey(
        "Invoice", on_delete=models.CASCADE, related_name="products"
    )

    # PRODUCT QUANTITY PRICE INVOICE
    # BARLEY    10       90      1
    # MIXED     20       131.75  1
    # SUGARFR   20       131.75  1
    # CHANNA    18       127     1

    def get_total(self):
        return self.quantity * self.price


class Setting(models.Model):
    port = models.ForeignKey(
        UniqueUserId, on_delete=models.CASCADE, null=True, blank=True
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True
    )
    PROVINCES = [
        ("Proviance1", "Proviance1"),
        ("Proviance2", "Proviance2"),
        ("Proviance3", "Proviance3"),
    ]

    client_name = models.CharField(max_length=255)
    address_line_1 = models.CharField(max_length=200)
    client_logo = models.ImageField(
        default="default_logo.jpg", upload_to="company_logos"
    )
    # this will create new folder called company logos.
    # we do this because we do not want to upload everything into same place.
    province = models.CharField(choices=PROVINCES, blank=True, max_length=100)
    postal_code = models.CharField(null=True, blank=True, max_length=100)
    # Slug is very important because  it helps in routing and its good for seo.
    slug = models.SlugField(null=True, blank=True, max_length=10)
    contact_number = models.CharField(max_length=255)
    email_addrress = models.CharField(null=True, blank=True, max_length=100)

    # Utility Fields
    unique_id = models.CharField(null=True, blank=True, max_length=200)
    remarks = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}{}{}".format(self.clientName, self.proviance, self.unique_id)

    def get_absolute_url(self):
        return reverse("settings-detail", kwargs={"slug": self.slug})
