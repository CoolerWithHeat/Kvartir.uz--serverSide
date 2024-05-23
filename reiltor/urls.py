from django.contrib import admin
from django.urls import path
from django.conf import settings
from announcements.views import *
from django.conf.urls.static import static

from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt

admin.site.login = csrf_exempt(admin.site.login)
admin.site.logout = csrf_exempt(admin.site.logout)
admin.site.password_change = csrf_exempt(admin.site.password_change)
admin.site.password_change_done = csrf_exempt(admin.site.password_change_done)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('serverdestination/createAnnouncement/', AnnouncementCreateView.as_view()),
    path('serverdestination/purgeAnnouncement/', DeleteAnnouncement.as_view()),
    path('serverdestination/handleRealtorContact/', ReiltorNumberView.as_view()),
    path('serverdestination/ResetAnnouncementImages/', AnnouncementDetailView.as_view()),
    path('serverdestination/FilterRequest/', FilteredAnnouncementsView.as_view()),
    path('serverdestination/AllAnnouncements/', AllAnnouncementRequest.as_view()),
    path('serverdestination/announcement/<int:product_id>/', GetAnnouncementInDetail.as_view()),
    path('serverdestination/authenticateAdmin/', ObtainExpiringToken.as_view()),
    path('serverdestination/ClientNumbers/', ManageClientNumbers.as_view()),
    path('serverdestination/sendMessage/', SendMessagesToClients.as_view()),
    path('serverdestination/purgeNumber/', PurgeNumber.as_view()),

] + static(settings.STATIC_URL, document_root=settings.MEDIA_ROOT)
