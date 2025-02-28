from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import timedelta
import random
from django.contrib.auth import get_user_model
class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # เชื่อมกับ auth.User
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return self.created_at + timedelta(minutes=5) > now()  # OTP ใช้ได้ 5 นาที

    @staticmethod
    def generate_otp():
        return str(random.randint(100000, 999999))  # สุ่ม OTP 6 หลัก


class Flour(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=5, decimal_places=2)

class Filling(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=5, decimal_places=2)

class Topping(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=5, decimal_places=2)

class Sauce(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=5, decimal_places=2)




class OrderGroup(models.Model):
    STATUS_CHOICES = [
        ('pending', 'รอดำเนินการ'),
        ('Order received', 'รับออเดอร์แล้ว'),
        ('confirmed', 'กำลังดำเนินการ'),
        ('completed', 'เสร็จสิ้น รอชำระเงิน'),
        ('paid', 'ชำระเงินเสร็จสิ้น'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    queue_number = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="order_groups",
        null=True,  # ✅ อนุญาตให้เป็น NULL ได้ชั่วคราว
        blank=True,
    )

class Order(models.Model):
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="orders",
        null=True,  # อนุญาตให้เป็น NULL ได้
        blank=True
    )
    flour = models.CharField(max_length=255, blank=True)
    filling = models.CharField(max_length=255, blank=True)
    topping = models.CharField(max_length=255, blank=True)
    sauce = models.CharField(max_length=255, blank=True)
    quantity = models.IntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    # ✅ ใช้ ForeignKey เชื่อมไปที่ OrderGroup
    order_group = models.ForeignKey(OrderGroup, on_delete=models.CASCADE, related_name="orders", null=True, blank=True)
        # ✅ เพิ่มฟิลด์ note รองรับข้อความจากลูกค้า
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Order {self.id} - {self.total_price} ฿"

