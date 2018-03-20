"""online_work URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from mywork import views

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^$', views.TableListView.as_view(), name='index'),
    url(r'^table_list', views.table_list, name='table_list'),
    url(r'^project', views.TableListView.as_view(), name='index'),
    url(r'^table/(?P<table_id>\d+)/$', views.table_view, name='main_table'),
    url(r'^edit_table/(?P<table_id>\d+)/$', views.edit_table, name='edit_table'),
    url(r'^new_table$', views.new_table, name='new_table'),
    url(r'^add_editor/(?P<tab_id>\d+)/(?P<user_id>\d+)/$', views.add_editor, name='add_editor'),
    url(r'^deleted_editor/(?P<tab_id>\d+)/(?P<user_id>\d+)/$', views.deleted_editor, name='deleted_editor'),
    url(r'^login$', views.LoginView, name='login'),
    url(r'^logout$', views.LogoutView, name='logout'),
]


