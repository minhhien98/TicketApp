import io
import os
import sys
import django
from PIL import Image
from datetime import datetime, timedelta, timezone


# script upload all participants to spreadsheet
# use linux cron to run this script

if __name__ == '__main__':
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(BASE_DIR)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TicketApp.settings")
    django.setup()
    
    from django.contrib.auth.models  import User
    from django.conf import settings
    from users.methods import send_email, send_email_img

    users = User.objects.filter(userextend__is_email_verified = True)
    # get guide img as bytes
    img = Image.open('static/users/images/huong_dan_chon_ws.png')
    back_im = img.copy()
    buffer = io.BytesIO()
    back_im.save(buffer, format='PNG', quality=100)
    bytes_img = buffer.getvalue()

    #Send mail to notify email
    subject = '[ĐHGT TGP Sài Gòn 2022] Thư Nhắc Nhở'
    template ='users/notify_email_near_event_template.html'
    home_link = settings.DOMAIN_NAME
    from_email ='GioiTreSaiGon Admin'
    emails_exist= []
    count = 0
    for user in users:
        if user.email not in emails_exist:
            to_emails=[]
            emails_exist.append(user.email)
            to_emails.append(user.email)
            merge_data = {
                'fullname':user.last_name + ' ' + user.first_name,
                'home_link':home_link,
            }
            send_email_img(template,subject,to_emails,merge_data,bytes_img)
            count +=1
    print('mail sent: ',count)