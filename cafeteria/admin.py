from django.contrib import admin

from .models import MenuItem, Order


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
