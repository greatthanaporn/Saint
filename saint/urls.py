from django.urls import path
from .import views
from .views import request_otp, verify_otp

urlpatterns = [
    path('order-crepe', views.order_crepe, name='order_crepe'),
    path('cart/', views.cart, name='cart'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('profile/', views.profile, name='profile'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path("logout/", views.logout_view, name="logout"),

    # ลบสินค้าออกจากตะกร้า
    path('delete-order/<int:order_id>/', views.delete_order, name='delete_order'),

    # ยืนยันคำสั่งซื้อและส่งไปยังแอดมิน
    path('confirm-order/', views.confirm_order, name='confirm_order'),  
    path('order-history/', views.order_history, name='order_history'),  

    
    path("", request_otp, name="request_otp"),
    path("verify/", verify_otp, name="verify_otp"),
    path("accept-order/<int:queue_number>/", views.accept_order, name="accept_order"),
    path("complete-order/<int:queue_number>/", views.complete_order, name="complete_order"),
    path("mark-as-paid/<int:queue_number>/", views.mark_as_paid, name="mark_as_paid"),



    #Admin
    path('Dashboard/', views.Dashboard, name='Dashboard'),  # ✅ Dashboard ใช้ views.Dashboard
    path('admin-order/', views.admin_order, name='admin_order'),
    path('add-menu/', views.add_menu, name='add_menu'),
    path('edit-menu/', views.edit_menu, name='edit_menu'),
    path('delete-menu/<int:item_id>/<str:category>/', views.delete_menu, name='delete_menu'),
    path('get-order-details/<int:queue_number>/', views.get_order_details, name='get_order_details'),
    path('admin-order-history/', views.order_history_admin, name="order_history_admin"),


    # เส้นทางอื่น ๆ
]



