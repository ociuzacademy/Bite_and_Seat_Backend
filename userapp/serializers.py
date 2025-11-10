from rest_framework import serializers
from .models import *
# from django.contrib.auth.password_validation import validate_password

class tbl_registerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def validate(self, data):
        if data.get('user_type') == 'student':
            if not data.get('batch_name') or not data.get('department'):
                raise serializers.ValidationError("Students must have batch_id and department.")
        return data
    
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


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['id', 'user', 'report_content', 'image']



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


from rest_framework import serializers
from .models import Feedback

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['id', 'user', 'order', 'rating', 'feedback', 'image', 'created_at']