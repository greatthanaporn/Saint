from django.urls import path
from .import views
from .views import request_otp, verify_otp

urlpatterns = [
    path('', views.order_crepe, name='order_crepe'),
    path('cart/', views.cart, name='cart'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('profile/', views.profile, name='profile'),
    
    path('login/', request_otp, name='request_otp'),
    path('verify/', verify_otp, name='verify_otp'),

    # เส้นทางอื่น ๆ
]
