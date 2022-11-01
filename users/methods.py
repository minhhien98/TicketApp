from email.mime.image import MIMEImage
import random, string
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import gspread
from django.conf import settings


def random_string_generator(length):
    uppercase_string = string.ascii_uppercase
    lowercase_string = string.ascii_lowercase
    digit_string = string.digits

    return ''.join(random.choices(uppercase_string + lowercase_string + digit_string, k=length))

def send_email(template,subject,to_emails,merge_data,connection=None,bcc=None):
    html_content = render_to_string(template, merge_data)
    message = EmailMultiAlternatives(
        subject= subject,  
        to = to_emails,
        connection=connection,
        bcc=bcc,
    )
    message.attach_alternative(html_content,'text/html')
    message.send(fail_silently=False)

def send_email_img(template,subject,to_emails,merge_data,img,connection=None,bcc=None):
    html_content = render_to_string(template, merge_data)
    print(to_emails)
    message = EmailMultiAlternatives(
        subject= subject,  
        to = to_emails,
        connection=connection,
        bcc=bcc,
    )
    if img:
        mime_image = MIMEImage(img)
        mime_image.add_header('Content-ID', '<image.png>')
        message.attach(mime_image)
    message.attach_alternative(html_content,'text/html')
    message.send(fail_silently=False)

# Google API
# scope = [
#         'https://www.googleapis.com/auth/drive',
#         'https://www.googleapis.com/auth/drive.file'
#         ]
# def add_participant_to_google_sheet(user_info): 
#     # Connect to google service account 
#     gc = gspread.service_account_from_dict(settings.GOOGLE_JSON_KEY,scopes=scope)
#     # Get Spreadsheet
#     sheet = gc.open_by_key(settings.SPREADSHEET_ID)
#     participant_worksheet = sheet.worksheet('Participant')
#     #get last row
#     last_row = len(participant_worksheet.get_all_values())
#     #get field name
#     field_list = participant_worksheet.row_values(1)
#     col = 1
#     # Check if participant exist in spread, update exist participant and return
#     qr_exist = participant_worksheet.find(in_column=6,query=user_info.get('QRCode'))
#     if qr_exist is not None:
#         for field in field_list:       
#             participant_worksheet.update_cell(qr_exist.row,col,str(user_info.get(field)))
#             col +=1
#         return
#     # Add new Participant to google sheet
#     for field in field_list:       
#         participant_worksheet.update_cell(last_row + 1,col,str(user_info.get(field)))
#        col +=1

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip