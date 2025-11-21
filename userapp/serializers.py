from rest_framework import serializers
from .models import *


# class tbl_registerSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = '__all__'

#     def validate(self, data):
#         if data.get('user_type') == 'student':
#             if not data.get('batch_name') or not data.get('department'):
#                 raise serializers.ValidationError("Students must have batch_id and department.")
#         return data
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TblUser
        fields = [
            'id',
            'username',
            'password',
            'user_type',
            'batch_name',
            'department',
            'profile_photo'
        ]
        
from rest_framework import serializers
from .models import Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)  # include category info

    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'image', 'rate', 'item_per_plate', 'category']
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if instance.image:
            rep['image'] = instance.image.url
        return rep
    

from rest_framework import serializers
from .models import Category, MenuItem, UserSelection

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class MenuItemSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()
    image = serializers.SerializerMethodField()  # Use method field

    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'rate', 'item_per_plate', 'image', 'category']

    def get_image(self, obj):
        if obj.image:
            return f"media/{obj.image.name}"  # Return relative media path
        return None
    
class DailyMenuSerializer(serializers.ModelSerializer):
    items = MenuItemSerializer(many=True, read_only=True)  # nested items

    class Meta:
        model = TblDailyMenu
        fields = ['id', 'date', 'items']
    
        
from rest_framework import serializers
from .models import UserSelection

class UserSelectionSerializer(serializers.ModelSerializer):
    selected_category = serializers.StringRelatedField()
    selected_food = serializers.StringRelatedField()
    user = serializers.StringRelatedField()

    class Meta:
        model = UserSelection
        fields = ['id', 'user', 'selected_category', 'selected_food', 'quantity', 'created_at']


class CreateUserSelectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSelection
        fields = ['user', 'selected_category', 'selected_food', 'quantity']


from rest_framework import serializers
from .models import TblTimeSlot

class TimeSlotSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = TblTimeSlot
        fields = ['id', 'category_name', 'category_id', 'start_time', 'end_time']

from rest_framework import serializers
from .models import Booking

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['id', 'selected_date', 'timeslot', 'num_persons', 'qr_code', 'created_at']
        read_only_fields = ['qr_code', 'created_at']


from rest_framework import serializers
from .models import Seat, SeatBooking


# class TableSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Table
#         fields = ['id', 'table_name', 'number_of_seats']


# class SeatSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Seat
#         fields = ['id', 'seat_number', 'seat_price', 'is_occupied', 'table']

from rest_framework import serializers
from .models import SeatBooking

class SeatBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeatBooking
        fields = ['id', 'user', 'table', 'seat', 'booking_time', 'booking_charge']
        read_only_fields = ['booking_time', 'booking_charge']


from rest_framework import serializers
from .models import Order, OrderItem, OrderSeat
from userapp.models import Seat, Table


class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = ['id', 'seat_number', 'seat_price', 'is_occupied', 'table']


class OrderSeatSerializer(serializers.ModelSerializer):
    seat = SeatSerializer(read_only=True)

    class Meta:
        model = OrderSeat
        fields = ['id', 'seat']


class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):
    food_item_name = serializers.CharField(source='food_item.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'food_item', 'food_item_name', 'quantity', 'price', 'total_price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    table = TableSerializer(read_only=True)
    order_seats = OrderSeatSerializer(many=True, read_only=True)
    
    # Add time slot details automatically
    time_slot_id = serializers.IntegerField(source='time_slot.id', read_only=True)
    slot_start_time = serializers.TimeField(source='time_slot.start_time', read_only=True)
    slot_end_time = serializers.TimeField(source='time_slot.end_time', read_only=True)
    slot_category_name = serializers.CharField(source='time_slot.category.name', read_only=True)

    class Meta:
        model = Order
        fields = '__all__' 


from rest_framework import serializers
from .models import UserReportImage,UserReport


class ReportImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserReportImage
        fields = ['id', 'image']


class ReportSerializer(serializers.ModelSerializer):
    images = ReportImageSerializer(many=True, read_only=True)

    class Meta:
        model = UserReport
        fields = ['id', 'user', 'category', 'description', 'images', 'created_at']




from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

    def validate(self, data):
        """
        Ensure correct fields are provided based on payment method.
        """
        method = data.get('payment_method')

        if method == 'upi':
            if not data.get('upi_id'):
                raise serializers.ValidationError({"upi_id": "UPI ID is required for UPI payments"})
        elif method == 'card':
            required_fields = ['cardholder_name', 'card_number', 'expiry_date', 'cvv_number']
            for field in required_fields:
                if not data.get(field):
                    raise serializers.ValidationError({field: f"{field.replace('_', ' ').capitalize()} is required for card payments"})
        else:
            raise serializers.ValidationError({"payment_method": "Invalid payment method"})

        return data





from rest_framework import serializers
from .models import Order, OrderItem, Payment

class OrderItemSerializer(serializers.ModelSerializer):
    food_item_id = serializers.IntegerField(source='food_item.id', read_only=True)
    food_item_name = serializers.CharField(source='food_item.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['food_item_id', 'food_item_name', 'quantity', 'price', 'total_price']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['payment_method', 'payment_status', 'payment_date']


class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'booking_type', 'category', 'date', 'time_slot',
            'number_of_persons', 'tables', 'table_charge', 'total_amount',
            'payment_mode', 'items', 'payments', 'created_at'
        ]


class SeatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = ['id', 'seat_number', 'seat_price', 'is_occupied']

class TablesSerializer(serializers.ModelSerializer):
    seats = SeatsSerializer(many=True, read_only=True)

    class Meta:
        model = Table
        fields = ['id', 'table_name', 'number_of_seats', 'seats']


# from rest_framework import serializers
# from .models import Feedback

# class FeedbackSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Feedback
#         fields = ['id', 'user', 'order', 'rating', 'feedback', 'image', 'created_at']

class FeedbackItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackItem
        fields = ['food_item', 'rating']


class FeedbackSerializer(serializers.ModelSerializer):
    items = FeedbackItemSerializer(many=True, write_only=True)

    class Meta:
        model = Feedback
        fields = ['user', 'order', 'overall_rating', 'comments', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items')  # Extract nested items
        feedback = Feedback.objects.create(**validated_data)

        for item in items_data:
            FeedbackItem.objects.create(feedback=feedback, **item)

        return feedback

class FeedbackItemsSerializer(serializers.ModelSerializer):
    food_item_name = serializers.CharField(source="food_item.name", read_only=True)

    class Meta:
        model = FeedbackItem
        fields = ["food_item", "food_item_name", "rating"]

class FeedbackListSerializer(serializers.ModelSerializer):
    items = FeedbackItemsSerializer(many=True, read_only=True)

    class Meta:
        model = Feedback
        fields = [
            "user",
            "order",
            "overall_rating",
            "comments",
            "items"
        ]

class UsersSerializer(serializers.ModelSerializer):
    profile_photo = serializers.SerializerMethodField()

    class Meta:
        model = TblUser
        fields = [
            'id',
            'username',
            'password',
            'user_type',
            'batch_name',
            'department',
            'profile_photo'
        ]

    def get_profile_photo(self, obj):
        if obj.profile_photo:
            return f"media/{obj.profile_photo.name}"   # <-- FIXED
        return None
    
    
class OrderItemsSerializer(serializers.ModelSerializer):
    food_name = serializers.CharField(source='food_item.name')

    class Meta:
        model = OrderItem
        fields = ['food_name', 'quantity', 'price', 'total_price']
        
        
class SeatssSerializer(serializers.ModelSerializer):
    seat_number = serializers.IntegerField(source="seat.seat_number")
    seat_price = serializers.DecimalField(source="seat.seat_price", max_digits=6, decimal_places=2)
    table_name = serializers.CharField(source="seat.table.table_name")

    class Meta:
        model = OrderSeat
        fields = ['seat_number', 'seat_price', 'table_name']

class UserOrderSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    items = OrderItemsSerializer(many=True)
    seats = serializers.SerializerMethodField()
    tables = serializers.SerializerMethodField()
    time_slot = serializers.CharField(source="time_slot.__str__", read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'user_id',
            'booking_type',
            'date',
            'category',
            'time_slot',
            'number_of_persons',
            'tables',
            'seats',
            'total_amount',
            'payment_mode',
            'items',
            'created_at'
        ]

    def get_seats(self, obj):
        seats = obj.order_seats.all()
        return SeatssSerializer(seats, many=True).data

    def get_tables(self, obj):
        from userapp.models import Table
        
        raw_tables = obj.tables
        table_ids = []

        for t in raw_tables:  
            if isinstance(t, int):
                table_ids.append(t)

            elif isinstance(t, str) and t.isdigit():
                table_ids.append(int(t))

            elif isinstance(t, dict) and "table_id" in t:
                table_ids.append(int(t["table_id"]))

        # queryset
        tables = Table.objects.filter(id__in=table_ids)
        return [t.table_name for t in tables]