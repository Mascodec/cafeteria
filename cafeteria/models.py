from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class MenuItem(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Preparing", "Preparing"),
        ("Ready", "Ready"),
        ("Completed", "Completed"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name="orders")
    quantity = models.PositiveIntegerField(default=1)
    payment_method = models.CharField(
        max_length=20,
        choices=[("Cash", "Cash"), ("Mpesa", "M-Pesa")],
        default="Cash",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.item.name}"

    @property
    def total(self):
        return self.item.price * self.quantity


class MpesaTransaction(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="mpesa_transactions", null=True, blank=True)
    phone_number = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    merchant_request_id = models.CharField(max_length=200, blank=True, null=True)
    checkout_request_id = models.CharField(max_length=200, blank=True, null=True)
    result_code = models.IntegerField(null=True, blank=True)
    result_desc = models.CharField(max_length=300, blank=True, null=True)
    mpesa_receipt_number = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"MPESA Transaction {self.checkout_request_id or self.pk} - {self.phone_number} - {self.amount}"
