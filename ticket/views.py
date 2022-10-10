from datetime import datetime, timedelta,timezone
import logging
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.db.models import Q,F,Sum
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models.functions import Coalesce
from django.urls import reverse
from ticket.methods import generate_qrcode, generate_ticket
from ticket.models import Participant, Workshop
from users.methods import send_email_img
from django.utils.translation import gettext as _

Logger = logging.getLogger("workshop_log")
# Create your views here.
def home(request):
    if request.user.is_authenticated:
        user = User.objects.get(username = request.user.username)
        workshops = Workshop.objects.filter(is_special= True,date__gte = datetime.now(timezone(timedelta(hours=+7))) - timedelta(days=1),slot__gt = Coalesce(Sum('participant__quantity'),0)).annotate(registered = Coalesce(Sum('participant__quantity', filter=Q(participant__user_id = request.user)),0),available = Coalesce(F('slot') - Sum('participant__quantity'),'slot'))
    else:
        return redirect('users:login')
    #if email is not verified
    if user.userextend.is_email_verified == False:
        return redirect('users:verify_email')

    if request.method == 'POST':
        id_inputs = request.POST.getlist('id')
        quantity_inputs = request.POST.getlist('quantity')
              
        if len(id_inputs) == 0:
            #user didnt choose workshop
            messages.warning(request,_('Xin vui lòng chọn workshop.'))
            return HttpResponseRedirect(reverse('ticket:home'))
        #get workshop id and ticket quantity
        result = []  
        quantity = 0
        total_ticket = 0
        for id,quantity_input in zip(id_inputs,quantity_inputs):
            dict = {}
            #if input number is not int, set quantity is 0
            try:
                quantity = int(quantity_input)
            except:
                quantity = 0
            if quantity > 0:
                #if workshop not exist refresh page
                workshop_exist = Workshop.objects.filter(id = id).annotate(available = Coalesce(F('slot') - Sum('participant__quantity'),'slot')).first()
                if not workshop_exist:
                    messages.warning(request,_('{workshop_name} không tồn tại, xin vui lòng chọn Workshop khác.').format(workshop_name = workshop_exist.name))
                    return render(request,'ticket/home.html',{'workshops':workshops})
                #if workshop out of slot                    
                if workshop_exist.available == 0:
                    messages.warning(request,_('{workshop_name} đã hết vé, xin vui lòng chọn Workshop khác.').format(workshop_name = workshop_exist.name))
                    return render(request,'ticket/home.html',{'workshops':workshops})
                #add id and quantity to a dict list    
                dict['id'] = id
                dict['quantity'] = quantity
                total_ticket = total_ticket + quantity
                result.append(dict)
                
        if len(result) == 0:
            messages.warning(request,_('Xin vui lòng nhập số vé để đăng ký.'))
            return HttpResponseRedirect(reverse('ticket:home'))

        #if total tickets excess current available user's ticket
        if user.userextend.special_ticket < total_ticket:
            messages.warning(request,_('Bạn không có đủ vé để đăng ký, xin vui lòng mua thêm vé.'))
            return HttpResponseRedirect(reverse('ticket:home'))

        #if workshops slot excess
        for item in result:        
            for workshop in workshops:               
                if str(workshop.id) == item.get('id'):
                    if workshop.available < item.get('quantity'):
                        messages.warning(request,_('Bạn chỉ có thể đăng ký {workshop_available} vé {workshop_name}').format(workshop_available=str(workshop.available),workshop_name=workshop.name))
                        return HttpResponseRedirect(reverse('ticket:home'))

        #register workshop     
        for item in result:
            for workshop in workshops:
                if str(workshop.id) == item.get('id'):
                    # Generate qrcode
                    qrcode = generate_qrcode()
                    participant = Participant(workshop_id = workshop,user_id = request.user,quantity = item.get('quantity'),qrcode = qrcode)                  
                    if workshop.is_special:
                        user.userextend.special_ticket = user.userextend.special_ticket - item.get('quantity')                     
                    else:
                        user.userextend.ticket = user.userextend.ticket - item.get('quantity')  

                    # Send Ticket to Email
                    fullname = user.last_name + ' ' + user.first_name
                    shortcode = fullname + ' ' + participant.workshop_id.name + ' ' + str(participant.quantity)
                    fullcode = fullname + '\n' + str(participant.workshop_id.id) + '\n' + participant.qrcode + '\n' + 'ĐHGT ' + str(datetime.utcnow().year)

                    # generate ticket
                    byte_ticket_img = generate_ticket(fullcode,shortcode,workshop.id,workshop.ticket_template)

                    #Send email function                   
                    subject =_('VÉ THAM DỰ ĐẠI HỘI GIỚI TRẺ {year} của {last_name} {first_name}').format(year=str(datetime.utcnow().year),last_name=user.last_name,first_name=user.first_name)
                    template = 'ticket/send_ticket_template.html'
                    merge_data = {
                        'fullname': user.last_name + ' ' + user.first_name,
                        'workshop': workshop.name,  
                        'date':workshop.date,
                        'address':workshop.address               
                    }
                    send_email_img(template,subject,user.email,merge_data,byte_ticket_img)

                    participant.save()
                    user.userextend.save()
                    # Logger
                    Logger.info(f'{request.user.username} registered {workshop.name} ticket. Quantity: {participant.quantity}')

        messages.success(request,_('Đăng ký vé thành công.'))
        return HttpResponseRedirect(reverse('ticket:home'))
    else:    
        return render(request, 'ticket/home.html', {'workshops' : workshops})

def guide(request):
    return render(request,'ticket/guide.html')

    