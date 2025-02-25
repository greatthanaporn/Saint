from django.contrib.auth import login
from .models import OTP, User
from .forms import OTPForm
from django.shortcuts import render, redirect
from .forms import EmailForm
from .utils import send_otp_email


#-----------------------view สำหรับการกรอกอีเมล

def request_otp(request):
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            send_otp_email(email)  # ส่ง OTP ไปยังอีเมล
            request.session['email'] = email  # เก็บอีเมลใน session
            return redirect('verify_otp')  # ไปที่หน้ากรอก OTP
    else:
        form = EmailForm()
    return render(request, 'request_otp.html', {'form': form})


#------------------------- View สำหรับตรวจสอบ OTP

def verify_otp(request):
    email = request.session.get('email')
    if not email:
        return redirect('request_otp')

    if request.method == 'POST':
        form = OTPForm(request.POST)
        if form.is_valid():
            otp_input = form.cleaned_data['otp']
            user = User.objects.get(email=email)
            
            try:
                otp = OTP.objects.get(user=user, otp_code=otp_input)
                if otp.is_valid():
                    OTP.objects.filter(user=user).delete()  # ลบ OTP เมื่อใช้แล้ว
                    login(request, user)  # ล็อกอินผู้ใช้
                    return redirect('home')  # ไปหน้าหลัก
            except OTP.DoesNotExist:
                form.add_error('otp', 'OTP ไม่ถูกต้อง หรือหมดอายุแล้ว')

    else:
        form = OTPForm()

    return render(request, 'verify_otp.html', {'form': form})


def order_crepe(request):
    return render(request, 'order_crepe.html')



def cart(request):
    return render(request, 'cart.html')


def my_orders(request):
    return render(request, 'my_orders.html')


def profile(request):
    return render(request, 'profile.html')

