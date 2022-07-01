from datetime import datetime, timedelta,timezone
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.db.models import Q,F,Sum
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models.functions import Coalesce

from django.urls import reverse
from ticket.models import Participant, Workshop

# Create your views here.
def home(request):
    if request.user.is_authenticated:
        user = User.objects.get(username = request.user.username)
        workshops = Workshop.objects.filter(date__gte = datetime.now(timezone(timedelta(hours=+7))) - timedelta(days=1),slot__gt = Coalesce(Sum('participant__quantity'),0)).annotate(registered = Coalesce(Sum('participant__quantity', filter=Q(participant__user_id = request.user)),0),available = Coalesce(F('slot') - Sum('participant__quantity'),'slot'))
    else:
        return redirect('users:login')
    #if email is not verified
    if user.userextend.is_email_verified == False:
        return redirect('users:verify_email')

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return render(request,'users/login/html',{'error_message':'Xin vui lòng đăng nhập.'})

        id_inputs = request.POST.getlist('id')
        quantity_inputs = request.POST.getlist('quantity')
              
        if len(id_inputs) == 0:
            #user didnt choose workshop
            messages.warning(request,'Xin vui lòng chọn workshop.')
            return render(request,'ticket/home.html',{'workshops':workshops})
        #get workshop id and ticket quantity
        result = []  
        total_ticket = 0
        for id,input_number in zip(id_inputs,quantity_inputs):
            dict = {}
            #if input number is not int, refresh page
            try:
                quantity = int(input_number)
                if quantity > 0:
                    #if workshop not exist refresh page
                    workshop_exist = Workshop.objects.filter(id = id).annotate(available = Coalesce(F('slot') - Sum('participant__quantity'),'slot')).first()
                    if not workshop_exist:
                        return render(request,'ticket/home.html',{'workshops':workshops})
                    #if workshop out of slot                    
                    if workshop_exist.available == 0:
                        messages.warning(request,workshop_exist.name + ' đã hết vé, xin vui lòng chọn Workshop khác!')
                        return render(request,'ticket/home.html',{'workshops':workshops})
                    dict['id'] = id
                    dict['quantity'] = quantity
                    total_ticket = total_ticket + quantity
                    result.append(dict)
            except:
                return render(request,'ticket/home.html',{'workshops':workshops})
        if len(result) == 0:
            messages.warning(request,'Xin vui lòng nhập số vé đăng ký.')
            return render(request,'ticket/home.html',{'workshops':workshops})

        #if total tickets excess current available user's ticket
        if user.userextend.ticket < total_ticket:
            messages.warning(request,'Bạn không có đủ vé để đăng ký, xin vui lòng mua thêm vé.')
            return render(request,'ticket/home.html',{'workshops':workshops})

        #if workshops slot excess
        for item in result:        
            for workshop in workshops:               
                if str(workshop.id) == item.get('id'):
                    if workshop.available < item.get('quantity'):
                        messages.warning(request,'Bạn chỉ có thể đăng ký '+ str(workshop.available) + ' vé '+ workshop.name)
                        return render(request,'ticket/home.html',{'workshops':workshops})

        #register workshop     
        for item in result:
            for workshop in workshops:
                 if str(workshop.id) == item.get('id'):
                    participant = Participant(workshop_id = workshop,user_id = request.user,quantity = item.get('quantity'))
                    participant.save()
        user.userextend.ticket = user.userextend.ticket - total_ticket
        user.userextend.save()
        messages.success(request,'Đăng ký vé thành công.')
        return HttpResponseRedirect(request.path_info)
    else:    
        return render(request, 'ticket/home.html', {'workshops' : workshops})


    