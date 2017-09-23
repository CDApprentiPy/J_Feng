from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='logreg_index'),
    url(r'process/$', views.process, name='logreg_process'),
    url(r'login/$', views.login, name='logreg_login'),
    url(r'logout/$', views.logout, name='logreg_logout'),
    url(r'(?P<id>\d+)/(?P<session_type>\w+)/success/$', views.success, name='logreg_success'),    
]
