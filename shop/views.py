from datetime import timedelta

from django.db.models import Q, F, Sum, IntegerField
from django.db.models.functions import TruncDate, TruncSecond
from django.utils import timezone
from django.views.generic import TemplateView

from .models import Product, Item, Category, Brand, Supplier


class NavBarMixin:
    @property
    def extra_context(self):
        return dict(
            categories=Category.objects.all(),
            brands=Brand.objects.all(),
            suppliers=Supplier.objects.all()
        )

    @property
    def q(self):
        params = self.request.GET
        q = Q()
        if "category__id" in params:
            q &= Q(category=params["category__id"])

        if "category__isnull" in params:
            q &= Q(category__isnull=int(params["category__isnull"]))

        if "brand__id" in params:
            q &= Q(brand=params["brand__id"])

        if "search" in params:
            search = params["search"]
            q &= Q(
                Q(name__iexact=search) |
                Q(brand__name__iexact=search) |
                Q(product_code=search)
            )

        return q

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search = self.request.GET.get("search")
        if search:
            context.update(search=search)
        return context


class Sale(NavBarMixin, TemplateView):
    template_name = "shop/sale.html"

    def get_context_data(self, **kwargs):
        products = Product.objects.filter(
            self.q
        ).order_by(
            "name"
        )
        context = super().get_context_data(**kwargs)
        context.update(products=products)
        return context

    def post(self, request, *args, **kwargs):
        amount = int(request.POST["amount"])
        product_id = int(request.POST["product__id"])
        selling_price = float(request.POST["price"])

        items = Item.objects.filter(
            product=product_id,
            selling_price__isnull=True
        ).order_by(
            "created_date"  # we sell oldest items first
        )[:amount]
        for item in items:
            item.selling_price = selling_price
            item.save(update_fields=["selling_price", "sold_date"])

        return self.get(request, *args, **kwargs)


class Warehouse(NavBarMixin, TemplateView):
    template_name = "shop/warehouse.html"

    def post(self, request, *args, **kwargs):
        amount = request.POST["amount"]
        product_id = request.POST["product__id"]
        cost = request.POST["cost"]
        supplier_id = request.POST["supplier__id"]

        Item.objects.bulk_create(
            Item(product_id=product_id, cost=cost, supplier_id=supplier_id)
            for _ in range(int(amount))
        )
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            products=Product.objects.filter(self.q),
            suppliers=Supplier.objects.all()
        )
        return context


class Report(NavBarMixin, TemplateView):

    template_name = "shop/report.html"

    @staticmethod
    def revise_q(q: Q):
        for i, child in enumerate(q.children.copy()):
            if hasattr(child, "children"):
                Report.revise_q(child)
                continue
            field, value = child
            q.children[i] = (f"product__{field}", value)
        return q

    @property
    def q(self):
        q = self.revise_q(super().q)

        params = self.request.GET
        if "date" in params:
            date = params["date"]
        else:
            date = timezone.now().date()
        q &= Q(sold_date__date=date)
        return q

    def get_context_data(self, **kwargs):
        items = Item.objects.filter(
            self.q
        ).values(
            "product"
        ).annotate(
            name=F("product__name"),
            sold_date=TruncSecond("sold_date"),
            cost=F("cost"),
            selling_price=F("selling_price"),
            profit=Sum(F("selling_price") - F("cost")),
            quantity=Sum(1, output_field=IntegerField())
        ).values(
            "name", "sold_date", "cost", "selling_price", "profit", "quantity"
        )

        dates = Item.objects.filter(
            sold_date__isnull=False
        ).annotate(
            date=TruncDate("sold_date")
        ).order_by(
            "-date"
        ).values_list(
            "date", flat=True
        ).distinct()

        total_profit = sum(item["profit"] for item in items)

        context = super().get_context_data(**kwargs)
        context.update(items=items, dates=dates, total_profit=total_profit)
        return context


class Analytics(NavBarMixin, TemplateView):

    template_name = "shop/analytics.html"

    @property
    def q(self):
        q = Report.revise_q(super().q)
        month_ago = timezone.now() - timedelta(days=30)
        q &= Q(sold_date__gte=month_ago.date())
        return q

    def get_context_data(self, **kwargs):
        queryset = Item.objects.filter(self.q)
        items = queryset.values(
            "product__name"
        ).annotate(
            product=F("product__name"),
            quantity=Sum(1, output_field=IntegerField()),
            profit=Sum(F("selling_price") - F("cost"))
        ).order_by(
            "-profit"
        )

        total_profit = queryset.aggregate(
            total_profit=Sum(F("selling_price") - F("cost"))
        )["total_profit"]

        context = super().get_context_data(**kwargs)
        context.update(items=items, total_profit=total_profit)
        return context
