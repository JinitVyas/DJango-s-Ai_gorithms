from django.contrib import admin
from django.urls import path
from LandingPage import views
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name="home"),
    path('token_request',views.run_get_token),
    path('find_Track',views.run_get_song_details),
    path('recommend',views.run_get_recommendation),
    path('features',views.run_get_features),
    path('filterout',views.run_get_top10),
    path('end',views.end)
] 