from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.db import models
from adminapp.models import *

# class tbl_register(models.Model):
#     USER_TYPES = [
#         ('student', 'Student'),
#         ('faculty', 'Faculty'),
#     ]

#     username = models.CharField(max_length=100)
#     password = models.CharField(max_length=100)
#     user_type = models.CharField(max_length=10, choices=USER_TYPES)
#     batch_name = models.CharField(max_length=20, null=True, blank=True)
#     department = models.CharField(max_length=100, null=True, blank=True)
#     profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)

#     def __str__(self):
#         return f"{self.username} ({self.user_type})"


class TblUser(models.Model):
    USER_TYPES = [
        ('student', 'Student'),
        ('faculty', 'Faculty'),
    ]

    username = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True, null=True, blank=True)
    password = models.CharField(max_length=100)
    user_type = models.CharField(max_length=10, choices=USER_TYPES)
    batch_name = models.CharField(max_length=20, null=True, blank=True)
    department = models.CharField(max_length=100, null=True, blank=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    registration_status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
        default='pending'
    )
    registered_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.username} ({self.user_type})"


class UserSelection(models.Model):
    user = models.ForeignKey(TblUser, on_delete=models.CASCADE)
    selected_category = models.ForeignKey(Category, on_delete=models.CASCADE)
    selected_food = models.ForeignKey(TblMenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)  # added quantity
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} selected {self.selected_food.name} ({self.selected_category}) x{self.quantity}"
    

from django.db import models
from adminapp.models import TblTimeSlot  # adjust import based on your structure

class Booking(models.Model):
    selected_date = models.DateField()
    timeslot = models.ForeignKey(TblTimeSlot, on_delete=models.CASCADE)
    num_persons = models.PositiveIntegerField(default=1)
    # qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking on {self.selected_date} for {self.timeslot}"
    
class SeatBooking(models.Model):
    user = models.ForeignKey(TblUser, on_delete=models.CASCADE)
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    booking_time = models.DateTimeField(auto_now_add=True)
    booking_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # 👈 add this






from decimal import Decimal

from django.db import models
from adminapp.models import TblMenuItem, Category
from userapp.models import TblUser, Table, Seat


class Order(models.Model):
    BOOKING_TYPES = [
        ('TABLE_ONLY', 'Table Only'),
        ('PREBOOKED', 'Prebooked (Table + Food)'),
        ('ONSPOT', 'On-the-Spot (Table + Food)'),
    ]

    PAYMENT_METHODS = [ 
        ('upi', 'UPI'),
        ('card', 'Card'),
        ('cash', 'Cash')
    ]

    BOOKING_STATUS = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    booking_status = models.CharField(
        max_length=20, 
        choices=BOOKING_STATUS, 
        default='pending'
    )

    user = models.ForeignKey(TblUser, on_delete=models.CASCADE, null=True, blank=True)
    
    # Outsider fields (Admin booking)
    outsider_name = models.CharField(max_length=100, null=True, blank=True)
    outsider_phone = models.CharField(max_length=20, null=True, blank=True)
    
    booking_type = models.CharField(max_length=25, choices=BOOKING_TYPES, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField(null=True, blank=True)

    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE, null=True, blank=True)
    number_of_persons = models.PositiveIntegerField(null=True, blank=True)

    # Instead of ManyToMany seats — link to table only
    tables = models.JSONField(default=list, blank=True)
    table_charge = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)

    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    # payment_mode = models.CharField(max_length=50, default='Cash') # split - table payment mode, food payment mode
    
    # Split payment tracking
    table_payment_mode = models.CharField(max_length=50, default='cash', choices= PAYMENT_METHODS)
    food_payment_mode = models.CharField(max_length=50, default='cash', choices= PAYMENT_METHODS)
    table_payment_status = models.CharField(max_length=20, default='pending', choices=[('pending', 'Pending'), ('paid', 'Paid')])
    food_payment_status = models.CharField(max_length=20, default='pending', choices=[('pending', 'Pending'), ('paid', 'Paid')])

    is_completed = models.BooleanField(default=False) #make true after scanning QR code at restaurant

    created_at = models.DateTimeField(auto_now_add=True)

    def update_total(self):
        food_total = sum(item.total_price for item in self.items.all())
        table_charge = self.table_charge or Decimal('0.00')
        self.total_amount = table_charge + Decimal(food_total)
        self.save()

    def get_food_total(self):
        """Calculate total food amount for email template"""
        return sum(item.total_price for item in self.items.all())


    def __str__(self):
        return f"Order #{self.id} - {self.user.username} ({self.get_booking_type_display()})"
        
class OrderSeat(models.Model):
    """Stores seats booked for a particular order."""
    order = models.ForeignKey(Order, related_name='order_seats', on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)

    def cancel_seat(self):
        """
        Cancel this seat booking if more than 30 minutes before booking time
        Returns: (success, message)
        """
        from django.utils import timezone
        from datetime import timedelta
        
        # Get booking date and time
        booking_date = self.order.date
        time_slot = self.order.time_slot
        
        if not booking_date or not time_slot:
            return False, "Invalid booking information"
        
        # Calculate booking datetime
        booking_datetime = timezone.make_aware(
            timezone.datetime.combine(booking_date, time_slot.start_time)
        )
        current_time = timezone.now()
        
        # Check if less than 30 minutes before booking
        time_difference = booking_datetime - current_time
        if time_difference <= timedelta(minutes=30):
            return False, "Cancellation not allowed within 30 minutes of booking time"
        
        # Free the seat
        self.seat.is_occupied = False
        self.seat.save()
        
        # Remove from order tables list
        order_tables = self.order.tables
        for table_info in order_tables:
            if self.seat.id in table_info.get('seat_ids', []):
                table_info['seat_ids'].remove(self.seat.id)
                # If no seats left in table, remove table from order
                if not table_info['seat_ids']:
                    order_tables.remove(table_info)
                break
        
        self.order.tables = order_tables
        self.order.table_charge -= self.seat.seat_price
        self.order.update_total()
        self.order.save()
        
        # Delete this seat booking
        self.delete()
        
        return True, f"Seat {self.seat.seat_number} cancelled successfully"

    def save(self, *args, **kwargs):
        # Mark seat as occupied when booked
        self.seat.is_occupied = True
        self.seat.save()
        super().save(*args, **kwargs)
        table_id = self.seat.table.id
        if table_id not in self.order.tables:
            updated_tables = self.order.tables
            updated_tables.append(table_id)
            self.order.tables = updated_tables
            self.order.save()

    def __str__(self):
        return f"{self.order} - {self.seat}"
        

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    food_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.price = self.food_item.rate
        self.total_price = self.food_item.rate * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.food_item.name} x {self.quantity}"


from django.db import models
from .models import Order

class Payment(models.Model):
    PAYMENT_METHODS = [ 
        ('upi', 'UPI'),
        ('card', 'Card'),
        ('cash', 'Cash')
    ]

    PAYMENT_TYPES = [
        ('table', 'Table Payment'),
        ('both', 'Table + Food Payment'),
    ]
    
    payment_type = models.CharField(max_length=10, choices=PAYMENT_TYPES, default='both')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS)
    upi_id = models.CharField(max_length=100, blank=True, null=True)
    cardholder_name = models.CharField(max_length=100, blank=True, null=True)
    card_number = models.CharField(max_length=16, blank=True, null=True)
    expiry_date = models.CharField(max_length=5, blank=True, null=True)
    cvv_number = models.CharField(max_length=4, blank=True, null=True)
    payment_status = models.CharField(max_length=50, default='success')
    payment_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Update order payment status based on payment type
        if self.order.booking_type == 'PREBOOKED':
            payment_mode_text = f"{self.get_payment_method_display()}"
            
            if self.payment_type == 'table' or self.payment_type == 'both':
                self.order.table_payment_mode = payment_mode_text
                self.order.table_payment_status = 'paid'
            
            if self.payment_type == 'food' or self.payment_type == 'both':
                self.order.food_payment_mode = payment_mode_text
                self.order.food_payment_status = 'paid'
            
            # For backward compatibility
            if self.payment_type == 'both':
                self.order.payment_mode = payment_mode_text
            
            self.order.save()
            
            #  Send payment confirmation email only for app payments (not cash)
            if self.payment_method != 'cash':
                self.send_payment_email()
    
    def send_payment_email(self):
        """Send payment confirmation email to user"""
        
        if self.order.user and self.order.user.email:
            subject = f"Payment Confirmation - Order #{self.order.id}"
            
            # Create email content
            context = {
                'order': self.order,
                'payment': self,
                'user': self.order.user
            }
            
            html_message = render_to_string('email/payment_confirmation.html', context)
            plain_message = strip_tags(html_message)
            
            try:
                send_mail(
                    subject=subject,
                    message=plain_message,
                    from_email='noreply@biteandseat.com',
                    recipient_list=[self.order.user.email],
                    html_message=html_message,
                    fail_silently=False
                )
                print(f"Payment confirmation email sent to {self.order.user.email}")
            except Exception as e:
                print(f" Failed to send email: {e}")

    def __str__(self):
        return f"Payment for Order #{self.order.id}"

    
from userapp.models import TblUser


class Reporttbl(models.Model):
    user = models.ForeignKey(TblUser, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.CharField(max_length=50)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)



    def __str__(self):
        return f"Report #{self.id} - {self.category}"


class ReprotTblImage(models.Model):
    report = models.ForeignKey(Reporttbl, related_name="report_images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="user_report_images/")

    def __str__(self):
        return f"Image for Report #{self.report.id}"


from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import TblUser, Order  # adjust import as needed

# class Feedback(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     order = models.ForeignKey(Order, on_delete=models.CASCADE)
#     rating = models.IntegerField(
#         validators=[MinValueValidator(1), MaxValueValidator(5)]
#     )
#     feedback = models.TextField()
#     image = models.ImageField(upload_to='feedback_images/', null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Feedback by {self.user.username} for Order {self.order.id}"


class Feedback(models.Model):
    user = models.ForeignKey(TblUser, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    overall_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    comments = models.TextField(null=True, blank=True)
    # image = models.ImageField(upload_to='feedback_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback by {self.user.username}"
    
class FeedbackItem(models.Model):
    feedback = models.ForeignKey(
        Feedback, on_delete=models.CASCADE, related_name="items"
    )
    food_item = models.ForeignKey(TblMenuItem, on_delete=models.CASCADE)

    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    def __str__(self):
        return f"{self.food_item.name} - {self.rating}"