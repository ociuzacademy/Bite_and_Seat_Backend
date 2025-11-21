from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from .models import Tbl_Admin
from userapp.models import *

from django.shortcuts import render, redirect
from .models import Tbl_Admin
from datetime import time
from django.utils.timezone import now
from django.contrib import messages
from django.shortcuts import render, redirect


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

        for i in range(len(names)):
            TblMenuItem.objects.create(
                name=names[i],
                rate=rates[i],
                item_per_plate=items_per_plate[i],
                category_id=categories_selected[i],
                image=images[i] if i < len(images) else None
            )

        return redirect('menu_list')

    return render(request, 'adminapp/add_menu.html', {'categories': categories})



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

    return render(request, 'adminapp/add_daily_menu.html', {'items': items})


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

    return render(request, 'adminapp/edit_daily_menu.html', {
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
    return render(request, 'adminapp/daily_menu_list.html', {'menus': menus})



def menu_list(request):
    items = TblMenuItem.objects.all()
    return render(request, 'adminapp/menu_list.html', {'items': items})


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
        When(category__name='Dinner', then=4),
        default=5,
        output_field=IntegerField(),
    )

    slots = TblTimeSlot.objects.all().order_by(order_priority, 'start_time')
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
        TblTimeSlot.objects.filter(category=category).delete()

        current_time = start_time
        while current_time < end_time:
            slot_start = current_time.time()
            slot_end = (current_time + timedelta(minutes=30)).time()

            if slot_end > end_time.time():
                slot_end = end_time.time()

            TblTimeSlot.objects.create(
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

    return render(request, 'adminapp/edit_time_slot.html', {'slot': slot, 'categories': categories})


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
from adminapp.models import TblMenuItem, TblDailyMenu  # ✅ import these

def admin_select_food(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        selected_items = request.POST.getlist('food_items')
        quantities = request.POST.getlist('quantities')

        for i, item_id in enumerate(selected_items):
            food_item = TblMenuItem.objects.get(id=item_id)
            quantity = int(quantities[i])
            total_price = food_item.rate * quantity

            OrderItem.objects.create(
                order=order,
                food_item=food_item,  # use string field if OrderItem doesn’t FK TblMenuItem
                quantity=quantity,
                price=food_item.rate,
                total_price=total_price
            )

        # update total
        order.total_amount = sum(item.total_price for item in order.items.all())
        order.save()
        return redirect('admin_order_detail', order_id=order.id)

    # show menu based on date
    daily_menu = TblDailyMenu.objects.filter(date=order.date).first()
    food_items = daily_menu.items.all() if daily_menu else []

    return render(request, 'adminapp/admin_select_food.html', {
        'order': order,
        'food_items': food_items
    })











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

from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib import messages
from decimal import Decimal
from .models import *
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

    # GET ACTIVE TIMESLOT
    selected_slot = TblTimeSlot.objects.filter(
        start_time__lte=now,
        end_time__gte=now
    ).first()

    selected_category = selected_slot.category if selected_slot else None

    tables = Table.objects.all()
    available_seat_ids = []
    food_items = []

    # FIND BOOKED SEATS (Don't use is_occupied)
    if selected_slot:
        booked_seat_ids = OrderSeat.objects.filter(
            order__date=today,
            order__time_slot=selected_slot
        ).values_list("seat_id", flat=True)

        available_seats = Seat.objects.exclude(id__in=booked_seat_ids)
        available_seat_ids = list(available_seats.values_list("id", flat=True))

    # LOAD TODAY'S FOOD ITEMS
    if selected_category:
        try:
            today_menu = TblDailyMenu.objects.get(date=today)
            food_items = today_menu.items.filter(category=selected_category)
        except TblDailyMenu.DoesNotExist:
            food_items = TblMenuItem.objects.filter(category=selected_category)

    # HANDLE FORM SUBMISSION
    if request.method == "POST" and request.POST.get("final_submit") == "1":

        name = request.POST.get("name", "").strip()
        phone = request.POST.get("phone", "").strip()
        persons = int(request.POST.get("number_of_persons", 0))
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

        # CREATE ORDER
        order = Order.objects.create(
            outsider_name=name,
            outsider_phone=phone,
            booking_type="ONSPOT",
            category=selected_category,
            date=today,
            time_slot=selected_slot,
            number_of_persons=persons,
            payment_mode="POS"
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
            qty = int(request.POST.get(f"food_{item.id}", 0))
            if qty > 0:
                OrderItem.objects.create(
                    order=order,
                    food_item=item,
                    quantity=qty,
                    price=item.rate,
                    total_price=item.rate * qty
                )

        order.update_total()

        messages.success(request, f"Booking successful! Order #{order.id}")
        return redirect("admin_all_orders")

    context = {
        "selected_slot": selected_slot,
        "selected_category": selected_category,
        "tables": tables,
        "available_seat_ids": available_seat_ids,
        "food_items": food_items,
    }

    return render(request, "adminapp/admin_outsider_booking.html", context)


def admin_add_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user_type = request.POST.get("user_type")
        batch_name = request.POST.get("batch_name")
        department = request.POST.get("department")
        profile_photo = request.FILES.get("profile_photo")

        if user_type == "student":
            if not batch_name or not department:
                messages.error(request, "Students must have batch name and department.")
                return redirect("admin_add_user")

        TblUser.objects.create(
            username=username,
            password=password,
            user_type=user_type,
            batch_name=batch_name if user_type == "student" else None,
            department=department,
            profile_photo=profile_photo
        )

        messages.success(request, "User added successfully!")
        return redirect("admin_add_user")

    return render(request, "adminapp/admin_add_user.html")


def admin_view_users(request):
    users = TblUser.objects.all().order_by('-id')
    return render(request, 'adminapp/admin_view_users.html', {'users': users})


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
