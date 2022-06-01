from datetime import datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.db.models import Count,Q
from django.contrib.auth.models import User
from django.urls import reverse
from ticket.models import Participant, Workshop


# Create your views here.
def home(request):
    if request.user.is_authenticated:
        workshops = Workshop.objects.filter(date__gte = datetime.now()).annotate(count = Count('participant'), bought = Count('participant', filter=Q(participant__user_id = request.user)))
    else:
        workshops = Workshop.objects.filter(date__gte = datetime.now() ).annotate(count = Count('participant'))
    context = {'workshops' : workshops}
    return render(request, 'ticket/home.html', context)

def ticket_detail(request,id):
    if request.user.is_authenticated:      
        workshop = Workshop.objects.filter(id = id).annotate(count = Count('participant'), bought = Count('participant', filter=Q(participant__user_id = request.user))).first()
        context = { 'workshop' : workshop}     
        return render(request, 'ticket/ticket_detail.html', context)
    else:
        return render(request, 'users/login.html')

def join_workshop(request):
    if not request.user.is_authenticated:
        return render(request, 'users/login.html',{'error_message':'Xin vui lòng đăng nhập.'})
    if request.method == 'POST':
        workshop_id = request.POST.get('workshop_id')
        quantity = request.POST.get('quantity')
        user = User.objects.filter(username = request.user.username).first()
        workshop = Workshop.objects.filter(id = workshop_id).annotate(count = Count('participant'), bought = Count('participant', filter=Q(participant__user_id = user))).first()

        #check if quantity is empty or less than 1
        if quantity == '' or int(quantity) <= 0:
            return render(request,'ticket/ticket_detail.html',{'workshop':workshop,'error_message':'Vui lòng nhập số lượng vé tham gia!'})

        #
        if user.userextend.ticket < int(quantity):
            return render(request,'ticket/ticket_detail.html',{'workshop':workshop,'error_message':'Bạn ko đủ vé. Xin vui lòng mua thêm vé để tham gia!'}) 

        #check if total ticket excess           
        total_ticket = workshop.count + int(quantity)
        if workshop.slot < total_ticket:
            avialable_slot = workshop.slot - workshop.count
            return render(request,'ticket/ticket_detail.html',{'workshop':workshop,'error_message':'Bạn chỉ có thể mua '+ str(avialable_slot) +' vé còn lại!'})
                
            
        for i in range(0,int(quantity),1):
            participant = Participant(workshop_id = workshop,user_id = request.user)
            participant.save()
        workshop.bought += int(quantity)
        user.userextend.ticket = user.userextend.ticket - int(quantity)
        user.userextend.save()
        return render(request,'ticket/ticket_detail.html',{'workshop':workshop,'error_message':'Mua vé thành công!'})