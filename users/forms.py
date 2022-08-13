from django import forms
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

class RegisterForm(forms.Form):
    username = forms.CharField(label=_('Tài khoản:'), required=True,min_length=5, max_length=20, widget=forms.TextInput(attrs={ 'class':'form-control form-control-lg', 
                                    'placeholder':_('Tài khoản')}))
    password = forms.CharField(label=_('Mật khẩu:'), required=True, min_length=5, widget=forms.TextInput(attrs={ 'type':'password', 'class':'form-control form-control-lg', 
                                    'placeholder':_('Mật khẩu')}))
    confirm_password = forms.CharField(label=_('Xác nhận mật khẩu:'),required=True, widget=forms.TextInput(attrs={ 'type':'password','class':'form-control form-control-lg', 
                                    'placeholder':_('Xác nhận mật khẩu')}))        
    last_name = forms.CharField(label=_('Họ:'), required=True,widget=forms.TextInput(attrs={ 'class':'form-control form-control-lg', 
                                    'placeholder':_('Họ')}))
    first_name = forms.CharField(label=_('Tên:'),required=True, widget=forms.TextInput(attrs={ 'class':'form-control form-control-lg', 
                                    'placeholder':_('Tên')}))                                
    email = forms.EmailField(label='Email:',required=True, widget=forms.TextInput(attrs={ 'class':'form-control form-control-lg', 
                                    'placeholder':'Email'}))
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message=_('Xin vui lòng nhập đúng số điện thoại!'))
    phone_number = forms.CharField(label=_('Số điện thoại:'),min_length=9,max_length=15,widget=forms.TextInput(attrs={ 'class':'form-control form-control-lg','placeholder':_('Số điện thoại')}),validators= [phone_regex])
    birthdate = forms.DateField(label =_('Ngày sinh:'),required= True, widget=forms.TextInput(attrs={'class': 'form-control', 'type':'date'}))
    address = forms.CharField(label=_('Địa chỉ:'),widget = forms.TextInput(attrs={'placeholder':_('Địa chỉ')}))
    parish = forms.CharField(label=_('Giáo xứ:'),max_length= 100, widget=forms.TextInput(attrs={'placeholder':_('Giáo xứ')}))


    def clean(self):
        data = super().clean()
        #check username exist
        username = data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(_('Tên tài khoản {username} đã tồn tại.').format(username=username))
        #check password and confirm password
        if data.get('password') != data.get('confirm_password'):
            raise forms.ValidationError(_('Mật khẩu xác nhận ko trùng khớp!'))
        return data

class UserProfileForm(forms.Form):       
    last_name = forms.CharField(label =_('Họ:'),required=True,widget=forms.TextInput(attrs={ 'class':'form-control form-control-lg', 
                                    'placeholder':_('Họ')}))
    first_name = forms.CharField(label =_('Tên:'),required=True, widget=forms.TextInput(attrs={ 'class':'form-control form-control-lg', 
                                    'placeholder':_('Tên')}))
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message=_('Xin vui lòng nhập đúng số điện thoại!'))
    phone_number = forms.CharField(label =_('Số điện thoại:'),min_length=9,max_length=15,widget=forms.TextInput(attrs={ 'class':'form-control form-control-lg','placeholder':_('Số điện thoại')}),validators= [phone_regex])
    birthdate = forms.DateField(label =_('Ngày sinh:'),required= True, widget=forms.TextInput(attrs={'class': 'form-control', 'type':'date'}))
    address = forms.CharField(label =_('Địa chỉ:'),widget = forms.TextInput(attrs={'placeholder':_('Địa chỉ')}))
    parish = forms.CharField(label =_('Giáo xứ:'),max_length= 100, widget=forms.TextInput(attrs={'placeholder':_('Giáo xứ')}))

class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(label =_('Mật khẩu cũ:'),required=True, min_length=5, widget=forms.TextInput(attrs={ 'type':'password', 'class':'form-control form-control-lg', 
                                    'placeholder':_('Mật khẩu cũ')}))
    new_password = forms.CharField(label =_('Mật khẩu mới:'),required=True, min_length=5, widget=forms.TextInput(attrs={ 'type':'password', 'class':'form-control form-control-lg', 
                                    'placeholder':_('Mật khẩu mới')}))
    confirm_password = forms.CharField(label=_('Xác nhận mật khẩu:'),required=True, min_length=5, widget=forms.TextInput(attrs={ 'type':'password', 'class':'form-control form-control-lg', 
                                    'placeholder':_('Xác nhận mật khẩu')}))

    def clean(self):
        data = super().clean()
        #check new password and confirm new password
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')
        if old_password == new_password:
            raise forms.ValidationError(_('Xin vui lòng không dùng mật khẩu cũ!'))
        if new_password != confirm_password:
            raise forms.ValidationError(_('Mật khẩu xác nhận ko trùng khớp!'))
        return data

class VerifyEmailForm(forms.Form):
    email = forms.EmailField(label = 'Email:',required=True,error_messages={'required':_('Xin vui lòng nhập email.'),'invalid':_('Xin vui lòng nhập đúng email của bạn.')})
    confirm_email = forms.EmailField(label=_('Xác nhận Email:'),required=True,error_messages={'required':_('Xin vui lòng nhập email.'),'invalid':_('Xin vui lòng nhập đúng email của bạn.')})

    def clean(self):
        data = super().clean()
        email = data.get('email')
        confirm_email = data.get('confirm_email')
        #check email and confirm email
        if str(email) != str(confirm_email):
            raise forms.ValidationError(_('Email không trùng khớp.'))
        return data