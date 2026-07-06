import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_cafeteria.settings')

import django
django.setup()

from cafeteria.models import MenuItem

MenuItem.objects.all().delete()
MenuItem.objects.create(name='Chicken Rice Bowl', description='A hearty bowl with grilled chicken and vegetables.', price=12.50)
MenuItem.objects.create(name='Beef Burger', description='Classic beef burger with lettuce and cheese.', price=10.00)
MenuItem.objects.create(name='Veggie Pasta', description='Creamy pasta packed with fresh vegetables.', price=9.50)
print('seeded')
