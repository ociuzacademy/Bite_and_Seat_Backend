from django.contrib import admin

# Register your models here.
from .models import (
    Tbl_Admin, Category, MenuItem, TblMenuItem, DailyMenu, TblDailyMenu,
    TimeSlot, TblTimeSlot, Table, Seat, TodaysSpecial
)

@admin.register(TodaysSpecial)
class TodaysSpecialAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'rate', 'date', 'created_at')
    list_filter = ('category', 'date', 'created_at')
    search_fields = ('name', 'category__name')
    ordering = ('-date', '-created_at')
    date_hierarchy = 'date'