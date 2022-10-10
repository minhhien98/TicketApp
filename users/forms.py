from django import forms
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.conf import settings

class RegisterForm(forms.Form):
    username = forms.CharField(label=_('Tài khoản:'), required=True,min_length=5, max_length=20, widget=forms.TextInput(attrs={'placeholder':_('Tài khoản')}),error_messages={'required':_('Xin hãy nhập tên tài khoản.'),'min_length':_('Tên tài khoản phải có ít nhất 5 ký tự.'),'max_length':_('Tên tài khoản chỉ dc tối đa 20 kí tự.')})
    password = forms.CharField(label=_('Mật khẩu:'), required=True, min_length=5, widget=forms.TextInput(attrs={ 'type':'password','placeholder':_('Mật khẩu')}),error_messages={'required':_('Xin hãy nhập mật khẩu.'),'min_length':_('Mật khẩu phải có ít nhất 5 kí tự.')})
    confirm_password = forms.CharField(label=_('Xác nhận mật khẩu:'),required=True, widget=forms.TextInput(attrs={ 'type':'password','placeholder':_('Xác nhận mật khẩu')}),error_messages={'required':_('Xin hãy nhập mật khẩu.')})        
    last_name = forms.CharField(label=_('Họ:'), required=True,widget=forms.TextInput(attrs={'placeholder':_('Họ')}), error_messages={'required':_('Xin hãy nhập họ của bạn.')})
    first_name = forms.CharField(label=_('Tên:'),required=True, widget=forms.TextInput(attrs={'placeholder':_('Tên')}), error_messages={'required':_('Xin hãy nhập tên của bạn.')})                                
    email = forms.EmailField(label='Email:',required=True, widget=forms.TextInput(attrs={'placeholder':'Email'}),error_messages={'required':_('Xin hãy nhập email.'),'invalid':_('Xin hãy nhập email hợp lệ.')})
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message=_('Xin hãy nhập số điện thoại hợp lệ.'))
    phone_number = forms.CharField(label=_('Số điện thoại:'),min_length=9,max_length=15,widget=forms.TextInput(attrs={'placeholder':_('Số điện thoại')}),validators= [phone_regex])
    birthdate = forms.DateField(label =_('Ngày sinh:'),required= True, widget=forms.TextInput(attrs={'type':'date'}),input_formats=settings.DATE_INPUT_FORMATS,error_messages={'required':_('Xin hãy nhập ngày sinh.')})
    address = forms.CharField(label=_('Địa chỉ:'),widget = forms.TextInput(attrs={'placeholder':_('Địa chỉ')}))
    parish = forms.CharField(label=_('Giáo xứ:'),max_length= 100, widget=forms.TextInput(attrs={'placeholder':_('Giáo xứ')}))


    def clean(self):
        data = super().clean()
        #check username exist
        username = data.get('username')
        if User.objects.filter(username=username).exists():
            self.add_error('username',_('Tên tài khoản {username} đã tồn tại.').format(username=username))
        #check password and confirm password
        if data.get('password') != data.get('confirm_password'):
            self.add_error('confirm_password',_('Mật khẩu xác nhận ko trùng khớp.'))
        return data

class UserProfileForm(forms.Form):       
    last_name = forms.CharField(label=_('Họ:'), required=True,widget=forms.TextInput(attrs={'placeholder':_('Họ')}), error_messages={'required':_('Xin hãy nhập họ của bạn.')})
    first_name = forms.CharField(label=_('Tên:'),required=True, widget=forms.TextInput(attrs={'placeholder':_('Tên')}), error_messages={'required':_('Xin hãy nhập tên của bạn.')})                       
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message=_('Xin hãy nhập số điện thoại hợp lệ.'))
    phone_number = forms.CharField(label=_('Số điện thoại:'),min_length=9,max_length=15,widget=forms.TextInput(attrs={'placeholder':_('Số điện thoại')}),validators= [phone_regex])
    birthdate = forms.DateField(label =_('Ngày sinh:'),required= True, widget=forms.TextInput(attrs={'type':'date'}),input_formats=settings.DATE_INPUT_FORMATS,error_messages={'required':_('Xin hãy nhập ngày sinh.')})
    address = forms.CharField(label =_('Địa chỉ:'),widget = forms.TextInput(attrs={'placeholder':_('Địa chỉ')}))
    parish = forms.CharField(label =_('Giáo xứ:'),max_length= 100, widget=forms.TextInput(attrs={'placeholder':_('Giáo xứ')}))

class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(label =_('Mật khẩu cũ:'), widget=forms.TextInput(attrs={'placeholder':_('Mật khẩu cũ')}))
    new_password = forms.CharField(label =_('Mật khẩu mới:'),required=True, min_length=5, widget=forms.TextInput(attrs={ 'type':'password','placeholder':_('Mật khẩu mới')}),error_messages={'required':_('Xin hãy nhập mật khẩu.'),'min_length':_('Mật khẩu phải có ít nhất 5 kí tự.')})
    confirm_password = forms.CharField(label=_('Xác nhận mật khẩu:'), widget=forms.TextInput(attrs={ 'type':'password','placeholder':_('Xác nhận mật khẩu')}))

    def clean(self):
        data = super().clean()
        #check new password and confirm new password
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')
        if new_password != confirm_password:
            raise forms.ValidationError(_('Mật khẩu xác nhận ko trùng khớp.'))
        return data

class VerifyEmailForm(forms.Form):
    email = forms.EmailField(label = 'Email:',required=True,error_messages={'required':_('Xin hãy nhập email.'),'invalid':_('Xin hãy nhập email hợp lệ.')})
    confirm_email = forms.EmailField(label=_('Xác nhận Email:'),required=True,error_messages={'required':_('Xin hãy nhập email.'),'invalid':_('Xin hãy nhập email hợp lệ.')})

    def clean(self):
        data = super().clean()
        email = data.get('email')
        confirm_email = data.get('confirm_email')
        #check email and confirm email
        if str(email) != str(confirm_email):
            raise forms.ValidationError(_('Email không trùng khớp.'))
        return data