import random
from django.core.mail import send_mail
from .models import OTP, User

def generate_otp():
    return str(random.randint(100000, 999999))  # สร้าง OTP 6 หลัก

def send_otp_email(user_email):
    otp = generate_otp()
    
    # ค้นหาผู้ใช้ หรือสร้างใหม่
    user, created = User.objects.get_or_create(email=user_email)

    # ลบ OTP เก่า
    OTP.objects.filter(user=user).delete()

    # บันทึก OTP ใหม่
    OTP.objects.create(user=user, otp_code=otp)

    # ส่งอีเมล
    send_mail(
        'Your OTP Code',
        f'Your OTP code is {otp}',
        'your_email@gmail.com',
        [user_email],
        fail_silently=False,
    )
