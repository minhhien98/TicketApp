import logging
from re import L, T
from django.contrib.auth.models  import User
from django.utils import translation
from django.conf import settings

Logger = logging.getLogger('request_log')

class RequestLoggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)    
        client_ip = get_client_ip(request)
        server_protocol = request.META.get('SERVER_PROTOCOL')
        Logger.info(f'{request.method} {request.build_absolute_uri()} {server_protocol} {response.status_code} {client_ip} {request.user.username}')
        return response

class UserLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)   
        #current_language = request.COOKIES.get('language')
        translation.activate('vi')
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME,'vi')
        # if languague cookie is exists in settings
        # lang_exists = False
        # for language in settings.LANGUAGES:                           
        #     if current_language == language[0]:
        #         lang_exists = True
        #         break
        # if lang_exists == False:
        #     translation.activate('vi')
        #     response.set_cookie(settings.LANGUAGE_COOKIE_NAME,'vi')
        #     return response 

        # # Change language for logged in users
        # if request.user.is_authenticated:            
        #     user = User.objects.get(username = request.user.username)
        #     # if language is different from user language, ignore
        #     if current_language != user.userextend.language:  
        #         # save language settings to db           
        #         user.userextend.language = current_language
        #         user.userextend.save()
        #         translation.activate(current_language)
        #         response.set_cookie(settings.LANGUAGE_COOKIE_NAME, current_language)    
        #     return response
        return response
            


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip