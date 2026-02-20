from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from .models import Tbl_Admin
from userapp.models import *

from .models import Tbl_Admin
from datetime import time
from django.utils.timezone import now
from django.contrib import messages


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import TodaysSpecialSerializer

def admin_login_view(request):
    entered_data = None  # To send data to template

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')


        try:
            admin = Tbl_Admin.objects.get(username=username, password=password)
            request.session['admin_id'] = admin.id
            return render(request, 'adminapp/dashboard.html')

        except Tbl_Admin.DoesNotExist:
            return render(
                request,
                'adminapp/login.html',
                {
                    'error': 'Invalid username or password',
                    'entered_data': entered_data
                }
            )

    return render(request, 'adminapp/login.html')

def admin_dashboard(request):
    return render(request,'adminapp/dashboard.html')




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

    return render(request, 'adminapp/add_category.html', {'error': error})


def category_list_view(request):
    categories = Category.objects.all()
    return render(request, 'adminapp/category_list.html', {'categories': categories})


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
            return render(request, 'adminapp/edit_category.html', {'category': category, 'error': error})

    return render(request, 'adminapp/edit_category.html', {'category': category})


# Delete Category
def delete_category_view(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        category.delete()
        return redirect('category_list')

    # Confirmation page for GET request
    return render(request, 'adminapp/delete_category.html', {'category': category})


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
        is_todays_special = request.POST.getlist('is_todays_special')
        special_dates = request.POST.getlist('special_date')

        for i in range(len(names)):
            MenuItem.objects.create(
                name=names[i],
                rate=rates[i],
                item_per_plate=items_per_plate[i],
                category_id=categories_selected[i],
                image=images[i] if i < len(images) else None,
                is_todays_special=bool(is_todays_special[i]) if i < len(is_todays_special) else False,
                special_date=special_dates[i] if i < len(special_dates) and special_dates[i] else None
            )

        return redirect('menu_list')

    return render(request, 'adminapp/add_menu.html', {'categories': categories})



# views.py
from datetime import datetime
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import TblMenuItem, TblDailyMenu

def add_daily_menu(request):
    items = MenuItem.objects.all()  # get all menu items

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

        daily_menu, created = DailyMenu.objects.get_or_create(date=date_obj)
        daily_menu.items.set(selected_items)  # assign correct items
        messages.success(request, f"Daily menu for {weekday} ({date_obj}) saved successfully!")
        return redirect('daily_menu_list')

    from datetime import date
    
    return render(request, 'adminapp/add_daily_menu.html', {
        'items': items,
        'today': date.today()
    })


from django.shortcuts import get_object_or_404

def edit_daily_menu(request, id):
    daily_menu = get_object_or_404(DailyMenu, id=id)
    items = MenuItem.objects.all()

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

    return render(request, 'adminapp/edit_daily_menu.html', {
        'menu': daily_menu,
        'items': items,
    })


def delete_daily_menu(request, id):
    daily_menu = get_object_or_404(DailyMenu, id=id)
    if request.method == 'POST':
        daily_menu.delete()
        messages.success(request, "Daily menu deleted successfully.")
        return redirect('daily_menu_list')
    
def daily_menu_list(request):
    menus = DailyMenu.objects.all().order_by('-date')
    return render(request, 'adminapp/daily_menu_list.html', {'menus': menus})



def menu_list(request):
    items = MenuItem.objects.all().order_by('-is_todays_special', 'category__name', 'name')
    return render(request, 'adminapp/menu_list.html', {'items': items})


def delete_menu_item(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)
    item.delete()
    return redirect('menu_list')


from django.shortcuts import render, get_object_or_404, redirect
from .models import MenuItem, Category

def edit_menu_item(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)
    categories = Category.objects.all()

    if request.method == 'POST':
        item.name = request.POST.get('name')
        item.rate = request.POST.get('rate')
        item.item_per_plate = request.POST.get('item_per_plate')
        item.category_id = request.POST.get('category')
        item.is_todays_special = request.POST.get('is_todays_special') == 'on'
        
        special_date = request.POST.get('special_date')
        item.special_date = special_date if special_date else None

        if request.FILES.get('image'):
            item.image = request.FILES['image']

        item.save()
        return redirect('menu_list')

    return render(request, 'adminapp/edit_menu.html', {
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
        default=5,
        output_field=IntegerField(),
    )

    slots = TimeSlot.objects.all().order_by(order_priority, 'start_time')
    return render(request, 'adminapp/time_slot_list.html', {'slots': slots})


# -------------------------------
# Add time slots (manual or auto 30-min slots)
# -------------------------------

def add_time_slot(request):
    categories = Category.objects.exclude(name="Dinner")  # Remove Dinner category

    if request.method == 'POST':
        category_id = request.POST.get('category')
        start_time_str = request.POST.get('start_time')
        end_time_str = request.POST.get('end_time')

        category = Category.objects.get(id=category_id)

        # Convert to datetime objects
        start_time = datetime.strptime(start_time_str, "%H:%M")
        end_time = datetime.strptime(end_time_str, "%H:%M")

        # Remove existing slots for selected category (optional)
        TimeSlot.objects.filter(category=category).delete()

        current_time = start_time
        while current_time < end_time:
            slot_start = current_time.time()
            slot_end = (current_time + timedelta(minutes=30)).time()

            if slot_end > end_time.time():
                slot_end = end_time.time()

            TimeSlot.objects.create(
                category=category,
                start_time=slot_start,
                end_time=slot_end,
            )
            current_time += timedelta(minutes=30)

        messages.success(request, "Time slots added successfully!")
        return redirect('time_slot_list')

    return render(request, 'adminapp/add_time_slot.html', {'categories': categories})


# -------------------------------
# Edit a time slot
# -------------------------------
def edit_time_slot(request, slot_id):
    slot = get_object_or_404(TimeSlot, id=slot_id)
    categories = Category.objects.all()

    if request.method == 'POST':
        category_id = request.POST.get('category')
        slot.category = Category.objects.get(id=category_id)
        slot.start_time = request.POST.get('start_time')
        slot.end_time = request.POST.get('end_time')
        slot.save()

        messages.success(request, "Time slot updated successfully!")
        return redirect('time_slot_list')

    return render(request, 'adminapp/edit_time_slot.html', {'slot': slot, 'categories': categories})


def delete_time_slot(request, slot_id):
    slot = get_object_or_404(TimeSlot, id=slot_id)
    slot.delete()

    messages.success(request, "Time slot deleted successfully!")
    return redirect('time_slot_list')


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Table

# Show all tables
def table_list(request):
    tables = Table.objects.all()
    return render(request, 'adminapp/table_list.html', {'tables': tables})

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

    return render(request, 'adminapp/add_table.html')

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

    return render(request, 'adminapp/edit_table.html', {'table': table})

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
    return render(request, 'adminapp/seat_list.html', {'table': table, 'seats': seats})




from django.shortcuts import render
from userapp.models import Order

def admin_all_orders(request):
    # Show the latest orders first — newest date (and id) at the top
    orders = Order.objects.all().order_by('-date', '-id')
    return render(request, 'adminapp/admin_all_orders.html', {'orders': orders})

def admin_cancelled_orders(request):
    # Show only cancelled orders, latest first
    orders = Order.objects.filter(booking_status='cancelled').order_by('-date', '-id')
    return render(request, 'adminapp/admin_cancelled_orders.html', {'orders': orders})

from django.shortcuts import render, get_object_or_404
from userapp.models import Table

from django.shortcuts import render, get_object_or_404
from userapp.models import Order, Table

def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    mapped_tables = []
    if isinstance(order.tables, list):
        for t in order.tables:
            try:
                table_obj = Table.objects.get(id=t["table_id"])
                mapped_tables.append({
                    "table_name": table_obj.table_name,
                    "seats": t["seat_ids"]
                })
            except:
                pass

    return render(request, "adminapp/admin_order_detail.html", {
        "order": order,
        "mapped_tables": mapped_tables
    })



from django.shortcuts import render, get_object_or_404, redirect
from userapp.models import Order, OrderItem
from .models import MenuItem, DailyMenu  # ✅ import these

def admin_select_food(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        selected_items = request.POST.getlist('food_items')
        quantities = request.POST.getlist('quantities')

        for i, item_id in enumerate(selected_items):
            food_item = MenuItem.objects.get(id=item_id)
            quantity = int(quantities[i])
            total_price = food_item.rate * quantity

            OrderItem.objects.create(
                order=order,
                food_item=food_item,
                quantity=quantity,
                price=food_item.rate,
                total_price=total_price
            )

        # update total
        order.total_amount = sum(item.total_price for item in order.items.all())
        order.save()
        return redirect('admin_order_detail', order_id=order.id)

    # show menu based on date
    daily_menu = DailyMenu.objects.filter(date=order.date).first()
    food_items = daily_menu.items.all() if daily_menu else []










from django.shortcuts import render, redirect
from django.contrib import messages
# from userapp.models import UserReport  # ✅ import from userapp
from django.shortcuts import render
# from userapp.models import UserReport

from django.shortcuts import render
# from userapp.models import UserReport
from django.shortcuts import render
# from userapp.models import UserReport
from userapp.models import *
# from django.db import connection

# def admin_view_all_reports(request):
#     print("DB in use (view):", connection.settings_dict['NAME'])
#     reports = (
#         UserReport.objects
#         .select_related('user')
#         .prefetch_related('images')
#         .order_by('-id')
#     )
#     print("Reports count in view:", reports.count())
#     print("Reports queryset in view:", list(reports))
#     return render(request, 'adminapp/admin_view_reports.html', {'reports': reports})

# adminapp/views.py

from django.shortcuts import render
# from django.contrib.auth.decorators import login_required
# from userapp.models import UserReport

from django.shortcuts import render
# from userapp.models import UserReport

def reports_list(request):
    reports = Reporttbl.objects.all().order_by("-created_at")  # latest first
    return render(request, "adminapp/admin_view_reports.html", {"reports": reports})

from django.shortcuts import render
from userapp.models import Feedback  # adjust import path if Feedback is in userapp

def admin_view_all_feedbacks(request):
    """Admin can view all feedbacks, latest first"""
    feedbacks = Feedback.objects.select_related('user', 'order').order_by('-created_at')
    return render(request, 'adminapp/admin_view_feedbacks.html', {'feedbacks': feedbacks})


def view_scanner_data(request):
    return render(request, 'adminapp/scanner.html')

def scan_qr_complete_order(request):
    """
    Scan QR code to mark order as completed and update payment status
    """
    order = None
    order_details = None
    
    if request.method == 'POST':
        # Check if QR data is provided
        qr_data = request.POST.get('qr_data')
        
        if qr_data:
            try:
                # Parse QR data (expected format: {"order_id": 23})
                import json
                qr_json = json.loads(qr_data)
                order_id = qr_json.get('order_id')
                
                # Alternative format check
                if not order_id:
                    # Try to extract order ID from text if not in JSON format
                    import re
                    match = re.search(r'order[_\s]*id\s*[:=]\s*(\d+)', qr_data, re.IGNORECASE)
                    if match:
                        order_id = match.group(1)
                    else:
                        # Try plain number
                        match = re.search(r'\b(\d{1,5})\b', qr_data)
                        if match and len(match.group(1)) <= 5:  # Reasonable order ID length
                            order_id = match.group(1)
                
                if order_id:
                    order = Order.objects.get(id=int(order_id))
                    
                    # a. Update is_completed: false -> True
                    order.is_completed = True
                    
                    # b. Update payment status for cash payments
                    if order.table_payment_mode == 'cash':
                        order.table_payment_status = 'paid'
                    
                    if order.food_payment_mode == 'cash':
                        order.food_payment_status = 'paid'
                    
                    order.save()
                    
                    # Update booking status to 'completed'
                    order.booking_status = 'completed'
                    order.save(update_fields=['booking_status'])

                    messages.success(request, f"Order #{order_id} marked as completed. Payment status updated.")
                    
                    # Fetch order details for display
                    order_details = {
                        'id': order.id,
                        'booking_type': order.get_booking_type_display(),
                        'user': order.user.username if order.user else order.outsider_name,
                        'date': order.date,
                        'total_amount': order.total_amount,
                        'table_payment_mode': order.table_payment_mode,
                        'food_payment_mode': order.food_payment_mode,
                        'table_payment_status': order.table_payment_status,
                        'food_payment_status': order.food_payment_status,
                        'is_completed': order.is_completed,
                    }
                    
            except json.JSONDecodeError:
                messages.error(request, "Invalid QR code format. Expected JSON: {'order_id': 123}")
            except Order.DoesNotExist:
                messages.error(request, f"Order #{order_id} not found")
            except Exception as e:
                messages.error(request, f"Error processing QR: {str(e)}")
        else:
            # Manual order ID input
            order_id = request.POST.get('order_id')
            
            if not order_id:
                messages.error(request, "Please scan a QR code or enter an Order ID")
                return render(request, 'adminapp/scanner.html')
            
            try:
                order = Order.objects.get(id=order_id)
                
                # a. Update is_completed: false -> True
                order.is_completed = True
                
                # b. Update payment status for cash payments
                if order.table_payment_mode == 'cash':
                    order.table_payment_status = 'paid'
                
                if order.food_payment_mode == 'cash':
                    order.food_payment_status = 'paid'
                
                order.save()
                
                # Update booking status to 'completed'
                order.booking_status = 'completed'
                order.save(update_fields=['booking_status'])
                
                messages.success(request, f"Order #{order_id} marked as completed. Payment status updated.")
                
                # Fetch order details for display
                order_details = {
                    'id': order.id,
                    'booking_type': order.get_booking_type_display(),
                    'user': order.user.username if order.user else order.outsider_name,
                    'date': order.date,
                    'total_amount': order.total_amount,
                    'table_payment_mode': order.table_payment_mode,
                    'food_payment_mode': order.food_payment_mode,
                    'table_payment_status': order.table_payment_status,
                    'food_payment_status': order.food_payment_status,
                    'is_completed': order.is_completed,
                    'booking_status': order.get_booking_status_display(),  
                }
                
            except Order.DoesNotExist:
                messages.error(request, f"Order #{order_id} not found")
    
    return render(request, 'adminapp/scanner.html', {
        'order': order,
        'order_details': order_details
    })

from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib import messages
from decimal import Decimal
from .models import *
from adminapp.models import MenuItem
from userapp.models import Table, Seat
from adminapp.models import TblMenuItem, TblDailyMenu
from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib import messages
from decimal import Decimal
from userapp.models import Table, Seat


from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib import messages
from decimal import Decimal

from userapp.models import Table, Seat
from adminapp.models import TblTimeSlot, TblDailyMenu, TblMenuItem
# from .models import Order, OrderSeat, OrderItem


def admin_book_outsider(request):
    today = timezone.localdate()
    now = timezone.localtime().time()
    
    # Initialize ALL variables at the beginning
    tables = Table.objects.all()
    available_seat_ids = []
    food_items = []
    # Get today's special items from MenuItem model
    todays_specials = MenuItem.objects.filter(
        is_todays_special=True, 
        special_date=today
    )
    selected_slot = None
    selected_category = None
    today_date = today
    
    # GET ACTIVE TIMESLOT (if any) - using unified TimeSlot model
    selected_slot = TimeSlot.objects.filter(
        start_time__lte=now,
        end_time__gte=now
    ).first()
    
    selected_category = selected_slot.category if selected_slot else None
    
    # Determine category based on time if no active slot
    if not selected_category:
        current_hour = now.hour
        if 7 <= current_hour < 11:
            time_based_category = "Breakfast"
        elif 11 <= current_hour < 15:
            time_based_category = "Lunch"
        elif 15 <= current_hour < 18:
            time_based_category = "Evening Snacks"
        elif 18 <= current_hour < 22:
            time_based_category = "Dinner"
        else:
            # Outside regular hours - check if any slots exist for today
            # Find the nearest future slot for today
            future_slots = TimeSlot.objects.filter(
                start_time__gte=now
            ).order_by('start_time').first()
            
            if future_slots:
                selected_category = future_slots.category
                selected_slot = future_slots
                time_based_category = selected_category.name
            else:
                # No future slots today, use default category logic
                time_based_category = "Dinner"  # Default
            
        try:
            selected_category = Category.objects.get(name=time_based_category)
        except Category.DoesNotExist:
            selected_category = Category.objects.first()  # Fallback

    # LOAD TODAY'S FOOD ITEMS
    # For outsider booking, show items based on selected_category
    if selected_category:
        try:
            today_menu = DailyMenu.objects.get(date=today)
            food_items = today_menu.items.filter(category=selected_category)
        except DailyMenu.DoesNotExist:
            food_items = MenuItem.objects.filter(category=selected_category)
    else:
        # Fallback: show first 10 menu items
        food_items = MenuItem.objects.all()[:10]
    
    # FIND BOOKED SEATS (for outsider booking - independent of selected_slot)
    # Get seats booked in time slots that are currently active or overlapping
    from datetime import datetime, time
    
    # Find all time slots that overlap with current time
    overlapping_slots = TimeSlot.objects.filter(
        start_time__lte=now,
        end_time__gte=now
    )
    
    if overlapping_slots.exists():
        # Get seats booked in overlapping time slots
        booked_seat_ids = OrderSeat.objects.filter(
            order__date=today,
            order__time_slot__in=overlapping_slots
        ).values_list("seat_id", flat=True)
    else:
        # If no overlapping slots, check all seats booked for today
        # This handles gaps between time slots
        booked_seat_ids = OrderSeat.objects.filter(
            order__date=today
        ).values_list("seat_id", flat=True)
    
    # For outsider booking, also exclude seats that are marked as occupied
    occupied_seat_ids = Seat.objects.filter(is_occupied=True).values_list('id', flat=True)
    all_unavailable_seats = list(booked_seat_ids) + list(occupied_seat_ids)
    available_seats = Seat.objects.exclude(id__in=all_unavailable_seats)
    available_seat_ids = list(available_seats.values_list("id", flat=True))

    # HANDLE FORM SUBMISSION
    if request.method == "POST" and request.POST.get("final_submit") == "1":

        name = request.POST.get("name", "").strip()
        phone = request.POST.get("phone", "").strip()
        persons_str = request.POST.get("number_of_persons", "0")
        try:
            persons = int(persons_str) if persons_str else 0
        except ValueError:
            persons = 0
        seat_ids = request.POST.getlist("seat_ids")

        if not name or not phone:
            messages.error(request, "Name and phone are required.")
            return redirect("admin_book_outsider")

        if persons <= 0:
            messages.error(request, "Invalid number of persons.")
            return redirect("admin_book_outsider")

        if len(seat_ids) < persons:
            messages.error(request, "Select enough seats.")
            return redirect("admin_book_outsider")

        if not selected_slot:
            messages.error(request, "No active timeslot.")
            return redirect("admin_book_outsider")
        
        # Count today's special items selected
        special_items_count = 0
        for special in todays_specials:
            qty_str = request.POST.get(f"special_{special.id}", "0")
            try:
                qty = int(qty_str) if qty_str else 0
            except ValueError:
                qty = 0
            if qty > 0:
                special_items_count += qty
        
        # If booking today's special, ensure at least one seat per special item
        if special_items_count > 0:
            # Check if total special items exceed available seats
            if special_items_count > len(seat_ids):
                messages.error(request, 
                    f"Cannot book {special_items_count} today's special items with only {len(seat_ids)} seats. "
                    f"Each special item requires at least one seat.")
                return redirect("admin_book_outsider")
        
        # CREATE ORDER
        order = Order.objects.create(
            outsider_name=name,
            outsider_phone=phone,
            booking_type="ONSPOT",
            category=selected_category,
            date=today,
            time_slot=selected_slot,
            number_of_persons=persons,
        )

        total_table_charge = Decimal("0.00")

        # =============== SAVE TABLE + SEAT MAPPING ===============
        table_map = {}  # {table_id: [seat_ids]}

        for seat_id in seat_ids:
            seat = Seat.objects.get(id=seat_id)
            table_id = seat.table.id

            # Add seat under correct table
            if table_id not in table_map:
                table_map[table_id] = []
            table_map[table_id].append(seat.id)

            # Save seat assignment
            OrderSeat.objects.create(order=order, seat=seat)
            total_table_charge += seat.seat_price

        # Store clean table list JSON
        order.tables = [
            {"table_id": tid, "seat_ids": sids}
            for tid, sids in table_map.items()
        ]

        order.table_charge = total_table_charge
        order.save()

        # ADD FOOD ITEMS
        for item in food_items:
            qty_str = request.POST.get(f"food_{item.id}", "0")
            try:
                qty = int(qty_str) if qty_str else 0
            except ValueError:
                qty = 0
            if qty > 0:
                OrderItem.objects.create(
                    order=order,
                    food_item=item,
                    quantity=qty,
                    price=item.rate,
                    total_price=item.rate * qty
                )

        # ADD TODAY'S SPECIAL ITEMS
        special_items_booked = 0
        for special in todays_specials:
            qty_str = request.POST.get(f"special_{special.id}", "0")
            try:
                qty = int(qty_str) if qty_str else 0
            except ValueError:
                qty = 0
            if qty > 0:
                # Find or create equivalent TblMenuItem for the special
                try:
                    menu_item = TblMenuItem.objects.get(
                        name=special.name,
                        category=special.category,
                        rate=special.rate
                    )
                except TblMenuItem.DoesNotExist:
                    # Create a temporary menu item if it doesn't exist
                    menu_item = TblMenuItem.objects.create(
                        name=special.name,
                        category=special.category,
                        rate=special.rate,
                        item_per_plate=special.item_per_plate,
                        image=special.image
                    )
                
                OrderItem.objects.create(
                    order=order,
                    food_item=menu_item,  # Use TblMenuItem, not TodaysSpecial
                    quantity=qty,
                    price=special.rate,
                    total_price=special.rate * qty
                )
                special_items_booked += qty
        
        if special_items_booked > 0:
            messages.success(request, f"{special_items_booked} today's special item(s) booked successfully!")

        order.table_payment_mode = 'cash'
        order.food_payment_mode = 'cash'
        order.table_payment_status = 'paid'  # Since it's on-spot booking
        order.food_payment_status = 'paid'   # Since it's on-spot booking
        order.save()
        order.update_total()

        messages.success(request, f"Booking successful! Order #{order.id}")
        return redirect("admin_all_orders")

    context = {
        "selected_slot": selected_slot,
        "selected_category": selected_category,
        "tables": tables,
        "available_seat_ids": available_seat_ids,
        "food_items": food_items,
        "todays_specials": todays_specials,
        "today": today_date,
        "now": now,  # Add current time to template context
    }

    return render(request, "adminapp/admin_outsider_booking.html", context)

def admin_pending_users(request):
    """View all users with pending registration status"""
    pending_users = TblUser.objects.filter(registration_status='pending').order_by('registered_at')
    
    # Count all statuses for dashboard info
    pending_count = pending_users.count()
    approved_count = TblUser.objects.filter(registration_status='approved').count()
    rejected_count = TblUser.objects.filter(registration_status='rejected').count()
    total_users = TblUser.objects.count()
    
    return render(request, 'adminapp/admin_pending_users.html', {
        'users': pending_users,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'total_users': total_users
    })

def admin_approve_user(request, user_id):
    """Approve a pending user registration"""
    user = get_object_or_404(TblUser, id=user_id)
    if user.registration_status == 'pending':
        user.registration_status = 'approved'
        user.save()
        messages.success(request, f"User '{user.username}' approved successfully!")
    else:
        messages.warning(request, f"User '{user.username}' is not pending approval.")
    return redirect('admin_pending_users')

def admin_reject_user(request, user_id):
    """Reject a pending user registration"""
    user = get_object_or_404(TblUser, id=user_id)
    if user.registration_status == 'pending':
        user.registration_status = 'rejected'
        user.save()
        messages.success(request, f"User '{user.username}' registration rejected.")
    else:
        messages.warning(request, f"User '{user.username}' is not pending approval.")
    return redirect('admin_pending_users')


# def admin_add_user(request):
#     if request.method == "POST":
#         username = request.POST.get("username")
#         password = request.POST.get("password")
#         user_type = request.POST.get("user_type")
#         batch_name = request.POST.get("batch_name")
#         department = request.POST.get("department")
#         profile_photo = request.FILES.get("profile_photo")

#         if user_type == "student":
#             if not batch_name or not department:
#                 messages.error(request, "Students must have batch name and department.")
#                 return redirect("admin_add_user")

#         TblUser.objects.create(
#             username=username,
#             password=password,
#             user_type=user_type,
#             batch_name=batch_name if user_type == "student" else None,
#             department=department,
#             profile_photo=profile_photo
#         )

#         messages.success(request, "User added successfully!")
#         return redirect("admin_add_user")

#     return render(request, "adminapp/admin_add_user.html")


def admin_view_users(request):
    """View all users with optional status filtering"""
    status_filter = request.GET.get('status', 'all')
    
    users = TblUser.objects.all().order_by('-id')
    
    if status_filter != 'all':
        users = users.filter(registration_status=status_filter)
    
    return render(request, 'adminapp/admin_view_users.html', {
        'users': users,
        'current_status': status_filter
    })

def admin_edit_user(request, user_id):
    user = get_object_or_404(TblUser, id=user_id)

    if request.method == "POST":
        user.username = request.POST.get("username")
        user.password = request.POST.get("password")
        user.user_type = request.POST.get("user_type")
        user.department = request.POST.get("department")
        user.batch_name = request.POST.get("batch_name") if user.user_type == "student" else None

        if "profile_photo" in request.FILES:
            user.profile_photo = request.FILES['profile_photo']

        user.save()
        messages.success(request, "User updated successfully!")
        return redirect('admin_view_users')

    return render(request, "adminapp/admin_edit_user.html", {"user": user})


def admin_delete_user(request, user_id):
    user = get_object_or_404(TblUser, id=user_id)
    user.delete()
    messages.success(request, "User deleted successfully!")
    return redirect('admin_view_users')

@api_view(['GET'])
def todays_special_list(request):
    """
    GET: List today's special items for a specific date
    Query param: ?date=2026-01-28 (defaults to today)
    """
    date_str = request.query_params.get('date')
    
    if date_str:
        try:
            from datetime import datetime
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST
            )
    else:
        from datetime import date
        date_obj = date.today()
    
    specials = TodaysSpecial.objects.filter(date=date_obj)
    serializer = TodaysSpecialSerializer(specials, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def create_todays_special(request):
    """
    POST: Create a new today's special item
    """
    serializer = TodaysSpecialSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def todays_special_page(request):
    """Display list of today's special items"""
    from datetime import date
    
    # Handle delete request
    if request.method == 'POST' and 'delete_id' in request.POST:
        try:
            special_id = request.POST.get('delete_id')
            special = TodaysSpecial.objects.get(id=special_id)
            special_name = special.name
            special.delete()
            messages.success(request, f"Today's special '{special_name}' deleted successfully!")
            return redirect('todays_special_page')
        except TodaysSpecial.DoesNotExist:
            messages.error(request, "Today's special item not found.")
        except Exception as e:
            messages.error(request, f"Error deleting item: {str(e)}")
    
    # Get date from query parameter or default to today
    date_str = request.GET.get('date')
    if date_str:
        try:
            from datetime import datetime
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Invalid date format. Using today's date.")
            selected_date = date.today()
    else:
        selected_date = date.today()
    
    # Order by category and name for better organization
    specials = TodaysSpecial.objects.filter(date=selected_date).order_by('category__name', 'name')
    
    return render(request, 'adminapp/todays_special_list.html', {
        'specials': specials,
        'today': selected_date
    })

def add_todays_special_page(request):
    """Display form to add today's special"""
    categories = Category.objects.all()
    
    if request.method == 'POST':
        # Handle form submission (both buttons)
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        rate = request.POST.get('rate')
        item_per_plate = request.POST.get('item_per_plate')
        date_str = request.POST.get('date')
        image = request.FILES.get('image')
        
        if not all([name, category_id, rate, item_per_plate, date_str]):
            messages.error(request, "All fields except image are required.")
            return redirect('add_todays_special_page')
        
        try:
            from datetime import datetime
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Create in old table for backward compatibility
            TodaysSpecial.objects.create(
                name=name,
                category_id=category_id,
                rate=rate,
                item_per_plate=item_per_plate,
                date=date_obj,
                image=image
            )
            
            # Create/update in new MenuItem table
            menu_item, created = MenuItem.objects.update_or_create(
                name=name,
                category_id=category_id,
                defaults={
                    'rate': rate,
                    'item_per_plate': item_per_plate,
                    'image': image,
                    'is_todays_special': True,
                    'special_date': date_obj
                }
            )
            
            if created:
                print(f"✅ Created new MenuItem: {name} (ID: {menu_item.id})")
            else:
                print(f"✅ Updated existing MenuItem: {name} (ID: {menu_item.id})")
            
            messages.success(request, f"Today's special '{name}' added successfully!")
            
            # Check which button was clicked
            if 'add_another' in request.POST:
                # Stay on the form to add another
                return redirect('add_todays_special_page')
            else:
                # Redirect to list page
                return redirect('todays_special_page')
                
        except ValueError:
            messages.error(request, "Invalid date format. Use YYYY-MM-DD.")
    
    return render(request, 'adminapp/add_todays_special.html', {
        'categories': categories
    })

def edit_todays_special(request, special_id):
    """Edit a today's special item"""
    special = get_object_or_404(TodaysSpecial, id=special_id)
    categories = Category.objects.all()
    
    if request.method == 'POST':
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        rate = request.POST.get('rate')
        item_per_plate = request.POST.get('item_per_plate')
        date_str = request.POST.get('date')
        
        if not all([name, category_id, rate, item_per_plate, date_str]):
            messages.error(request, "All fields are required.")
            return redirect('edit_todays_special', special_id=special_id)
        
        try:
            from datetime import datetime
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Update fields
            special.name = name
            special.category_id = category_id
            special.rate = rate
            special.item_per_plate = item_per_plate
            special.date = date_obj
            
            # Handle image update
            if request.FILES.get('image'):
                special.image = request.FILES['image']
            
            special.save()
            
            messages.success(request, f"Today's special '{name}' updated successfully!")
            return redirect('todays_special_page')
            
        except ValueError:
            messages.error(request, "Invalid date format. Use YYYY-MM-DD.")
    
    return render(request, 'adminapp/edit_todays_special.html', {
        'special': special,
        'categories': categories
    })

def admin_add_food_to_order(request, order_id):
    """
    Add food items to a TABLE_ONLY order (for QR scanned orders)
    """
    from datetime import date
    
    order = get_object_or_404(Order, id=order_id)
    today = date.today()
    
    # Verify this is a TABLE_ONLY order
    if order.booking_type != 'TABLE_ONLY':
        messages.error(request, "Food can only be added to TABLE_ONLY orders")
        return redirect('scan_qr')
    
    # Get current time to determine category
    now = timezone.localtime().time()
    
    # Find active time slot
    selected_slot = TimeSlot.objects.filter(
        start_time__lte=now,
        end_time__gte=now
    ).first()
    
    selected_category = selected_slot.category if selected_slot else None
    
    # Load today's food items based on category
    food_items = []
    if selected_category:
        try:
            today_menu = DailyMenu.objects.get(date=today)
            food_items = today_menu.items.filter(category=selected_category)
        except DailyMenu.DoesNotExist:
            food_items = MenuItem.objects.filter(category=selected_category)
    else:
        # If no active time slot, show all food items for today
        try:
            today_menu = DailyMenu.objects.get(date=today)
            food_items = today_menu.items.all()
        except DailyMenu.DoesNotExist:
            # If no daily menu, show all menu items
            food_items = MenuItem.objects.all()
    
    # Load today's special items
    todays_specials = MenuItem.objects.filter(
        is_todays_special=True, 
        special_date=today
    )
    
    if request.method == 'POST':
        # Add food items to the order
        items_added = 0
        
                # Add regular food items
        for item in food_items:
            qty = int(request.POST.get(f"food_{item.id}", 0))
            if qty > 0:
                OrderItem.objects.create(
                    order=order,
                    food_item=item,
                    quantity=qty,
                    price=item.rate,
                    total_price=item.rate * qty
                )
                items_added += qty
        
        # Add today's special items
        for special in todays_specials:
            qty = int(request.POST.get(f"special_{special.id}", 0))
            if qty > 0:
                # Find corresponding TblMenuItem for today's special
                try:
                    # Try to find menu item with same name and category
                    menu_item = TblMenuItem.objects.get(
                        name=special.name,
                        category=special.category
                    )
                    
                    OrderItem.objects.create(
                        order=order,
                        food_item=menu_item,  # ✅ Use TblMenuItem instance
                        quantity=qty,
                        price=special.rate,
                        total_price=special.rate * qty
                    )
                    items_added += qty
                except TblMenuItem.DoesNotExist:
                    # If menu item doesn't exist, create a temporary one
                    messages.warning(request, 
                        f"Menu item '{special.name}' not found. Using today's special rate.")
                    
                    # Create a temporary TblMenuItem
                    menu_item = TblMenuItem.objects.create(
                        name=special.name,
                        category=special.category,
                        rate=special.rate,
                        item_per_plate=special.item_per_plate,
                        image=special.image if special.image else None
                    )
                    
                    OrderItem.objects.create(
                        order=order,
                        food_item=menu_item,
                        quantity=qty,
                        price=special.rate,
                        total_price=special.rate * qty
                    )
                    items_added += qty

        if items_added > 0:
            order.update_total()
            messages.success(request, f"{items_added} food item(s) added to order #{order_id}")
            return redirect('admin_order_detail', order_id=order_id)
        else:
            messages.warning(request, "No food items selected")
    
    context = {
        'order': order,
        'selected_slot': selected_slot,
        'selected_category': selected_category,
        'food_items': food_items,
        'todays_specials': todays_specials,
        'today': today,
        'now': now,
    }
    
    return render(request, 'adminapp/admin_add_food_to_order.html', context)

# Custom 404 error handler
def custom_404_view(request, exception):
    print("="*50)
    print("CUSTOM 404 VIEW CALLED")
    print(f"Request path: {request.path}")
    print(f"Exception: {exception}")
    print("="*50)
    return render(request, '404.html', status=404)