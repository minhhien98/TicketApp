import logging
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

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip