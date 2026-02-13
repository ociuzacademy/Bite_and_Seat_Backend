from django.db import models

class Tbl_Admin(models.Model):
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.username
    

from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    


class MenuItem(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='menu_images/', null=True, blank=True)
    rate = models.DecimalField(max_digits=8, decimal_places=2)
    item_per_plate = models.CharField(max_length=100)
    is_todays_special = models.BooleanField(default=False)
    special_date = models.DateField(null=True, blank=True)

    def __str__(self):
        if self.is_todays_special and self.special_date:
            return f"{self.name} (Today's Special - {self.special_date})"
        return self.name


# No longer used - Use MenuItem instead
# This model will be removed after data migration
class TblMenuItem(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='menu_images/')
    rate = models.DecimalField(max_digits=8, decimal_places=2)
    item_per_plate = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} (OLD MODEL)"
    

class DailyMenu(models.Model):
    date = models.DateField(unique=True)
    items = models.ManyToManyField(MenuItem)  # selected menu items for that day

    def __str__(self):
        return f"Menu for {self.date.strftime('%A, %d %B %Y')}"
    

# No longer used - Use DailyMenu instead
# This model will be removed after data migration
class TblDailyMenu(models.Model):
    date = models.DateField(unique=True)
    items = models.ManyToManyField(TblMenuItem)  # selected menu items for that day

    def __str__(self):
        return f"Menu for {self.date.strftime('%A, %d %B %Y')} (OLD MODEL)"
    

class TimeSlot(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category__name', 'start_time']  # Sort by category name and time

    def __str__(self):
        return f"{self.category.name} ({self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')})"
    

# No longer used - Use TimeSlot instead
# This model will be removed after data migration
class TblTimeSlot(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        ordering = ['category__name', 'start_time']  # Sort by category name and time

    def __str__(self):
        return f"{self.category.name} ({self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}) (OLD MODEL)"
    


from django.db import models

class Table(models.Model):
    table_name = models.CharField(max_length=50)
    number_of_seats = models.PositiveIntegerField()

    def save(self, *args, **kwargs):
        # Allow only 2, 4, or 6 seats
        if self.number_of_seats not in [2, 4, 6]:
            raise ValueError("A table can only have 2, 4, or 6 seats.")
        super().save(*args, **kwargs)

        # Auto-create seats (reset if number changed)
        if self.seats.count() != self.number_of_seats:
            self.seats.all().delete()
            for i in range(1, self.number_of_seats + 1):
                Seat.objects.create(table=self, seat_number=i)

    def total_price(self):
        """Get total price of all seats."""
        return sum(seat.seat_price for seat in self.seats.all())

    def __str__(self):
        return f"{self.table_name} ({self.number_of_seats} seats)"


class Seat(models.Model):
    table = models.ForeignKey(Table, related_name='seats', on_delete=models.CASCADE)
    seat_number = models.PositiveIntegerField()
    seat_price = models.DecimalField(max_digits=6, decimal_places=2, default=5.00)
    is_occupied = models.BooleanField(default=False)  # New field

    class Meta:
        unique_together = ('table', 'seat_number')

    def __str__(self):
        status = "Occupied" if self.is_occupied else "Not Occupied"
        return f"{self.table.table_name} - Seat {self.seat_number} (₹{self.seat_price}) - {status}"

# No longer used - Use MenuItem with is_todays_special and special_date instead
# This model will be removed after data migration
class TodaysSpecial(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='todays_special/', null=True, blank=True)
    rate = models.DecimalField(max_digits=8, decimal_places=2)
    item_per_plate = models.CharField(max_length=100)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.date} ({self.category.name}) - Today's Special (OLD MODEL)"