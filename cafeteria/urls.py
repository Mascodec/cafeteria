from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("menu/", views.menu_view, name="menu"),
    path("order/<int:pk>/", views.order_food, name="order_food"),
    path("orders/", views.orders_view, name="orders"),
    path("mpesa/stk_push/<int:order_id>/", views.mpesa_stk_push, name="mpesa_stk_push"),
    path("mpesa/callback/", views.mpesa_callback, name="mpesa_callback"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("dashboard/", views.admin_dashboard, name="dashboard"),
]
