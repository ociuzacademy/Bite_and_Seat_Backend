from django.urls import path
from . import views
from .views import * #admin_login_view, scan_qr_complete_order, todays_special_list, create_todays_special
from django.shortcuts import render
from .views import add_category_view, category_list_view
from .views import time_slot_list, add_time_slot, edit_time_slot, delete_time_slot



urlpatterns = [
   path('', admin_login_view, name='admin_login'),
   path('admin_dashboard/',views.admin_dashboard, name='admin_dashboard'),
   path('add_category/', add_category_view, name='add_category'),
   path('category_list/', category_list_view, name='category_list'),
   path('category/edit/<int:category_id>/', views.edit_category_view, name='edit_category'),
   path('category/delete/<int:category_id>/', views.delete_category_view, name='delete_category'),
   path('menu/', views.menu_list, name='menu_list'),
   path('menu/add/', views.add_menu_item, name='add_menu'),
   path('menu/delete/<int:item_id>/', views.delete_menu_item, name='delete_menu'),
   path('menu/edit/<int:item_id>/', views.edit_menu_item, name='edit_menu'),
   path('add-daily-menu/', views.add_daily_menu, name='add_daily_menu'),
   path('daily-menu-list/', views.daily_menu_list, name='daily_menu_list'),
   path('timeslots/', time_slot_list, name='time_slot_list'),
   path('timeslots/add/', add_time_slot, name='add_time_slot'),
   path('timeslots/edit/<int:slot_id>/', edit_time_slot, name='edit_time_slot'),
   path('timeslots/delete/<int:slot_id>/', delete_time_slot, name='delete_time_slot'),
   path('tables/', views.table_list, name='table_list'),
   path('tables/add/', views.add_table, name='add_table'),
   path('tables/edit/<int:table_id>/', views.edit_table, name='edit_table'),
   path('tables/delete/<int:table_id>/', views.delete_table, name='delete_table'),
   path('tables/<int:table_id>/seats/', views.view_seats, name='view_seats'),
   path('edit-daily-menu/<int:id>/', views.edit_daily_menu, name='edit_daily_menu'),
   path('delete-daily-menu/<int:id>/', views.delete_daily_menu, name='delete_daily_menu'),
   path('orders/', views.admin_all_orders, name='admin_all_orders'),
   path('orders/<int:order_id>/', views.admin_order_detail, name='admin_order_detail'),
   path('cancelled-orders/', views.admin_cancelled_orders, name='admin_cancelled_orders'),
   path('reports/', views.reports_list, name='admin_view_all_reports'),
   path('feedbacks/', views.admin_view_all_feedbacks, name='admin_view_all_feedbacks'),
   path('view_scanner_data/',views.view_scanner_data,name='view_scanner_data'),
   path('scan-qr/', scan_qr_complete_order, name='scan_qr'),
   path('select-food/<int:order_id>/', views.admin_select_food, name='admin_select_food'),
   path('admin/outsider-booking/',views.admin_book_outsider, name='admin_book_outsider'),
   path('pending-users/', views.admin_pending_users, name='admin_pending_users'),
   path('approve-user/<int:user_id>/', views.admin_approve_user, name='admin_approve_user'),
   path('reject-user/<int:user_id>/', views.admin_reject_user, name='admin_reject_user'),
   path('admin_view_users/', views.admin_view_users, name='admin_view_users'),
   path('users/edit/<int:user_id>/', views.admin_edit_user, name='admin_edit_user'),
   path('users/delete/<int:user_id>/', views.admin_delete_user, name='admin_delete_user'),
   path('api/todays-special/', todays_special_list, name='todays_special_list'),
   path('api/todays-special/create/', create_todays_special, name='create_todays_special'),
   path('todays-special-page/', todays_special_page, name='todays_special_page'),
   path('add-todays-special-page/', add_todays_special_page, name='add_todays_special_page'),
   path('todays-special/edit/<int:special_id>/', views.edit_todays_special, name='edit_todays_special'),
   path('order-food/<int:order_id>/', views.admin_add_food_to_order, name='admin_add_food_to_order'),
]
