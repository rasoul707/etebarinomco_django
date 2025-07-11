from django.urls import path
from .views import (
    create_request_step1, 
    create_request_step2, 
    create_request_step3, 
    create_request_step4,
    user_dashboard_view,
    ticket_list_view,
    ticket_create_view,
    ticket_detail_view,
    request_start_view,
    request_initial_view,
    signature_view,
    validation_payment_view,
    validation_document_view,
    subscription_payment_view,
    guarantor_signature_view,
)


urlpatterns = [
    path('start/', request_start_view, name='request_start'),
    path('initial/', request_initial_view, name='request_initial'),
    path('request/validation_document/', validation_document_view, name='validation_document'),
    path('request/step1/', create_request_step1, name='create_request_step1'),
    path('request/step2/', create_request_step2, name='create_request_step2'),
    path('request/step3/', create_request_step3, name='create_request_step3'),
    path('request/step4/', create_request_step4, name='create_request_step4'),
    path('dashboard/', user_dashboard_view, name='user_dashboard'),

    path('tickets/', ticket_list_view, name='ticket_list'),
    path('tickets/create/', ticket_create_view, name='ticket_create'),
    path('tickets/<int:ticket_id>/', ticket_detail_view, name='ticket_detail'),
    path('request/signature/', signature_view, name='request_signature'),
    path('request/validation_payment/', validation_payment_view, name='validation_payment'),
    path('request/subscription_payment/', subscription_payment_view, name='subscription_payment'),
    path('request/guarantor-signature/', guarantor_signature_view, name='request_guarantor_signature'),
]
