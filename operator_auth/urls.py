from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.operator_login, name='login'),
    path('logout/', views.operator_logout, name='logout'),
]