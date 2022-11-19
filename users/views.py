from datetime import datetime, timedelta, timezone
from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models  import User
from django.core.mail import get_connection
from django.urls import reverse
from users.forms import ChangePasswordForm, RegisterForm, ForgotPasswordForm, ResetPasswordForm, UserProfileForm, VerifyEmailForm
from users.methods import get_client_ip, random_string_generator, send_email
from users.models import UserExtend
from django.utils.translation import gettext as _
from django.conf import settings

import logging
Logger = logging.getLogger("login_log")
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
                                   key_expires = datetime.now() + timedelta(days=1))
            user.save()
            userextend.save()
            #Send mail to verify email function
            connection = get_connection(host=settings.GMAIL_HOST,port=settings.GMAIL_PORT,username=settings.GMAIL_HOST_USER, password=settings.GMAIL_HOST_PASSWORD,use_tls=settings.GMAIL_USE_TLS)
            subject =_('Xác nhận email!')
            template ='users/verify_email_template.html'
            verify_link = request.scheme + '://' + request.get_host() +'/u/confirm-email/' + user.userextend.activation_key
            home_link = settings.DOMAIN_NAME
            from_email ='GioiTreSaiGon Admin'
            to_emails=[]
            to_emails.append(user.email)
            bcc =[]
            bcc.append('dhgttgpsaigon@gmail.com')
            merge_data = {
                'fullname':user.last_name + ' ' + user.first_name,
                'verify_link':verify_link,
                'home_link':home_link,
            }
            send_email(template,subject,to_emails,merge_data,connection,from_email=from_email,bcc=bcc)
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
        messages.warning(request,_('Xin vui lòng đăng nhập.'))
        return render(request,'users/login.html')
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
            messages.success(request,_('Đã Lưu'))
            return render(request,'users/user_profile.html',{'form':form})
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
        messages.warning(request,_('Xin vui lòng đăng nhập.'))
        return render(request,'users/login.html')
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            old_password = form.cleaned_data.get('old_password')
            user = User.objects.filter(username = request.user.username).first()
            if not user.check_password(old_password):
                messages.warning(request,_('Mật khẩu cũ không chính xác.'))
                return render(request,'users/change_password.html',{'form':form})
            new_password = form.cleaned_data.get('new_password')
            user.set_password(new_password)
            user.save()
            messages.success(request,_('Thay đổi mật khẩu thành công.'))
            return render(request,'users/change_password.html',{'form':form})
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
        client_ip = get_client_ip(request)
        user = authenticate(request, username = username, password = password)
        if user is not None:
            auth_login(request, user)         
            Logger.info(f'{client_ip} pass {username}')
            #if user's email is not verified
            if not user.userextend.is_email_verified:
                messages.warning(request,_('Tài khoản chưa xác nhận email. Bạn vui lòng xác nhận email để đăng nhập.'))
                return redirect('users:verify_email')
            return HttpResponseRedirect(reverse('ticket:home'))
        else:
            Logger.warning(f'{client_ip} fail {username}')
            messages.warning(request,_('Tài khoản/Mật khẩu không chính xác!'))
            return render(request,'users/login.html')
    else:
        messages.warning(request,'Hiện chúng tôi đã đóng link đăng ký. Nếu bạn chưa chọn vé workshop, bạn vẫn có thể đăng nhập để chọn vé.')
        return render(request,'users/login.html')

def logout(request):
	if request.method == 'POST':
		auth_logout(request)		
		return redirect('users:login')

#verify email for user try to log in
def verify_email(request):
    if not request.user.is_authenticated:
        messages.warning(request,_('Xin vui lòng đăng nhập.'))
        return render(request,'users/login.html')
        
    user = User.objects.get(username = request.user.username)
    #if user's email already verified
    if user.userextend.is_email_verified:
        return redirect('ticket:home')

    if request.method == 'POST':
        form = VerifyEmailForm(request.POST)
        if form.is_valid():
            # Check if mail is sent recently (1 minute)
            if user.userextend.key_expires is not None:
                minutes_ago = datetime.now(timezone(timedelta(hours=+0))) - timedelta(minutes=1)
                key_created_date = user.userextend.key_expires - timedelta(days=1)
                if minutes_ago < key_created_date:
                    messages.warning(request,_('Mail vừa được gửi mới đây, xin vui lòng chờ.'))
                    return render(request,'users/verify_email.html',{'form':form})  
            email = form.cleaned_data.get('email') 
            user.email = email
            user.userextend.activation_key = random_string_generator(length=15)
            user.userextend.key_expires = datetime.now() + timedelta(days=1)            
            user.save()
            user.userextend.save()

            #Send mail to verify email function
            connection = get_connection(host=settings.GMAIL_HOST,port=settings.GMAIL_PORT,username=settings.GMAIL_HOST_USER, password=settings.GMAIL_HOST_PASSWORD,use_tls=settings.GMAIL_USE_TLS)
            subject =_('Xác nhận email!')
            template ='users/verify_email_template.html'
            verify_link = request.scheme + '://' + request.get_host() +'/u/confirm-email/' + user.userextend.activation_key
            home_link = settings.DOMAIN_NAME
            from_email ='GioiTreSaiGon Admin'
            to_emails=[]
            to_emails.append(user.email)
            bcc =[]
            bcc.append('dhgttgpsaigon@gmail.com')
            merge_data = {
                'fullname':user.last_name + ' ' + user.first_name,
                'verify_link':verify_link,
                'home_link':home_link,
            }
            send_email(template,subject,to_emails,merge_data,connection,from_email=from_email,bcc=bcc)
            messages.success(request,_('Đã gửi mail xác nhận. Xin vui lòng kiểm tra email.'))
            return HttpResponseRedirect(reverse('users:verify_email'))
        else:
            return render(request,'users/verify_email.html',{'form':form})       
    else:
        form = VerifyEmailForm()
        return render(request,'users/verify_email.html',{'form':form})

#verify email
def confirm_email(request,key):
    user_extend = get_object_or_404(UserExtend, activation_key = key, is_email_verified= False)
    #if activation key expires, request user to login for verify email
    if user_extend.key_expires.replace(tzinfo=None) < datetime.utcnow():
        return HttpResponseNotFound()
    user_extend.is_email_verified = True
    user_extend.activation_key = ''
    user_extend.save()

    #force logout if login in another account
    if request.user.is_authenticated:
        auth_logout(request)  

    #Send email function
    link_home = settings.DOMAIN_NAME
    subject =_('Hướng dẫn chuyển khoản mua vé.')
    template ='users/how_to_buy_ticket_template.html'
    to_emails=[]
    to_emails.append(user_extend.user_id.email)
    merge_data = {
         'fullname':user_extend.user_id.last_name + ' ' + user_extend.user_id.first_name,
         'link_home': link_home,
         'username': user_extend.user_id.username
    }  
    send_email(template, subject,to_emails , merge_data)
    messages.success(request,_('Xác nhận email thành công, bạn có thể kiểm tra email hoặc đăng nhập xem hướng dẫn mua vé.'))
    return redirect('users:login')

def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username') 
            user = User.objects.filter(username = username).first()
            # Check if mail is sent recently (1 minute)
            if user.userextend.key_expires is not None:
                minutes_ago = datetime.now(timezone(timedelta(hours=+0))) - timedelta(minutes=1)
                key_created_date = user.userextend.key_expires - timedelta(days=1)
                if minutes_ago < key_created_date:
                    messages.warning(request,_('Mail vừa được gửi mới đây, xin vui lòng chờ.'))
                    return render(request,'users/forgot_password.html',{'form':form}) 
            user.userextend.activation_key = random_string_generator(length=15)
            user.userextend.key_expires = datetime.now() + timedelta(days=1)            
            user.userextend.save()
            # send mail reset password
            subject =_('Xác nhận đổi mật khẩu')
            template ='users/forgot_password_template.html'
            verify_link = request.scheme + '://' + request.get_host() +'/u/reset-password/' + user.userextend.activation_key
            home_link = settings.DOMAIN_NAME
            to_emails=[]
            to_emails.append(user.email)
            merge_data = {
                'fullname':user.last_name + ' ' + user.first_name,
                'verify_link':verify_link,
                'home_link':home_link,
            }
            send_email(template,subject,to_emails,merge_data)
            messages.success(request,_('Bạn vui lòng kiểm tra email để đặt lại mật khẩu.'))
            return HttpResponseRedirect(reverse('users:forgot_password'))
        else:
            return render(request,'users/forgot_password.html',{'form':form})
    else:
        form = ForgotPasswordForm()
        return render(request,'users/forgot_password.html',{'form':form})

def reset_password(request,key):
    user_extend = get_object_or_404(UserExtend, activation_key = key)
    # if key is out of date (1 day)
    if user_extend.key_expires.replace(tzinfo=None) < datetime.utcnow():
        return HttpResponseNotFound()
    # force logout
    if request.user.is_authenticated:
        auth_logout(request)
    
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data.get('new_password')
            user_extend.user_id.set_password(new_password)
            user_extend.activation_key = ''
            user_extend.user_id.save()
            messages.success(request,'Mật khẩu đã được thay đổi, bạn có thể đăng nhập ngay.')
            return redirect('users:login')
        else:
            return render(request,'users/reset_password.html',{'form':form})
    else:
        form = ResetPasswordForm()
        return render(request,'users/reset_password.html',{'form':form})