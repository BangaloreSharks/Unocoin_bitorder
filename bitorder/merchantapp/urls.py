
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.merchant , name = 'merchant'),
    url(r'^merchantlogin$', views.merchantlogin , name = 'merchantlogin'),
    url(r'^merchant$', views.merchant_order , name = 'merchant_order'),
    url(r'^order$', views.order , name = 'order'),
    url(r'^refresh_order$', views.refresh_order , name = 'refresh_order'),
    url(r'^delete$', views.delete , name = 'delete'),    
    #url(r'^orderpage$', views.orderpage , name = 'orderpage'),
]
