import random
from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from mill.constants import CITIES
from mill.models import Product, Order, Profile


class Command(BaseCommand):
    help = 'Seeds the flour catalog, a demo admin/customer account, and sample orders for the dashboard charts.'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Clearing existing Product, demo Order, and demo account records...'))
        Order.objects.all().delete()
        Product.objects.all().delete()
        User.objects.filter(username__in=['admin', 'demo_customer']).delete()

        self.stdout.write('Seeding flour catalog...')
        products = [
            {'name': 'Whole Wheat Flour', 'icon': '🌾', 'rate_per_kg': 130,
             'tag': Product.TAG_SPECIAL,
             'description': '100% stone-ground whole wheat, high fiber, no preservatives. Our signature.'},
            {'name': 'Maize Flour', 'icon': '🌽', 'rate_per_kg': 150,
             'tag': Product.TAG_GLUTEN_FREE,
             'description': 'Fine ground maize flour, perfect for makki di roti, gluten-free option.'},
            {'name': 'Multigrain Flour', 'icon': '🌾', 'rate_per_kg': 240,
             'tag': Product.TAG_POWER_MIX,
             'description': 'Blend of wheat, maize, barley, and chickpea — protein rich.'},
            {'name': 'Fine White Flour', 'icon': '🌾', 'rate_per_kg': 140,
             'tag': Product.TAG_PREMIUM,
             'description': 'Sifted stone-ground flour, light texture for baking & naan.'},
            {'name': 'Barley Flour', 'icon': '🌾', 'rate_per_kg': 180,
             'tag': Product.TAG_STANDARD,
             'description': 'Nutritious barley flour, ground fresh from premium quality jau.'},
            {'name': 'Chickpea Flour (Besan)', 'icon': '🫘', 'rate_per_kg': 200,
             'tag': Product.TAG_PREMIUM,
             'description': 'Pure ground chana besan, stone-milled for authentic flavor.'},
            {'name': 'Oat Flour', 'icon': '🌾', 'rate_per_kg': 260,
             'tag': Product.TAG_GLUTEN_FREE,
             'description': 'Finely milled oats, a light and nutritious everyday flour.'},
            {'name': 'Rye Flour', 'icon': '🌾', 'rate_per_kg': 220,
             'tag': Product.TAG_STANDARD,
             'description': 'Stone-ground rye flour with a distinctive, earthy flavor.'},
        ]
        created_products = [Product.objects.create(is_available=True, **p) for p in products]
        self.stdout.write(self.style.SUCCESS(f'Created {len(created_products)} products.'))

        self.stdout.write('Creating demo staff (admin) account...')
        admin_user = User.objects.create_superuser('admin', 'admin@rabbaniflour.pk', 'admin123')
        admin_user.first_name = 'Mill'
        admin_user.last_name = 'Admin'
        admin_user.save()
        self.stdout.write(self.style.SUCCESS('Admin login -> username: admin / password: admin123'))

        self.stdout.write('Creating demo customer account...')
        customer = User.objects.create_user('demo_customer', 'demo@rabbaniflour.pk', 'demo12345')
        customer.first_name = 'Demo'
        customer.last_name = 'Customer'
        customer.save()
        Profile.objects.create(user=customer, phone='0300-1234567', city='Rawalpindi')
        self.stdout.write(self.style.SUCCESS('Demo customer login -> username: demo_customer / password: demo12345'))

        self.stdout.write('Seeding sample orders for dashboard charts...')
        statuses = [c for c, _ in Order.STATUS_CHOICES]
        weights = [0.4, 0.15, 0.15, 0.15, 0.15]
        now = timezone.now()
        created_orders = 0
        for days_ago in range(6, -1, -1):
            for _ in range(random.randint(2, 5)):
                product = random.choice(created_products)
                city = random.choice(CITIES)
                weight_kg = random.choice([2, 5, 10, 15, 20])
                status = random.choices(statuses, weights=weights, k=1)[0]
                order = Order(
                    customer=customer,
                    product=product,
                    weight_kg=weight_kg,
                    destination_city=city,
                    delivery_address=f'Demo address, {city}',
                    phone=customer.profile.phone,
                    status=status,
                )
                order.save()
                order_time = now - timedelta(days=days_ago, hours=random.randint(0, 23))
                Order.objects.filter(pk=order.pk).update(created_at=order_time, updated_at=order_time)
                created_orders += 1
        self.stdout.write(self.style.SUCCESS(f'Created {created_orders} demo orders.'))

        self.stdout.write(self.style.SUCCESS('Rabbani Stone-Ground database seeded successfully.'))
