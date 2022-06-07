from datetime import datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.db.models import Count,Q,F
from django.contrib import messages
from django.contrib.auth.models import User

from django.urls import reverse
from ticket.models import Participant, Workshop

# Create your views here.
def home(request):  
    if request.user.is_authenticated:
        workshops = Workshop.objects.filter(date__gte = datetime.now()).annotate(registered = Count('participant', filter=Q(participant__user_id = request.user)),available = F('slot') - Count('participant'))
    else:
        workshops = Workshop.objects.filter(date__gte = datetime.now() ).annotate(available = F('slot') - Count('participant'))

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return render(request,'users/login/html',{'error_message':'Xin vui lòng đăng nhập.'})

        ids = request.POST.getlist('cinput')
        inputs_number = request.POST.getlist('ninput')
        user = User.objects.get(username = request.user.username)
        total_ticket = 0
        if len(ids) == 0:
            #user didnt choose workshop
            messages.warning(request,'Xin vui lòng chọn workshop.')
            return render(request,'ticket/home.html',{'workshops':workshops})
        #get workshop id and ticket quantity
        result = []  
        for id,input_number in zip(ids,inputs_number):
            dict = {}
            #if input number is not int, refresh page
            try:
                quantity = int(input_number)
                if quantity > 0:
                    #if workshop not exist refresh page
                    workshop_exist = Workshop.objects.filter(id = id).first()
                    if not workshop_exist:
                        return render(request,'ticket/home.html',{'workshops':workshops})
                    dict['id'] = id
                    dict['quantity'] = quantity
                    total_ticket = total_ticket + int(input_number)
                    result.append(dict)
                else:
                    messages.warning(request,'Xin vui lòng nhập số vé đăng ký.')
                    return render(request,'ticket/home.html',{'workshops':workshops})
            except:
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
                    for i in range(0,item.get('quantity'),1):                       
                        participant = Participant(workshop_id = workshop,user_id = request.user)
                        participant.save()
        user.userextend.ticket = user.userextend.ticket - total_ticket
        user.userextend.save()
        messages.success(request,'Đăng ký vé thành công.')
        return HttpResponseRedirect(request.path_info)
    else:    
        return render(request, 'ticket/home.html', {'workshops' : workshops})
    