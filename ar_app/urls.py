from django.urls import path
from ar_app.views import base,ar_view,video_feed

urlpatterns = [
    path('',base,name='base'),
    path('ar/', ar_view, name='ar_view'),
    path('video_feed/', video_feed, name='video_feed'),
]