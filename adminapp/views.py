from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from .models import Tbl_Admin

def admin_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            admin = Tbl_Admin.objects.get(username=username, password=password)
            request.session['admin_id'] = admin.id
            # Redirect to admin dashboard or home page after login
            return redirect('admin_dashboard')
        except Tbl_Admin.DoesNotExist:
            return render(request, 'login.html', {'error': 'Invalid username or password'})

    # GET request: just show login form
    return render(request, 'login.html')


def admin_dashboard(request):
    return render(request,'dashboard.html')




from django.shortcuts import render, redirect
from .models import Category

def add_category_view(request):
    error = ""
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            if not Category.objects.filter(name__iexact=name).exists():
                Category.objects.create(name=name)
                return redirect('category_list')
            else:
                error = "Category already exists."
        else:
            error = "Name field cannot be empty."

    return render(request, 'add_category.html', {'error': error})


def category_list_view(request):
    categories = Category.objects.all()
    return render(request, 'category_list.html', {'categories': categories})


from django.shortcuts import render, redirect, get_object_or_404
from .models import Category

# Edit Category
def edit_category_view(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        new_name = request.POST.get('name')
        if new_name:
            category.name = new_name
            category.save()
            return redirect('category_list')
        else:
            error = "Name cannot be empty."
            return render(request, 'edit_category.html', {'category': category, 'error': error})

    return render(request, 'edit_category.html', {'category': category})


# Delete Category
def delete_category_view(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        category.delete()
        return redirect('category_list')

    # Confirmation page for GET request
    return render(request, 'delete_category.html', {'category': category})


from django.shortcuts import render, redirect, get_object_or_404
from .models import Category, MenuItem
def add_menu_item(request):
    categories = Category.objects.all()

    if request.method == 'POST':
        names = request.POST.getlist('name')
        rates = request.POST.getlist('rate')
        items_per_plate = request.POST.getlist('item_per_plate')
        categories_selected = request.POST.getlist('category')
        images = request.FILES.getlist('image')

        for i in range(len(names)):
            TblMenuItem.objects.create(
                name=names[i],
                rate=rates[i],
                item_per_plate=items_per_plate[i],
                category_id=categories_selected[i],
                image=images[i] if i < len(images) else None
            )

        return redirect('menu_list')

    return render(request, 'add_menu.html', {'categories': categories})



# views.py
from datetime import datetime
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import TblMenuItem, TblDailyMenu

def add_daily_menu(request):
    items = TblMenuItem.objects.all()  # get all menu items

    if request.method == 'POST':
        date_str = request.POST.get('date')
        if not date_str:
            messages.error(request, "Please select a date.")
            return redirect('add_daily_menu')

        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        weekday = date_obj.strftime('%A')

        if weekday == 'Sunday':
            messages.error(request, "Menu not available for Sunday.")
            return redirect('add_daily_menu')

        selected_items = list(map(int, request.POST.getlist('items')))  # ensure integers
        if not selected_items:
            messages.error(request, "Please select at least one menu item.")
            return redirect('add_daily_menu')

        daily_menu, created = TblDailyMenu.objects.get_or_create(date=date_obj)
        daily_menu.items.set(selected_items)  # assign correct items
        messages.success(request, f"Daily menu for {weekday} ({date_obj}) saved successfully!")
        return redirect('daily_menu_list')

    return render(request, 'add_daily_menu.html', {'items': items})


from django.shortcuts import get_object_or_404

def edit_daily_menu(request, id):
    daily_menu = get_object_or_404(TblDailyMenu, id=id)
    items = TblMenuItem.objects.all()

    if request.method == 'POST':
        date_str = request.POST.get('date')
        if not date_str:
            messages.error(request, "Please select a date.")
            return redirect('edit_daily_menu', id=id)

        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        weekday = date_obj.strftime('%A')

        if weekday == 'Sunday':
            messages.error(request, "Menu not available for Sunday.")
            return redirect('edit_daily_menu', id=id)

        selected_items = list(map(int, request.POST.getlist('items')))
        if not selected_items:
            messages.error(request, "Please select at least one menu item.")
            return redirect('edit_daily_menu', id=id)

        daily_menu.date = date_obj
        daily_menu.items.set(selected_items)
        daily_menu.save()
        messages.success(request, f"Daily menu for {weekday} ({date_obj}) updated successfully!")
        return redirect('daily_menu_list')

    return render(request, 'edit_daily_menu.html', {
        'menu': daily_menu,
        'items': items,
    })


def delete_daily_menu(request, id):
    daily_menu = get_object_or_404(TblDailyMenu, id=id)
    if request.method == 'POST':
        daily_menu.delete()
        messages.success(request, "Daily menu deleted successfully.")
        return redirect('daily_menu_list')
    








def daily_menu_list(request):
    menus = TblDailyMenu.objects.all().order_by('-date')
    return render(request, 'daily_menu_list.html', {'menus': menus})



def menu_list(request):
    items = TblMenuItem.objects.all()
    return render(request, 'menu_list.html', {'items': items})


def delete_menu_item(request, item_id):
    item = get_object_or_404(TblMenuItem, id=item_id)
    item.delete()
    return redirect('menu_list')


from django.shortcuts import render, get_object_or_404, redirect
from .models import MenuItem, Category

def edit_menu_item(request, item_id):
    item = get_object_or_404(TblMenuItem, id=item_id)
    categories = Category.objects.all()

    if request.method == 'POST':
        item.name = request.POST.get('name')
        item.rate = request.POST.get('rate')
        item.item_per_plate = request.POST.get('item_per_plate')
        item.category_id = request.POST.get('category')

        if request.FILES.get('image'):
            item.image = request.FILES['image']

        item.save()
        return redirect('menu_list')

    return render(request, 'edit_menu.html', {
        'item': item,
        'categories': categories
    })


from django.shortcuts import render, redirect, get_object_or_404
from .models import TblTimeSlot, Category
from datetime import datetime, timedelta
from django.shortcuts import render
from django.db.models import Case, When, IntegerField
from .models import TblTimeSlot
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from datetime import datetime, timedelta
from .models import TblTimeSlot, Category
from django.db.models import Case, When, IntegerField

# -------------------------------
# List all time slots
# -------------------------------
def time_slot_list(request):
    # Custom order: Breakfast → Lunch → Evening Snacks → Dinner → others
    order_priority = Case(
        When(category__name='Breakfast', then=1),
        When(category__name='Lunch', then=2),
        When(category__name='Evening Snacks', then=3),
        When(category__name='Dinner', then=4),
        default=5,
        output_field=IntegerField(),
    )

    slots = TblTimeSlot.objects.all().order_by(order_priority, 'start_time')
    return render(request, 'time_slot_list.html', {'slots': slots})


# -------------------------------
# Add time slots (manual or auto 30-min slots)
# -------------------------------
def add_time_slot(request):
    categories = Category.objects.all()

    if request.method == 'POST':
        # Example: automatic slot generation
        meal_slots = {
            'Breakfast': ('08:00', '11:00'),
            'Lunch': ('12:00', '15:00'),
            'Evening Snacks': ('16:00', '18:00'),
            'Dinner': ('19:00', '22:00'),
        }

        for meal_name, (start_str, end_str) in meal_slots.items():
            # Safely get or create category
            category, created = Category.objects.get_or_create(name=meal_name)

            start_time = datetime.strptime(start_str, '%H:%M')
            end_time = datetime.strptime(end_str, '%H:%M')

            current_time = start_time
            while current_time < end_time:
                slot_start = current_time.time()
                slot_end = (current_time + timedelta(minutes=30)).time()
                if slot_end > end_time.time():
                    slot_end = end_time.time()

                TblTimeSlot.objects.create(
                    category=category,
                    start_time=slot_start,
                    end_time=slot_end
                )
                current_time += timedelta(minutes=30)

        messages.success(request, "Time slots added successfully!")
        return redirect('time_slot_list')

    return render(request, 'add_time_slot.html', {'categories': categories})


# -------------------------------
# Edit a time slot
# -------------------------------
def edit_time_slot(request, slot_id):
    slot = get_object_or_404(TblTimeSlot, id=slot_id)
    categories = Category.objects.all()

    if request.method == 'POST':
        category_id = request.POST.get('category')
        slot.category = Category.objects.get(id=category_id)
        slot.start_time = request.POST.get('start_time')
        slot.end_time = request.POST.get('end_time')
        slot.save()

        messages.success(request, "Time slot updated successfully!")
        return redirect('time_slot_list')

    return render(request, 'edit_time_slot.html', {'slot': slot, 'categories': categories})


# -------------------------------
# Delete a time slot
# -------------------------------
def delete_time_slot(request, slot_id):
    slot = get_object_or_404(TblTimeSlot, id=slot_id)
    slot.delete()

    messages.success(request, "Time slot deleted successfully!")
    return redirect('time_slot_list')


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Table

# Show all tables
def table_list(request):
    tables = Table.objects.all()
    return render(request, 'table_list.html', {'tables': tables})

# Add new table
def add_table(request):
    if request.method == 'POST':
        table_name = request.POST.get('table_name')
        number_of_seats = int(request.POST.get('number_of_seats'))

        try:
            table = Table.objects.create(table_name=table_name, number_of_seats=number_of_seats)
            messages.success(request, f"Table '{table_name}' created with {number_of_seats} seats (₹5 each).")
            return redirect('table_list')
        except Exception as e:
            messages.error(request, str(e))

    return render(request, 'add_table.html')

# Edit table
def edit_table(request, table_id):
    table = get_object_or_404(Table, id=table_id)

    if request.method == 'POST':
        table_name = request.POST.get('table_name')
        number_of_seats = int(request.POST.get('number_of_seats'))

        try:
            table.table_name = table_name
            table.number_of_seats = number_of_seats
            table.save()
            messages.success(request, f"Table '{table_name}' updated to {number_of_seats} seats.")
            return redirect('table_list')
        except Exception as e:
            messages.error(request, str(e))

    return render(request, 'edit_table.html', {'table': table})

# Delete table
def delete_table(request, table_id):
    table = get_object_or_404(Table, id=table_id)
    table.delete()
    messages.success(request, f"Table '{table.table_name}' deleted successfully!")
    return redirect('table_list')

# View seats of a table
def view_seats(request, table_id):
    table = get_object_or_404(Table, id=table_id)
    seats = table.seats.all()
    return render(request, 'seat_list.html', {'table': table, 'seats': seats})




from django.shortcuts import render
from userapp.models import Order

def admin_all_orders(request):
    # Show the latest orders first — newest date (and id) at the top
    orders = Order.objects.all().order_by('-date', '-id')
    return render(request, 'admin_all_orders.html', {'orders': orders})

def admin_order_details(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'admin_order_details.html', {'order': order})


from django.shortcuts import render, redirect
from django.contrib import messages
from userapp.models import Report  # ✅ import from userapp

def admin_view_all_reports(request):
    # Get all reports (latest first)
    reports = Report.objects.select_related('user').order_by('-id')
    return render(request, 'admin_view_reports.html', {'reports': reports})


from django.shortcuts import render
from userapp.models import Feedback  # adjust import path if Feedback is in userapp

def admin_view_all_feedbacks(request):
    """Admin can view all feedbacks, latest first"""
    feedbacks = Feedback.objects.select_related('user', 'order').order_by('-created_at')
    return render(request, 'admin_view_feedbacks.html', {'feedbacks': feedbacks})


def view_scanner_data(request):
    return render(request, 'scanner.html')