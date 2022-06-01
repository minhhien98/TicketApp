from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models  import User
from django.urls import reverse
from users.forms import RegisterForm, UserProfileForm
from users.models import UserExtend

# Create your views here.

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User(username = form.cleaned_data.get('username'), first_name = form.cleaned_data.get('first_name'), last_name = form.cleaned_data.get('last_name'), email = form.cleaned_data.get('email'))
            user.set_password(str(form.cleaned_data.get('password')))            
            user.save()
            userextend =UserExtend(user_id = user,phone_number = form.cleaned_data.get('phone_number'),birth_date = form.cleaned_data.get('birth_date'), address= form.cleaned_data.get('address'), parish = form.cleaned_data.get('parish'))
            userextend.save()
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
            user.email = form.cleaned_data.get('email')
            user.userextend.phone_number = form.cleaned_data.get('phone_number')
            user.userextend.birth_date = form.cleaned_data.get('birth_date')
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
                                'birth_date':user.userextend.birth_date,
                                'address':user.userextend.address,
                                'parish':user.userextend.parish})

        return render(request,'users/user_profile.html',{'form':form})

def login(request):
    if request.user.is_authenticated:
        return redirect('ticket:home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username = username, password = password)
        if user is not None:
            auth_login(request, user)
            return HttpResponseRedirect(reverse('ticket:home'))
        else:
            return render(request,'users/login.html',{'error_message':'Invalid username/password!'})
    else:
        return render(request,'users/login.html')

def logout(request):
	if request.method == 'POST':
		user = User.objects.get(username = request.user.username)
		auth_logout(request)		
		return redirect('users:login')
