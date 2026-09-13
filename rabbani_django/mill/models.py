import random

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone

from .constants import CITIES, MILL_CITY, calculate_order_fare


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=50, choices=[(c, c) for c in CITIES], default=MILL_CITY)

    def __str__(self):
        return f"Profile: {self.user.get_username()}"


class Product(models.Model):
    TAG_SPECIAL = 'SPECIAL'
    TAG_GLUTEN_FREE = 'GLUTEN_FREE'
    TAG_PREMIUM = 'PREMIUM'
    TAG_POWER_MIX = 'POWER_MIX'
    TAG_STANDARD = 'STANDARD'

    TAG_CHOICES = [
        (TAG_SPECIAL, 'Rabbani Special'),
        (TAG_GLUTEN_FREE, 'Gluten-Free'),
        (TAG_PREMIUM, 'Premium'),
        (TAG_POWER_MIX, 'Power Mix'),
        (TAG_STANDARD, 'Standard'),
    ]

    name = models.CharField(max_length=150)
    icon = models.CharField(max_length=8, default='🌾')
    description = models.TextField(blank=True)
    rate_per_kg = models.DecimalField(max_digits=8, decimal_places=2)
    tag = models.CharField(max_length=20, choices=TAG_CHOICES, default=TAG_STANDARD)
    is_available = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} (Rs. {self.rate_per_kg}/kg)"


class Order(models.Model):
    STATUS_PENDING = 'PENDING'
    STATUS_MILLING = 'MILLING'
    STATUS_PACKED = 'PACKED'
    STATUS_ON_THE_WAY = 'ON_THE_WAY'
    STATUS_DELIVERED = 'DELIVERED'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_MILLING, 'Milling in Progress'),
        (STATUS_PACKED, 'Packed'),
        (STATUS_ON_THE_WAY, 'On the Way'),
        (STATUS_DELIVERED, 'Delivered'),
    ]

    tracking_number = models.CharField(max_length=40, unique=True, editable=False, blank=True)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='orders')
    weight_kg = models.DecimalField(max_digits=6, decimal_places=2)
    destination_city = models.CharField(max_length=50, choices=[(c, c) for c in CITIES], default=MILL_CITY)
    delivery_address = models.TextField()
    phone = models.CharField(max_length=20, blank=True)

    product_cost = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0)
    delivery_fare = models.DecimalField(max_digits=8, decimal_places=2, editable=False, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.tracking_number} - {self.customer}"

    def generate_tracking_number(self):
        stamp = timezone.now().strftime('%y%m%d%H%M%S')
        suffix = random.randint(10, 99)
        return f"RB-{stamp}{suffix}"

    def save(self, *args, **kwargs):
        if not self.tracking_number:
            new_id = self.generate_tracking_number()
            while Order.objects.filter(tracking_number=new_id).exists():
                new_id = self.generate_tracking_number()
            self.tracking_number = new_id

        self.product_cost = self.product.rate_per_kg * self.weight_kg
        self.delivery_fare = calculate_order_fare(self.destination_city)
        self.total_amount = self.product_cost + self.delivery_fare

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('mill:track_order_page', kwargs={'tracking_number': self.tracking_number})

    def status_badge_class(self):
        return {
            self.STATUS_PENDING: 'status-pending',
            self.STATUS_MILLING: 'status-milling',
            self.STATUS_PACKED: 'status-packed',
            self.STATUS_ON_THE_WAY: 'status-transit',
            self.STATUS_DELIVERED: 'status-delivered',
        }.get(self.status, 'status-pending')


class ContactMessage(models.Model):
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.created_at:%d %b %Y})"
