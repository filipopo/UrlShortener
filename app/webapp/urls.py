from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('u/<str:path>', views.u, name='u'),
    path('url/<str:path>', views.url, name='url'),
    path('url/', views.urls, name='urls'),
    path('link/<str:path>', views.link, name='link'),
    path('link/', views.links, name='links'),
    path('accounts/register/', views.register, name='register'),
]
