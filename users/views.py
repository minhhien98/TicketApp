from datetime import datetime, timedelta
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models  import User
from django.urls import reverse
from users.forms import ChangePasswordForm, RegisterForm, UserProfileForm, VerifyEmailForm
from users.methods import random_string_generator, send_email
from users.models import UserExtend
from django.utils.translation import gettext as _

# Create your views here.

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User(username = form.cleaned_data.get('username'), first_name = form.cleaned_data.get('first_name'), last_name = form.cleaned_data.get('last_name'), email = form.cleaned_data.get('email'))
            user.set_password(str(form.cleaned_data.get('password')))            
            
            userextend =UserExtend(user_id = user,phone_number = form.cleaned_data.get('phone_number'),
                                   birthdate = form.cleaned_data.get('birthdate'),
                                   address= form.cleaned_data.get('address'), parish = form.cleaned_data.get('parish'),
                                   activation_key = random_string_generator(length=15),
                                   key_expires = datetime.now() + timedelta(minutes=30))
            user.save()
            userextend.save()
            #Send email function
            subject =_('Xác nhận email!')
            template ='users/email_template.html'
            title =_('Xác nhận email!')
            content = _('Link xác nhận email( Thời hạn 1 ngày):')
            link = request.scheme + '://' + request.get_host() +'/u/confirm-email/' + user.userextend.activation_key
            merge_data = {
                'tittle':title,
                'content':content,
                'link':link,
                'key': user.userextend.activation_key,
                'username': user.username,
            }
            send_email(template,subject,user.email,merge_data)
            return HttpResponseRedirect(reverse('users:register_success'))
        else:
            return render(request,'users/register.html',{'form':form})
    else:
        form = RegisterForm()
        return render(request,'users/register.html',{'form':form})

def register_success(request):
    return render(request,'users/register_success.html')

def user_profile(request):
    if not request.user.is_authenticated:
        return render(request,'users/login.html',{'error_message':'Xin vui lòng đăng nhập.'})
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            user = User.objects.get(username = request.user.username)
            user.last_name = form.cleaned_data.get('last_name')
            user.first_name = form.cleaned_data.get('first_name')
            user.userextend.phone_number = form.cleaned_data.get('phone_number')
            user.userextend.birthdate = form.cleaned_data.get('birthdate')
            user.userextend.address = form.cleaned_data.get('address')
            user.userextend.parish = form.cleaned_data.get('parish')
            user.save()
            user.userextend.save()
            return render(request,'users/user_profile.html',{'form':form, 'error_message':'Lưu Thành công.'})
        else:
            return render(request,'users/user_profile.html',{'form':form})
    else:
        user = User.objects.get(username = request.user.username)
        form = UserProfileForm({'username' : user.username,
                                'first_name':user.first_name,
                                'last_name':user.last_name,
                                'email':user.email,
                                'phone_number':user.userextend.phone_number,
                                'birthdate':user.userextend.birthdate,
                                'address':user.userextend.address,
                                'parish':user.userextend.parish})
        return render(request,'users/user_profile.html',{'form':form})

def change_password(request):
    if not request.user.is_authenticated:
        return render(request,'users/login.html',{'error_message':_('Xin vui lòng đăng nhập.')})
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            old_password = form.cleaned_data.get('old_password')
            user = User.objects.filter(username = request.user.username).first()
            if not user.check_password(old_password):
                return render(request,'users/change_password.html',{'form':form,'error_message':_('Mật khẩu cũ không chính xác.')})
            new_password = form.cleaned_data.get('new_password')
            user.set_password(new_password)
            user.save()
            return render(request,'users/change_password.html',{'form':form,'error_message':_('Thay đổi mật khẩu thành công.')})
        else:
            return render(request,'users/change_password.html',{'form':form})
    else:
        form = ChangePasswordForm()
        return render(request,'users/change_password.html',{'form':form})

def login(request):
    if request.user.is_authenticated:
        return redirect('ticket:home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username = username, password = password)
        if user is not None:
            auth_login(request, user)
            #if user's email is not verified
            if not user.userextend.is_email_verified:
                return redirect('users:verify_email')

            return HttpResponseRedirect(reverse('ticket:home'))
        else:
            return render(request,'users/login.html',{'error_message':'Invalid username/password!'})
    else:
        return render(request,'users/login.html')

def logout(request):
	if request.method == 'POST':
		auth_logout(request)		
		return redirect('users:login')

#verify email for user try to log in
def verify_email(request):
    if not request.user.is_authenticated:
        return render(request,'users/login.html',{'error_message':_('Xin vui lòng đăng nhập.')})
        
    user = User.objects.get(username = request.user.username)
    #if user's email already verified
    if user.userextend.is_email_verified:
        return redirect('ticket:home')

    if request.method == 'POST':
        form = VerifyEmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email') 
            user.email = email
            user.userextend.activation_key = random_string_generator(length=15)
            user.userextend.key_expires = datetime.now()  + timedelta(days=1)            
            user.save()
            user.userextend.save()

            #Send email function
            subject =_('Xác nhận email!')
            template ='users/email_template.html'
            title =_('Xác nhận email!')
            content = _('Link xác nhận email( Thời hạn 1 ngày):')
            link = request.scheme + '://' + request.get_host() +'/u/confirm-email/' + user.userextend.activation_key
            merge_data = {
                'title':title,
                'content':content,
                'link':link,
                'key': user.userextend.activation_key,
                'username': user.username,
            }
            send_email(template,subject,user.email,merge_data)
            messages.success(request,_('Đã gửi mail xác nhận. Xin vui lòng kiểm tra email.'))
            return HttpResponseRedirect(reverse('users:verify_email'))
        else:
            return render(request,'users/verify_email.html',{'form':form})       
    else:
        form = VerifyEmailForm()
        return render(request,'users/verify_email.html',{'form':form})

#verify email
def confirm_email(request,key):
    user_extend = get_object_or_404(UserExtend, activation_key = key)
    #if activation key expires, request user to login for verify email
    if user_extend.key_expires.replace(tzinfo=None) < datetime.utcnow():
        messages.warning(request,_('Link đã hết hạn, xin vui lòng đăng nhập để xác nhận lại email.'))
        return render(request,'users/confirm_email.html')
    user_extend.is_email_verified = True
    user_extend.save()
    #Send email function
    subject =_('Hướng dẫn chuyển khoản mua vé.')
    template ='users/email_template.html'
    title =_('Hướng dẫn chuyển khoản mua vé.')
    content = _('Hướng dẫn chuyển khoản mua vé.')
    merge_data = {
        'title':title,
        'content':content,
        'username': user_extend.user_id.username,
    }  
    send_email(template, subject, user_extend.user_id.email, merge_data)
    #Xác nhận thành công
    messages.success(request,_('Xác nhận Email Thành công.'))
    return render(request,'users/confirm_email.html')