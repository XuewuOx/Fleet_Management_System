from django.urls import path
from dashboard.views.dashboard_views import *
from dashboard.views.layout_views import *
from dashboard.views.admin_views import *

urlpatterns = [
    #  Dashboard Index Page
    path('index/', dashboard, name='dashboard_index'),

    #  Fleet Monitoring Page
    #path('fleet_monitoring/', fleet_monitoring, name='fleet_monitoring'),

    #  Layout Page
    path('layout/', layout, name='layout'),
    path('layout_edit/', layout_edit, name='layout_edit'),

    #  Admin Page
    path('user_registration/', user_registration, name='user_registration'),
    path('profile/', profile, name='profile'),
    path('user_table/', user_table, name='user_table'),



]