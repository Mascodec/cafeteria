from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CustomUserCreationForm, OrderQuantityForm
from .models import MenuItem, Order


def home(request):
    return render(request, "home.html")


def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully.")
            return redirect("menu")
    else:
        form = CustomUserCreationForm()
    return render(request, "register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Logged in successfully.")
            return redirect("menu")
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.info(request, "You logged out.")
    return redirect("home")


def menu_view(request):
    items = MenuItem.objects.filter(is_available=True)
    return render(request, "menu.html", {"items": items})


@login_required
def order_food(request, pk):
    item = get_object_or_404(MenuItem, pk=pk)
    if request.method == "POST":
        form = OrderQuantityForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data["quantity"]
            Order.objects.create(user=request.user, item=item, quantity=quantity)
            messages.success(request, "Order placed successfully.")
            return redirect("orders")
    else:
        form = OrderQuantityForm()
    return render(request, "order.html", {"item": item, "form": form})


@login_required
def orders_view(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "orders.html", {"orders": orders})
