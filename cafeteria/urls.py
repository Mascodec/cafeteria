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
]
