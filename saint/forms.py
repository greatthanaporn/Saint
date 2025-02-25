from django import forms
from .models import User


#-----------------ฟอร์มรับอีเมล

class EmailForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'กรอกอีเมลของคุณ',
    }))

#---------------------ฟอร์มกรอก OTP
class OTPForm(forms.Form):
    otp = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'กรอก OTP ที่ได้รับ',
    }))


#----------