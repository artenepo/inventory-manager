from typing import Optional

from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class Supplier(models.Model):
    class Meta:
        verbose_name = _("Supplier")
        verbose_name_plural = _("Suppliers")
        db_table = "supplier"

    name = models.CharField(_("Name"), max_length=150)
    phone = models.CharField(_("Phone"), max_length=20)
    notes = models.TextField(_("Notes"), max_length=500, blank=True, null=True)

    def __str__(self) -> str:
        return str(self.name)


class Brand(models.Model):
    class Meta:
        verbose_name = _("Brand")
        verbose_name_plural = _("Brands")
        db_table = "brand"

    name = models.CharField(_("Name"), max_length=150)

    def __str__(self) -> str:
        return str(self.name)


class Category(models.Model):
    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        db_table = "category"

    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return str(self.name)


class Product(models.Model):
    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        db_table = "product"

    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, verbose_name=_("brand"))
    name = models.CharField(_("Name"), max_length=250, null=False)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name=_("category"))
    product_code = models.CharField(_("Product code"), max_length=100)
    margin = models.FloatField(_("Margin"))

    @property
    def quantity(self) -> int:
        return self.items.filter(selling_price__isnull=True).count()

    @property
    def price(self) -> float:
        available_items = list(self.items.filter(sold_date__isnull=True))
        if available_items:
            return max(item.price for item in available_items)

    @property
    def cost(self) -> float:
        if self.items.exists():
            return self.items.order_by("-created_date").first().cost

    def __str__(self) -> str:
        return str(self.name)


class Item(models.Model):
    class Meta:
        db_table = "item"
        verbose_name = _("Item")
        verbose_name_plural = _("Items")

    created_date = models.DateTimeField(_("Date created"), auto_now=True, editable=False)
    updated_date = models.DateTimeField(_("Date updated"), auto_now_add=True, editable=False)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="items", verbose_name=_("product"))
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name="items", verbose_name=_("supplier"))
    cost = models.FloatField(_("Cost"))
    selling_price = models.FloatField(_("Selling price"), null=True, blank=True)
    sold_date = models.DateTimeField(_("Date of the sale"), null=True, blank=True)

    @property
    def status(self) -> str:
        return _("Available") if not self.selling_price else _("Sold")

    @property
    def price(self) -> Optional[float]:
        if self.product.margin and self.cost:
            price = self.cost + (self.cost / 100 * self.product.margin)
            return round(price)

    @property
    def profit(self) -> Optional[float]:
        if self.selling_price:
            return self.selling_price - self.cost

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.selling_price and not self.sold_date:
            self.sold_date = timezone.now()
        super().save(force_insert, force_update, using, update_fields)

    def __str__(self) -> str:
        return f"{self.product} ({self.cost})"
