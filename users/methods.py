from email.mime.image import MIMEImage
import random, string
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

def random_string_generator(length):
    uppercase_string = string.ascii_uppercase
    lowercase_string = string.ascii_lowercase
    digit_string = string.digits

    return ''.join(random.choices(uppercase_string + lowercase_string + digit_string, k=length))

def send_email(template,subject,email,merge_data):
    html_content = render_to_string(template, merge_data)
    message = EmailMultiAlternatives(
        subject= subject,  
        to = [email],
    )
    message.attach_alternative(html_content,'text/html')
    message.send(fail_silently=False)

def send_email_img(template,subject,email,merge_data,img):
    html_content = render_to_string(template, merge_data)
    message = EmailMultiAlternatives(
        subject= subject,  
        to = [email],
    )
    if img:
        mime_image = MIMEImage(img)
        mime_image.add_header('Content-ID', '<image.png>')
        message.attach(mime_image)
    message.attach_alternative(html_content,'text/html')
    message.send(fail_silently=False)