from django.contrib.auth.models import User
from django.db import models


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
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.item.name}"
