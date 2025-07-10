from django.urls import path
from . import views


urlpatterns = [
    path('login/', views.staff_login_view, name='staff_login'),
    path('dashboard/', views.staff_dashboard_view, name='staff_dashboard'),
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('request/<int:request_id>/', views.request_detail_view, name='staff_request_detail'),
    path('customers/', views.customer_list_view, name='customer_list'),
    path('tickets/', views.staff_ticket_list_view, name='staff_ticket_list'),
    path('tickets/<int:ticket_id>/', views.staff_ticket_detail_view, name='staff_ticket_detail'),
    path('users/', views.admin_user_list_view, name='admin_user_list'),
    path('users/<int:user_id>/edit/', views.admin_user_edit_choice_view, name='admin_user_edit_choice'), 
    path('users/<int:user_id>/edit/simple/', views.admin_user_edit_simple_view, name='admin_user_edit_simple'),
    path('customers/<int:user_id>/print/', views.print_customer_info_view, name='print_customer_info'),
    path('users/add/', views.admin_add_user_view, name='admin_add_user'),
]