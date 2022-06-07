import datetime
from email.policy import default
from django import forms
from django.contrib.auth.models import User
from django.core.validators import RegexValidator


class RegisterForm(forms.Form):
    username = forms.CharField( required=True,min_length=5, max_length=20, widget=forms.TextInput(attrs={ 'class':"form-control form-control-lg", 
                                    'placeholder':"Tên tài khoản"}))
    password = forms.CharField( required=True, min_length=5, widget=forms.TextInput(attrs={ 'type':'password', 'class':"form-control form-control-lg", 
                                    'placeholder':"Mật khẩu"}))
    confirm_password = forms.CharField(required=True, label='Confirm password:', widget=forms.TextInput(attrs={ 'type':'password','class':"form-control form-control-lg", 
                                    'placeholder':"Xác nhận mật khẩu"}))        
    last_name = forms.CharField(required=True,widget=forms.TextInput(attrs={ 'class':"form-control form-control-lg", 
                                    'placeholder':"Họ"}))
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={ 'class':"form-control form-control-lg", 
                                    'placeholder':"Tên"}))                                
    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={ 'class':"form-control form-control-lg", 
                                    'placeholder':"Email"}))
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Xin vui lòng nhập đúng số điện thoại!")
    phone_number = forms.CharField(min_length=9,max_length=15,widget=forms.TextInput(attrs={ 'class':"form-control form-control-lg",'placeholder':"Số điện thoại"}),validators= [phone_regex])
    birth_date = forms.DateField(required= True, widget=forms.TextInput(attrs={'class': 'form-control', 'type':'date'}))
    address = forms.CharField(widget = forms.TextInput(attrs={'placeholder':'Địa chỉ'}))
    parish = forms.CharField(max_length= 100, widget=forms.TextInput(attrs={'placeholder':'Giáo xứ'}))


    def clean(self):
        data = super().clean()

        #check username exist
        username = data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(u'Tên tài khoản "'+username+'" đã tồn tại.')
        #check password and confirm password
        if data.get('password') != data.get('confirm_password'):
            raise forms.ValidationError('Mật khẩu xác nhận ko trùng khớp!')
        return data

class UserProfileForm(forms.Form):       
    last_name = forms.CharField(label ='Họ: ',required=True,widget=forms.TextInput(attrs={ 'class':"form-control form-control-lg", 
                                    'placeholder':"Họ"}))
    first_name = forms.CharField(label ='Tên: ',required=True, widget=forms.TextInput(attrs={ 'class':"form-control form-control-lg", 
                                    'placeholder':"Tên"}))                                
    email = forms.EmailField(label ='Email: ',required=True, widget=forms.TextInput(attrs={ 'class':"form-control form-control-lg", 
                                    'placeholder':"Email"}))
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Xin vui lòng nhập đúng số điện thoại!")
    phone_number = forms.CharField(label ='Số điện thoại: ',min_length=9,max_length=15,widget=forms.TextInput(attrs={ 'class':"form-control form-control-lg",'placeholder':"Số điện thoại"}),validators= [phone_regex])
    birth_date = forms.DateField(label ='Ngày sinh: ',required= True, widget=forms.TextInput(attrs={'class': 'form-control', 'type':'date'}))
    address = forms.CharField(label ='Địa chỉ: ',widget = forms.TextInput(attrs={'placeholder':'Địa chỉ'}))
    parish = forms.CharField(label ='Giáo xứ: ',max_length= 100, widget=forms.TextInput(attrs={'placeholder':'Giáo xứ'}))

    # def clean(self):
    #     data = super().clean()
    #     #if user tried changing username
    #     username = data.get('username')
    #     user = User.objects.filter(username = username).exists()
    #     if not user:
    #         raise forms.ValidationError('Bạn không được đổi tên tài khoản!')

    #     return data

class ChangePasswordForm(forms.Form):
    old_password = forms.CharField()
    new_password = forms.CharField(label ='Mật khẩu Mới:',required=True, min_length=5, widget=forms.TextInput(attrs={ 'type':'password', 'class':"form-control form-control-lg", 
                                    'placeholder':"Mật khẩu Mới"}))
    confirm_password = forms.CharField(label='Xác nhận mật khẩu:',required=True, min_length=5, widget=forms.TextInput(attrs={ 'type':'password', 'class':"form-control form-control-lg", 
                                    'placeholder':"Xác nhận mật khẩu"}))

    def clean(self):
        data = super().clean()
        #check new password and confirm new password
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')
        if new_password != confirm_password:
            raise forms.ValidationError('Mật khẩu xác nhận không đúng!')