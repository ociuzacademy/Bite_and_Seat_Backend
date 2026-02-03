from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SeatBookingSerializer, UserSerializer
from .models import *
# class RegisterUserAPI(APIView):
#     def post(self, request):
#         serializer = UserSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({
#                 "message": "User registered successfully!",
#                 "data": serializer.data
#             }, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
# from django.contrib.auth.hashers import check_password
# @api_view(['POST'])
# def login_view(request):
#     username = request.data.get('username')
#     password = request.data.get('password')

#     if not username or not password:
#         return Response({
#             "message": "Username and password are required",
#             "status": "failure"
#         }, status=status.HTTP_400_BAD_REQUEST)

#     try:
#         user = User.objects.get(username=username, password=password)

#         # Store user ID in session (optional)
#         request.session['user_id'] = user.id

#         serializer = tbl_registerSerializer(user)
#         return Response({
#             "message": "User login successful",
#             "status": "success",
#             'user_id':user.id,
#             "user": serializer.data
#         }, status=status.HTTP_200_OK)

#     except User.DoesNotExist:
#         return Response({
#             "message": "Invalid username or password",
#             "status": "failure"
#         }, status=status.HTTP_401_UNAUTHORIZED)
    

@api_view(['POST'])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({
            "message": "Username and password are required",
            "status": "failure"
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = TblUser.objects.get(username=username, password=password)
        
        # Check registration status
        if user.registration_status != 'approved':
            return Response({
                "message": f"Registration {user.registration_status}. Please wait for admin approval.",
                "status": "failure"
            }, status=status.HTTP_403_FORBIDDEN)

        # Save user in session
        request.session['user_id'] = user.id

        serializer = UserSerializer(user)
        return Response({
            "message": "User login successful",
            "status": "success",
            "user_id": user.id,
            "user": serializer.data
        }, status=status.HTTP_200_OK)

    except TblUser.DoesNotExist:
        return Response({
            "message": "Invalid username or password",
            "status": "failure"
        }, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def register_user(request):
    """
    User registration endpoint - creates user with 'pending' status
    """

    # Manual validation for student-specific fields
    user_type = request.data.get('user_type')
    if user_type == 'student':
        batch_name = request.data.get('batch_name')
        department = request.data.get('department')
        
        if not batch_name or not department:
            return Response({
                "error": "Students must provide batch_name and department."
            }, status=status.HTTP_400_BAD_REQUEST)
        
    # Validate email is provided
    email = request.data.get('email')
    if not email:
        return Response({
            "error": "Email address is required."
        }, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        # Save user with pending status
        user = serializer.save(registration_status='pending')
        return Response({
            "message": "Registration successful! Please wait for admin approval.",
            "status": "pending",
            "user_id": user.id
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def test_email(request):
    """Test email sending functionality"""
    from django.core.mail import send_mail
    
    recipient_email = request.data.get('email', 'ananyasajan07@gmail.com')
    
    try:
        send_mail(
            subject='Test Email from Bite & Seat',
            message='This is a test email to verify email functionality is working.',
            from_email='noreply@biteandseat.com',
            recipient_list=[recipient_email],
            fail_silently=False,
        )
        return Response({
            "message": f"Test email sent to {recipient_email}",
            "status": "Check console for email output"
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            "error": f"Failed to send email: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from rest_framework import generics, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from adminapp.models import*
from .serializers import CategorySerializer

# ✅ 1. API View for JSON data
class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]  # public access



from rest_framework import generics, permissions
from django.shortcuts import render
from .models import MenuItem
from .serializers import MenuItemSerializer

# ✅ API View (for JSON data)
class MenuItemListAPIView(generics.ListAPIView):
    queryset = MenuItem.objects.select_related('category').all()
    serializer_class = MenuItemSerializer
    permission_classes = [permissions.AllowAny]



class MenuByCategoryAPIView(generics.ListAPIView):
    serializer_class = MenuItemSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return MenuItem.objects.filter(category_id=category_id).select_related('category')
    

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Category, MenuItem, UserSelection
from .serializers import (
    CategorySerializer,
    MenuItemSerializer,
    UserSelectionSerializer,
    CreateUserSelectionSerializer
)

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class MenuItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_queryset(self):
        category_name = self.request.query_params.get('category')
        if category_name:
            return MenuItem.objects.filter(category__name=category_name)
        return super().get_queryset()

# views.py
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import UserSelection, Category, MenuItem, TblUser
from .serializers import UserSelectionSerializer, CreateUserSelectionSerializer

@api_view(['POST'])
def select_food(request):
    """
    User selects a food item and category
    """
    serializer = CreateUserSelectionSerializer(data=request.data)
    if serializer.is_valid():
        selection = serializer.save()
        return Response({
            "message": "Food selection saved successfully!",
            "data": UserSelectionSerializer(selection).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def view_all_selections(request):
    """
    List all selections
    """
    selections = UserSelection.objects.all()
    serializer = UserSelectionSerializer(selections, many=True)
    return Response(serializer.data)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import TblTimeSlot
from .serializers import TimeSlotSerializer

@api_view(['GET'])
def user_time_slots(request):
    category_id = request.query_params.get('category_id')

    if not category_id:
        return Response(
            {"error": "category_id query parameter is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Filter slots by category ID
    slots = TblTimeSlot.objects.filter(category_id=category_id).order_by('start_time')

    if not slots.exists():
        return Response(
            {"message": "No time slots found for this category"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = TimeSlotSerializer(slots, many=True)
    return Response(serializer.data)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Booking
from .serializers import BookingSerializer

# POST: Submit booking data
@api_view(['POST'])
def submit_booking(request):
    serializer = BookingSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "success": True,
            "message": "Booking successful"
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



from datetime import date, datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import TblDailyMenu
from .serializers import DailyMenuSerializer


@api_view(['GET'])
def daily_menus_api(request):
    date_str = request.GET.get('date')

    if date_str:
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST
            )
    else:
        selected_date = date.today()

    # Get the first matching menu for the date
    menu = TblDailyMenu.objects.prefetch_related('items').filter(date=selected_date).first()

    if not menu:
        return Response(
            {"message": f"No menu found for {selected_date}."},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = DailyMenuSerializer(menu, context={'request': request})
    return Response(serializer.data)

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Table, Seat, Booking
from .serializers import SeatSerializer, BookingSerializer

@api_view(['GET'])
def available_seats(request, table_id):
    """List seats of a table with occupancy status"""
    try:
        table = Table.objects.get(id=table_id)
    except Table.DoesNotExist:
        return Response({'error': 'Table not found'}, status=status.HTTP_404_NOT_FOUND)
    
    seats = table.seats.all()
    serializer = SeatSerializer(seats, many=True)
    return Response(serializer.data)
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import TblUser, Table, Seat, SeatBooking
from .serializers import SeatBookingSerializer

@api_view(['POST'])
def book_multiple_seats(request):
   
    user_id = request.data.get('user_id')
    table_id = request.data.get('table_id')
    seat_ids = request.data.get('seat_ids', [])

    # Validate user
    try:
        user = TblUser.objects.get(id=user_id)
    except TblUser.DoesNotExist:
        return Response({'error': 'Invalid user_id'}, status=status.HTTP_400_BAD_REQUEST)

    # Validate table
    try:
        table = Table.objects.get(id=table_id)
    except Table.DoesNotExist:
        return Response({'error': 'Invalid table_id'}, status=status.HTTP_400_BAD_REQUEST)

    if not seat_ids or not isinstance(seat_ids, list):
        return Response({'error': 'seat_ids must be a non-empty list'}, status=status.HTTP_400_BAD_REQUEST)

    total_booking_charge = 0
    booked_seats = []

    for seat_id in seat_ids:
        try:
            seat = Seat.objects.get(id=seat_id, table=table)
        except Seat.DoesNotExist:
            return Response({'error': f'Seat {seat_id} is invalid for this table'}, status=status.HTTP_400_BAD_REQUEST)

        if seat.is_occupied:
            return Response({'error': f'Seat {seat_id} is already occupied'}, status=status.HTTP_400_BAD_REQUEST)

        # Only booking price for the seat
        total_booking_charge += seat.seat_price

        # Create booking and mark seat as occupied
        booking = SeatBooking.objects.create(user=user, table=table, seat=seat, booking_charge=seat.seat_price)
        booked_seats.append(booking)
        seat.is_occupied = True
        seat.save()

    serializer = SeatBookingSerializer(booked_seats, many=True)
    return Response({
        "message": f"{len(booked_seats)} seat(s) booked successfully.",
        "bookings": serializer.data,
        "total_booking_charge": total_booking_charge
    }, status=status.HTTP_201_CREATED)

from decimal import Decimal
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Order
from .serializers import OrderSerializer
from adminapp.models import MenuItem
from adminapp.models import TblTimeSlot
from .models import OrderSeat


@api_view(['POST'])
def create_step1(request):
    from .models import OrderItem
    from adminapp.models import TblMenuItem

    # 👇 Default to today's date if not provided
    request_data = request.data.copy()
    if not request_data.get('date'):
        request_data['date'] = date.today()

    serializer = OrderSerializer(data=request_data)
    if serializer.is_valid():
        order = serializer.save()

        # ✅ If booking type is PREBOOKED or TABLE_ONLY, add food items
        if order.booking_type == 'PREBOOKED' or order.booking_type == 'TABLE_ONLY':
            items = request.data.get('items', [])
            for item_data in items:
                food_id = item_data.get('food_item')
                quantity = int(item_data.get('quantity', 1))
                try:
                    food = TblMenuItem.objects.get(id=food_id)
                    
                    # Check if this is a today's special item
                    from adminapp.models import TodaysSpecial
                    from datetime import date
                    today = date.today()
                    
                    # Only restrict today's special for PREBOOKED, not for TABLE_ONLY
                    if order.booking_type == 'PREBOOKED' and TodaysSpecial.objects.filter(
                        name=food.name, 
                        category=food.category,
                        date=today
                    ).exists():
                        return Response(
                            {
                                "error": f"Today's special item '{food.name}' cannot be booked through pre-booking",
                                "error_code": "TODAYS_SPECIAL_RESTRICTED",
                                "message": "This item is only available through admin outsider booking or TABLE_ONLY booking"
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    
                    OrderItem.objects.create(
                        order=order,
                        food_item=food,
                        quantity=quantity,
                        price=food.rate,
                        total_price=food.rate * quantity
                    )
                except TblMenuItem.DoesNotExist:
                    return Response(
                        {"error": f"Invalid food item ID {food_id}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

        order.update_total()
        return Response(
            {"message": "Step 1 completed", "order": OrderSerializer(order).data},
            status=status.HTTP_201_CREATED
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 💙 Step 2: Update time slot and number of persons
@api_view(['PUT'])
def update_step2(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

    slot_id = request.data.get('slot_id')
    num_persons = request.data.get('number_of_persons')

    if not slot_id:
        return Response({"error": "slot_id is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        slot = TblTimeSlot.objects.get(id=slot_id)
    except TblTimeSlot.DoesNotExist:
        return Response({"error": "Invalid slot_id"}, status=status.HTTP_404_NOT_FOUND)

    # ✅ FIXED: assign FK instance
    order.time_slot = slot
    order.category = slot.category

    if num_persons:
        order.number_of_persons = num_persons

    order.save()

    serializer = OrderSerializer(order)

    slot_data = {
        "slot_id": slot.id,
        "category_id": slot.category.id,
        "category_name": slot.category.name,
        "slot_time": f"{slot.start_time} - {slot.end_time}"
    }

    return Response({
        "message": "Step 2 completed — slot and number of persons selected",
        "order": serializer.data,
        "slot_details": slot_data
    }, status=status.HTTP_200_OK)

# 💚 Step 3: Update table and seats
@api_view(['PUT'])
def update_step3(request, order_id):
    """
    Step 3: Assign multiple tables & seats for the given order.
    Prevents double booking of seats on the same date.
    """
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

    # Ensure order has a date
    if not order.date:
        return Response({"error": "Booking date not set for this order."}, status=status.HTTP_400_BAD_REQUEST)

    tables_data = request.data.get('tables', [])
    if not tables_data:
        return Response({"error": "No tables provided"}, status=status.HTTP_400_BAD_REQUEST)

    # Clear old seats for this order
    OrderSeat.objects.filter(order=order).delete()

    total_charge = Decimal('0.00')
    booked_tables = []

    for table_info in tables_data:
        table_id = table_info.get('table_id')
        seat_ids = table_info.get('seat_ids', [])

        if not table_id or not seat_ids:
            return Response(
                {"error": "Each table must include table_id and seat_ids."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            table = Table.objects.get(id=table_id)
        except Table.DoesNotExist:
            return Response({"error": f"Table {table_id} not found"}, status=status.HTTP_404_NOT_FOUND)

        booked_tables.append({"table_id": table_id, "seat_ids": seat_ids})

        for seat_id in seat_ids:
            try:
                seat = Seat.objects.get(id=seat_id, table=table)

                # ✅ Check if this seat is already booked on SAME date AND SAME time slot
                if OrderSeat.objects.filter(
                    seat=seat,
                    order__date=order.date,
                    order__time_slot=order.time_slot
                ).exists():
                    return Response(
                        {"error": f"Seat {seat.id} in Table {table.id} is already booked on {order.date} at time slot {order.time_slot.id}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                # Book it
                OrderSeat.objects.create(order=order, seat=seat)
                total_charge += Decimal(seat.seat_price or 0)

            except Seat.DoesNotExist:
                return Response(
                    {"error": f"Seat {seat_id} in Table {table_id} not found."},
                    status=status.HTTP_400_BAD_REQUEST
                )

    # Save table and total info
    order.tables = booked_tables
    order.table_charge = total_charge
    order.update_total()
    order.save()

    serializer = OrderSerializer(order)
    return Response({
        "message": "Step 3 completed successfully — seats booked for the selected date.",
        "order": serializer.data
    }, status=status.HTTP_200_OK)
# 🧾 Final Step: Finalize order (COD or payment)
# @api_view(['GET'])
# def finalize_order(request, order_id):
#     try:
#         order = Order.objects.get(id=order_id)
#     except Order.DoesNotExist:
#         return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

#     order.payment_mode = "Cash on Delivery"
#     order.save()

#     order.refresh_from_db()
#     order = (
#         Order.objects
#         .select_related('table', 'category', 'user')
#         .prefetch_related('order_seats__seat', 'items__food_item')
#         .get(id=order_id)
#     )

#     serializer = OrderSerializer(order)
#     return Response({
#         "message": "Order finalized successfully (COD)",
#         "order": serializer.data
#     }, status=status.HTTP_200_OK)



from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import TblUser
from .serializers import UsersSerializer

class UserProfileView(viewsets.ReadOnlyModelViewSet):
    queryset = TblUser.objects.all()
    serializer_class=UsersSerializer
    
    def list(self, request, *args,**kwargs):
        user_id= request.query_params.get('user_id')
        
        if user_id:
            try:
                user= self.queryset.get(id=user_id)
                serializer = self.get_serializer(user)
                return Response(serializer.data,status=status.HTTP_200_OK)
            except TblUser.DoesNotExist:
                return Response({"detail":"User not found"},status=status.HTTP_404_NOT_FOUND)
        else:
            return super().list(request,*args,**kwargs)

from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

# from .models import UserReport, UserReportImage
from .serializers import ReportSerializer

@api_view(['POST'])
def create_report(request):
    """
    Create a user report with optional multiple images.
    """

    user = request.data.get("user")
    category = request.data.get("category")
    description = request.data.get("description")

    if not user or not category or not description:
        return Response(
            {"error": "user, category, description are required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 1️⃣ Create the report
    report = Reporttbl.objects.create(
        user_id=user,
        category=category,
        description=description,
    )

    # 2️⃣ Handle images
    images = request.FILES.getlist("images")
    for img in images:
        ReprotTblImage.objects.create(report=report, image=img)

    # 3️⃣ Return serialized response
    serializer = ReportSerializer(report)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Payment, Order
from .serializers import PaymentSerializer

@api_view(['POST'])
def make_payment(request):
    order_id = request.data.get('order')

    if not order_id:
        return Response({"error": "order field is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = PaymentSerializer(data=request.data)
    if serializer.is_valid():
        payment_type = serializer.validated_data.get('payment_type', 'both')
        serializer.save(order=order)  #FIXED
        
        # Update payment mode based on payment type
        payment_method = serializer.validated_data.get('payment_method')
        payment_mode_text = f"{payment_method}"
        
        if payment_type == 'table' or payment_type == 'both':
            order.table_payment_mode = payment_mode_text
            order.table_payment_status = 'pending' if payment_method == 'cash' else 'paid'
        
        if payment_type == 'both':
            order.food_payment_mode = payment_mode_text
            order.food_payment_status = 'pending' if payment_method == 'cash' else 'paid'
            order.save(update_fields=['table_payment_mode', 'food_payment_mode', 'table_payment_status', 'food_payment_status'])
        
        elif payment_type == 'table':
            order.save(update_fields=['table_payment_mode', 'table_payment_status'])
        
        return Response({
            "status": "success",
            "message": "Payment processed successfully",
            "data": {
                "order_id": order.id,
                "payment_id": serializer.instance.id if serializer.instance else None,
                "payment_method": serializer.validated_data.get('payment_method'),
                "payment_type": serializer.validated_data.get('payment_type', 'both'),
                # "order_payment_mode": order.payment_mode,
                "table_payment_mode": order.table_payment_mode,
                "food_payment_mode": order.food_payment_mode,
                "table_payment_status": order.table_payment_status,
                "food_payment_status": order.food_payment_status
            }
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Order
from .serializers import OrderDetailSerializer


@api_view(['GET'])
def view_order(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = OrderDetailSerializer(order)
    return Response(serializer.data, status=status.HTTP_200_OK)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from .models import Table, Seat, OrderSeat, Order
from adminapp.models import TblTimeSlot  # Import time slot model

@api_view(['GET'])
def get_all_tables_and_seats(request):
    """
    Fetch all tables and seats, showing which seats are booked for a given date,
    category, and time slot (by ID).
    Example:
        /userapp/get-tables/?date=2025-11-05
        /userapp/get-tables/?date=2025-11-05&category=2
        /userapp/get-tables/?date=2025-11-05&time_slot=5
        /userapp/get-tables/?date=2025-11-05&category=2&time_slot=5
    """
    # --- Step 1: Get and validate date ---
    date_str = request.query_params.get('date')
    if not date_str:
        return Response({"error": "Please provide a date in ?date=YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        booking_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

    # --- Step 2: Optional filters ---
    category_id = request.query_params.get('category')
    time_slot_id = request.query_params.get('time_slot')

    order_filter = {"date": booking_date}
    if category_id:
        order_filter["category_id"] = category_id
    if time_slot_id:
        try:
            slot = TblTimeSlot.objects.get(id=time_slot_id)
            # Match time slot string (example: "10:00 AM - 12:00 PM")
            order_filter["time_slot_id"] = time_slot_id
        except TblTimeSlot.DoesNotExist:
            return Response({"error": "Invalid time_slot ID"}, status=status.HTTP_404_NOT_FOUND)

    # --- Step 3: Get booked seat IDs ---
    booked_seats = OrderSeat.objects.filter(
        order__in=Order.objects.filter(**order_filter)
    ).values_list('seat_id', flat=True)

    # --- Step 4: Build response with seat status ---
    tables = Table.objects.prefetch_related('seats').all()
    response_data = []
    for table in tables:
        seat_list = []
        for seat in table.seats.all():
            seat_list.append({
                "id": seat.id,
                "seat_number": seat.seat_number,
                "is_booked": seat.id in booked_seats
            })

        response_data.append({
            "id": table.id,
            "table_name": table.table_name,
            "number_of_seats": table.number_of_seats,
            "seats": seat_list
        })

    # --- Step 5: Return API response ---
    return Response({
        "status": "success",
        "total_tables": tables.count(),
        "filters": {
            "date": str(booking_date),
            "category": category_id,
            "time_slot_id": time_slot_id
        },
        "data": response_data
    }, status=status.HTTP_200_OK)

# userapp/views.py

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Feedback, Order
from .serializers import FeedbackSerializer,FeedbackListSerializer,UserOrderSerializer

@api_view(['POST'])
def create_feedback(request):
    serializer = FeedbackSerializer(data=request.data)

    if serializer.is_valid():
        # Check if any food items in the order are today's special
        order_id = request.data.get('order')
        if order_id:
            from adminapp.models import TodaysSpecial
            from datetime import date
            today = date.today()
            
            # Get the order
            order = Order.objects.get(id=order_id)
            
            # Only restrict feedback for PREBOOKED orders with today's special
            # Allow feedback for TABLE_ONLY orders with today's special (food added via QR)
            if order.booking_type == 'PREBOOKED':
                for order_item in order.items.all():
                    if TodaysSpecial.objects.filter(
                        name=order_item.food_item.name,
                        category=order_item.food_item.category,
                        date=today
                    ).exists():
                        return Response({
                            "error": f"Cannot submit feedback for PREBOOKED order containing today's special items"
                        }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save()
        return Response({
            "message": "Feedback submitted successfully"
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_user_feedback(request, user_id):
    """Fetch all feedbacks submitted by a particular user, including item ratings."""

    feedbacks = Feedback.objects.filter(user_id=user_id).order_by('-created_at')

    if not feedbacks.exists():
        return Response({
            "status": "success",
            "user_id": user_id,
            "total_feedbacks": 0,
            "data": []
        }, status=status.HTTP_200_OK)

    serializer = FeedbackListSerializer(feedbacks, many=True)

    return Response({
        "status": "success",
        "user_id": user_id,
        "total_feedbacks": feedbacks.count(),
        "data": serializer.data
    }, status=status.HTTP_200_OK)
    
    
class OrderListView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id')

        if not user_id:
            return Response(
                {"error": "User ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # FIX: use 'date' or 'created_at'
        orders = Order.objects.filter(user_id=user_id).order_by('-created_at')

        serializer = UserOrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
@api_view(['POST'])
def cancel_order(request):
    """
    Cancel entire order - free all seats in the order
    Body: {"order_id": 1}
    """
    order_id = request.data.get('order_id')
    
    if not order_id:
        return Response(
            {"error": "order_id is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response(
            {"error": "Order not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check if user owns this order
    user_id = request.data.get('user_id')
    if user_id and order.user.id != int(user_id):
        return Response(
            {"error": "You can only cancel your own orders"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Check 1-hour restriction
    from django.utils import timezone
    from datetime import timedelta
    
    if order.date and order.time_slot:
        booking_datetime = timezone.make_aware(
            timezone.datetime.combine(order.date, order.time_slot.start_time)
        )
        current_time = timezone.now()
        
        time_difference = booking_datetime - current_time
        if time_difference <= timedelta(hours=1):
            return Response(
                {"error": "Cancellation not allowed within 1 hour of booking time"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Cancel all seats in the order
    seats_cancelled = 0
    for order_seat in order.order_seats.all():
        order_seat.seat.is_occupied = False
        order_seat.seat.save()
        order_seat.delete()
        seats_cancelled += 1
    
    # Reset order tables and charges
    order.tables = []
    order.table_charge = 0
    order.update_total()
    order.save()
    
    # Send cancellation email
    try:
        from django.core.mail import send_mail
        from django.template.loader import render_to_string
        from django.utils.html import strip_tags
        
        if order.user and order.user.email:
            subject = f"Order Cancellation - Order #{order_id}"
            
            context = {
                'order': order,
                'seats_freed': seats_cancelled,
                'user': order.user,
                'cancellation_time': timezone.now(),
                'cancellation_policy': '1 hour'  # Add policy info
            }
            
            html_message = render_to_string('email/order_cancellation.html', context)
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email='noreply@biteandseat.com',
                recipient_list=[order.user.email],
                html_message=html_message,
                fail_silently=False
            )
            print(f"Cancellation email sent to {order.user.email}")
    except Exception as e:
        print(f"Failed to send cancellation email: {e}")

    return Response(
        {
            "message": f"Order #{order_id} cancelled successfully. {seats_cancelled} seat(s) freed.",
            "status": "cancelled",
            "seats_freed": seats_cancelled
        },
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
def get_todays_special(request):
    """
    GET: Get today's special items for users
    Query param: ?date=2026-01-28 (optional, defaults to today)
    """
    date_str = request.query_params.get('date')
    
    if date_str:
        try:
            from datetime import datetime
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Don't allow future dates for today's special
            from datetime import date
            today = date.today()
            if date_obj > today:
                return Response(
                    {"error": "Cannot view today's special for future dates"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST
            )
    else:
        from datetime import date
        date_obj = date.today()
    
    from adminapp.models import TodaysSpecial
    specials = TodaysSpecial.objects.filter(date=date_obj)
    
    # Convert to similar format as menu items
    response_data = []
    for special in specials:
        response_data.append({
            'id': special.id,
            'name': special.name,
            'image': special.image.url if special.image else None,
            'rate': str(special.rate),
            'item_per_plate': special.item_per_plate,
            'category': special.category.id,
            'category_name': special.category.name,
            'is_todays_special': True,
            'item_source': "Today's Special",  # Add this line
            'booking_restrictions': {
                'can_be_booked_by_users_prebooked': False,
                'can_be_booked_by_users_table_only': True,
                'can_be_booked_by_admin': True,
                'message': 'Available through: 1) Admin outsider booking, 2) TABLE_ONLY booking'
            }
        })
    
    return Response(response_data)