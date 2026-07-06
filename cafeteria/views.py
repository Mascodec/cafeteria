from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required

import requests
import base64
from datetime import datetime

from .forms import CustomUserCreationForm, OrderQuantityForm
from .models import MenuItem, Order


def home(request):
    # If a staff user opens the site, send them to the site dashboard
    if request.user.is_authenticated and getattr(request.user, "is_staff", False):
        return redirect("admin_dashboard")
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
            payment_method = form.cleaned_data["payment_method"]
            status = "Completed" if payment_method == "Cash" else "Pending"
            Order.objects.create(
                user=request.user,
                item=item,
                quantity=quantity,
                payment_method=payment_method,
                status=status,
            )
            if payment_method == "Cash":
                messages.success(request, "Cash payment selected — order completed successfully.")
            else:
                messages.success(request, "Order placed. Use M-Pesa on the orders page to pay.")
            return redirect("orders")
    else:
        form = OrderQuantityForm()
    return render(request, "order.html", {"item": item, "form": form})


@login_required
def orders_view(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "orders.html", {"orders": orders})


def _get_mpesa_access_token():
    consumer_key = getattr(settings, "MPESA_CONSUMER_KEY", None)
    consumer_secret = getattr(settings, "MPESA_CONSUMER_SECRET", None)
    if not consumer_key or not consumer_secret:
        return None
    auth = requests.auth.HTTPBasicAuth(consumer_key, consumer_secret)
    env = getattr(settings, "MPESA_ENV", "sandbox")
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    if env == "production":
        url = "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    r = requests.get(url, auth=auth)
    if r.status_code == 200:
        return r.json().get("access_token")
    return None


@login_required
def mpesa_stk_push(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    if request.method != "POST":
        return redirect("orders")

    phone = request.POST.get("phone")
    if not phone:
        messages.error(request, "Please provide a phone number.")
        return redirect("orders")

    # normalize phone to E.164 for Kenya (254)
    phone_clean = phone.strip()
    if phone_clean.startswith("0"):
        phone_clean = "254" + phone_clean[1:]
    if phone_clean.startswith("+"):
        phone_clean = phone_clean[1:]

    amount = float(order.item.price) * order.quantity

    token = _get_mpesa_access_token()
    if not token:
        messages.error(request, "Unable to get MPESA access token. Configure credentials.")
        return redirect("orders")

    shortcode = getattr(settings, "MPESA_SHORTCODE", "174379")
    passkey = getattr(settings, "MPESA_PASSKEY", "")
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password = base64.b64encode(f"{shortcode}{passkey}{timestamp}".encode()).decode()

    env = getattr(settings, "MPESA_ENV", "sandbox")
    stk_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    if env == "production":
        stk_url = "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

    callback_url = getattr(settings, "MPESA_CALLBACK_URL", None)
    if not callback_url:
        messages.error(request, "MPESA callback URL not configured. Set MPESA_CALLBACK_URL env var to your ngrok URL plus /mpesa/callback/.")
        return redirect("orders")

    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(amount),
        "PartyA": phone_clean,
        "PartyB": shortcode,
        "PhoneNumber": phone_clean,
        "CallBackURL": callback_url,
        "AccountReference": f"order_{order.pk}",
        "TransactionDesc": f"Payment for order {order.pk}"
    }

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    resp = requests.post(stk_url, json=payload, headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        # store transaction
        from .models import MpesaTransaction

        tx = MpesaTransaction.objects.create(
            order=order,
            phone_number=phone_clean,
            amount=amount,
            merchant_request_id=data.get("MerchantRequestID"),
            checkout_request_id=data.get("CheckoutRequestID")
        )
        messages.success(request, "STK Push initiated. Check your phone to complete payment.")
        return redirect("orders")
    else:
        messages.error(request, f"MPESA STK Push failed: {resp.text}")
        return redirect("orders")


@csrf_exempt
def mpesa_callback(request):
    # Safaricom will POST the result here; update transaction and order status
    if request.method != "POST":
        return HttpResponse(status=405)
    try:
        data = request.body.decode("utf-8")
        payload = requests.utils.json.loads(data)
    except Exception:
        return HttpResponse(status=400)

    # expected structure: {'Body': {'stkCallback': { ... }}}
    body = payload.get("Body", {})
    stk = body.get("stkCallback", {})
    checkout_request_id = stk.get("CheckoutRequestID")
    merchant_request_id = stk.get("MerchantRequestID")
    result_code = stk.get("ResultCode")
    result_desc = stk.get("ResultDesc")

    # extract receipt and amount if available
    callback_metadata = stk.get("CallbackMetadata", {})
    items = callback_metadata.get("Item", []) if callback_metadata else []
    receipt = None
    amount = None
    for it in items:
        name = it.get("Name")
        if name == "MpesaReceiptNumber":
            receipt = it.get("Value")
        if name == "Amount":
            amount = it.get("Value")

    from .models import MpesaTransaction
    try:
        tx = MpesaTransaction.objects.filter(checkout_request_id=checkout_request_id).first()
        if tx:
            tx.result_code = result_code
            tx.result_desc = result_desc
            tx.mpesa_receipt_number = receipt
            tx.save()
            if result_code == 0 and tx.order:
                tx.order.status = "Completed"
                tx.order.save()
    except Exception:
        # swallow errors but return 200 so Safaricom doesn't retry aggressively
        pass

    return JsonResponse({"status": "received"})


@staff_member_required
def admin_dashboard(request):
    from .models import Order, MpesaTransaction

    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status="Pending").count()
    total_revenue = sum((o.total for o in Order.objects.filter(status="Completed")), 0)
    recent_orders = Order.objects.order_by("-created_at")[:10]
    recent_transactions = MpesaTransaction.objects.order_by("-created_at")[:10]

    return render(request, "admin_dashboard.html", {
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "total_revenue": total_revenue,
        "recent_orders": recent_orders,
        "recent_transactions": recent_transactions,
    })
