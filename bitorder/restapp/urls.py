
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.customer , name = 'customer'),
    url(r'^customerlogin$', views.customerlogin , name = 'customerlogin'),
    url(r'^test$', views.test , name = 'test'),
    url(r'^menu/$', views.menu , name = 'menu'),
    url(r'^menu/(?P<id>[\w\s]+)$',views.menu, name='menu'),
    url(r'^order$',views.order, name='order'),
]
