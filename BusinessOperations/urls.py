from django.conf.urls import url,include
from django.contrib import admin
from rest_framework import routers
from Times import views

urlpatterns = [
   url(r'^getDuration', views.getDuration, name='getDuration')
]
