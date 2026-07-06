# Smart Cafeteria

A Django web app for a smart cafeteria where customers can register, log in, view meals, place orders, and track their orders. Admin users can update order status from the Django admin panel.

## Features
- Customer registration and login
- Beautiful landing page
- Menu page for available meals
- Order placement flow
- Customer order history
- Admin panel for updating order status

## Project Structure
- cafeteria/models.py - MenuItem and Order models
- cafeteria/views.py - Home, auth, menu, and order logic
- cafeteria/urls.py - App routes
- cafeteria/admin.py - Admin registration and order status actions
- templates/ - HTML pages
- static/css/style.css - Styling for the site

## Run locally
```bash
cd C:\Users\PC\smart-cafeteria
python manage.py runserver
```

Then open:
- Home page: http://127.0.0.1:8000/
- Admin panel: http://127.0.0.1:8000/admin/

## Admin credentials
- Username: admin
- Password: admin123

## Create sample menu items
If needed, run:
```bash
python manage.py shell -c "from cafeteria.models import MenuItem; MenuItem.objects.create(name='Chicken Rice Bowl', description='A hearty bowl with grilled chicken and vegetables.', price=12.50); MenuItem.objects.create(name='Beef Burger', description='Classic beef burger with lettuce and cheese.', price=10.00); MenuItem.objects.create(name='Veggie Pasta', description='Creamy pasta packed with fresh vegetables.', price=9.50)"
```
"# cafeteria" 
