from django.conf.urls import url,include
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^restapp/',include('restapp.urls')),
    url(r'^merchantapp/',include('merchantapp.urls'))
]
