from django.middleware.csrf import CsrfViewMiddleware
from django.urls import reverse

class CustomCsrfViewMiddleware(CsrfViewMiddleware):
    def process_view(self, request, callback, callback_args, callback_kwargs):
        admin_url = reverse('admin:index')
        if request.path.startswith(admin_url):
            return None
        return super().process_view(request, callback, callback_args, callback_kwargs)