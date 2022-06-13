import random, string
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

def random_string_generator(length):
    uppercase_string = string.ascii_uppercase
    lowercase_string = string.ascii_lowercase
    digit_string = string.digits

    return ''.join(random.choices(uppercase_string + lowercase_string + digit_string, k=length))

def send_email(subject,email,merge_data):
    html_content = render_to_string('users/email_template.html', merge_data)
    message = EmailMultiAlternatives(
        subject= subject,  
        to = [email],
    )
    message.attach_alternative(html_content,'text/html')
    message.send(fail_silently=False)