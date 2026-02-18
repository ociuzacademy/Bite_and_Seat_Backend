from django.contrib import admin

# Register your models here.
from .models import (
    Tbl_Admin, Category, MenuItem, DailyMenu,
    TimeSlot, Table, Seat, TodaysSpecial
)
# Note: TblMenuItem, TblDailyMenu, TblTimeSlot removed - using MenuItem, DailyMenu, TimeSlot instead

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'rate', 'is_todays_special', 'special_date')
    list_filter = ('category', 'is_todays_special', 'special_date')
    search_fields = ('name', 'category__name')
    ordering = ('-is_todays_special', 'category', 'name')
    
# OLD MODEL - Will be removed after migration
@admin.register(TodaysSpecial)
class TodaysSpecialAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'rate', 'date', 'created_at')
    list_filter = ('category', 'date', 'created_at')
    search_fields = ('name', 'category__name')
    ordering = ('-date', '-created_at')
    date_hierarchy = 'date'