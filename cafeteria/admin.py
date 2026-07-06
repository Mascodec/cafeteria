from django.contrib import admin

from .models import MenuItem, Order
from .models import MpesaTransaction


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "is_available")
    list_filter = ("is_available",)
    search_fields = ("name",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("user", "item", "quantity", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "item__name")
    actions = ["mark_as_preparing", "mark_as_ready", "mark_as_completed"]

    def mark_as_preparing(self, request, queryset):
        queryset.update(status="Preparing")

    mark_as_preparing.short_description = "Mark selected orders as preparing"

    def mark_as_ready(self, request, queryset):
        queryset.update(status="Ready")

    mark_as_ready.short_description = "Mark selected orders as ready"

    def mark_as_completed(self, request, queryset):
        queryset.update(status="Completed")

    mark_as_completed.short_description = "Mark selected orders as completed"


@admin.register(MpesaTransaction)
class MpesaTransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "phone_number", "amount", "result_code", "mpesa_receipt_number", "created_at")
    search_fields = ("phone_number", "checkout_request_id", "mpesa_receipt_number")
    list_filter = ("result_code", "created_at")


# Add a dashboard view into the Django admin site
from django.urls import path
from django.template.response import TemplateResponse


def _admin_dashboard_view(request):
    from .models import Order, MpesaTransaction

    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status="Pending").count()
    total_revenue = sum((o.total for o in Order.objects.filter(status="Completed")), 0)
    recent_orders = Order.objects.order_by("-created_at")[:10]
    recent_transactions = MpesaTransaction.objects.order_by("-created_at")[:10]

    context = {
        **admin.site.each_context(request),
        "title": "Site Dashboard",
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "total_revenue": total_revenue,
        "recent_orders": recent_orders,
        "recent_transactions": recent_transactions,
    }
    return TemplateResponse(request, "admin/dashboard.html", context)


# Insert dashboard URL at the top of admin urls
original_get_urls = admin.site.get_urls

def get_urls():
    urls = original_get_urls()
    my_urls = [path("dashboard/", admin.site.admin_view(_admin_dashboard_view), name="site-dashboard")]
    return my_urls + urls

admin.site.get_urls = get_urls
