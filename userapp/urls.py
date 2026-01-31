from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny

from .views import get_todays_special  # Add this import

from .views import *
from . import views

# from .views import CreateBookingView

# DRF Router
router = routers.DefaultRouter()


# Swagger schema view
schema_view = get_schema_view(
    openapi.Info(
        title="My API",
        default_version='v1',
        description="API documentation for my project",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="support@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # API routes at root
    path('', include(router.urls)),

    # Swagger UI
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    # ReDoc UI
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Raw JSON/YAML schema
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger.yaml', schema_view.without_ui(cache_timeout=0), name='schema-yaml'),

    # Login API
    # path('register/', RegisterUserAPI.as_view(), name='    '),


    path('login/', login_view, name='login'),
    path('register/', register_user, name='register_user'),
    path('categories/', CategoryListAPIView.as_view(), name='api_category_list'),  # API
    path('menu/', MenuItemListAPIView.as_view(), name='api_menu_list'),  # API endpoint
    path('menu/<int:category_id>/', MenuByCategoryAPIView.as_view(), name='api_menu_by_category'),
    path('select/', select_food, name='select_food'),
    path('selections/', view_all_selections, name='view_all_selections'),
    path('user-time-slots/', views.user_time_slots, name='user_time_slots'),
    path('submit-booking/', views.submit_booking, name='submit_booking'),
    path('daily-menus/', daily_menus_api, name='daily-menus-api'),
    path('todays-special/', get_todays_special, name='user_todays_special'),
    path('seats/<int:table_id>/', views.available_seats, name='available-seats'),
    path('book-seat/', views.book_multiple_seats, name='book-seat'),
    path('create-step1/', views.create_step1, name='create-step1'),
    path('update-step2/<int:order_id>/', views.update_step2, name='update-step2'),
    path('update-step3/<int:order_id>/', views.update_step3, name='update-step3'),
    # path('finalize-order/<int:order_id>/', views.finalize_order, name='finalize-order'),
    path('view_profile/',UserProfileView.as_view({'get':'list'}),name='view_profile'),
    # path('profile/', user_profile, name='profile'),
    path('report/create/', create_report, name='create-report'),
    path('make-payment/', make_payment, name='make_payment'),
    path('view-order/<int:order_id>/', view_order, name='view-order'),
    path('all-tables-seats/', views.get_all_tables_and_seats, name='get_all_tables_and_seats'),
    path('feedback/create/', views.create_feedback, name='create_feedback'),
    path('feedback/<int:user_id>/', views.get_user_feedback, name='get_user_feedback'),
    path('orders-list/', OrderListView.as_view(), name='orders-list'),
    path('cancel-order/', cancel_order, name='cancel_order'),
    path('test-email/', test_email, name='test_email'),
]