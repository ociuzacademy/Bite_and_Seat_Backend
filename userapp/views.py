from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SeatBookingSerializer, UserSerializer
from .models import TblUser, UserReport, UserReportImage
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

from rest_framework import generics, permissions
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

        # ✅ If booking type is PREBOOKED, add food items
        if order.booking_type == 'PREBOOKED':
            items = request.data.get('items', [])
            for item_data in items:
                food_id = item_data.get('food_item')
                quantity = int(item_data.get('quantity', 1))
                try:
                    food = TblMenuItem.objects.get(id=food_id)
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

from .models import UserReport, UserReportImage
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
    report = UserReport.objects.create(
        user_id=user,
        category=category,
        description=description,
    )

    # 2️⃣ Handle images
    images = request.FILES.getlist("images")
    for img in images:
        UserReportImage.objects.create(report=report, image=img)

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
        serializer.save(order=order)  # ✅ FIXED
        order.payment_mode = serializer.validated_data.get('payment_method')
        order.save(update_fields=['payment_mode'])
        
        return Response({
            "message": "Payment successful",
            "order_id": order.id,
            "updated_payment_mode": order.payment_mode,
            "payment_details": serializer.data
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