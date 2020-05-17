from django.urls import path

from shop.views import Warehouse, Sale, Report, Analytics

urlpatterns = [
    path("", Sale.as_view()),
    path("warehouse", Warehouse.as_view()),
    path("report", Report.as_view()),
    path("analytics", Analytics.as_view()),
]
