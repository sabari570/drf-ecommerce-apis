from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()


def get_catgegory_icon_image_path(instance, filename):
    return f"products/category/icons/{instance.name}/{filename}"


def get_category_image_path(instance, filename):
    return f"products/category/images/{instance.name}/{filename}"


class ProductCategory(models.Model):
    '''
    This is the Product category model that has the various categories for the products
    '''
    name = models.CharField(_("Category name"), max_length=100)
    icon = models.ImageField(
        upload_to=get_catgegory_icon_image_path, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Product Category")
        verbose_name_plural = _("Product Categories")

    def __str__(self):
        return self.name


def get_default_product_category():
    return ProductCategory.objects.get_or_create(name="Others")[0]


class Product(models.Model):
    '''
    This is the product model
    '''
    seller = models.ForeignKey(
        User, related_name='products', on_delete=models.CASCADE)
    category = models.ForeignKey(ProductCategory, related_name='categories',
                                 on_delete=models.SET(get_default_product_category))
    name = models.CharField(max_length=200)
    desc = models.CharField(max_length=300)
    image = models.ImageField(upload_to=get_category_image_path, blank=True)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    quantity = models.IntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.name
