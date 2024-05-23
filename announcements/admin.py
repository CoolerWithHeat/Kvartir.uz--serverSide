from django.contrib import admin
from django.contrib.auth.models import Group, User
from .models import *

webapp_name = 'Kvartir.uz'

admin.site.site_header = webapp_name
admin.site.site_title = webapp_name
admin.site.index_title = f"{webapp_name} administration"
admin.site.register(Announcement)
admin.site.register(apartment_images)
admin.site.register(floor)
admin.site.register(Reiltor_Number)
admin.site.register(phone_number)
admin.site.register(client_numbers)

admin.site.unregister(Group)
admin.site.unregister(User)