"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login_, name='login'),
    path('logout/', views.logout_, name='logout'),

    path('formCreateClient/', views.formCreateClient, name='formCreateClient'),
    path('check-phone-number/', views.check_phone_number, name = 'check_phone_number'),
    path('motivationalPhrase/', views.motivationalPhrase, name='motivationalPhrase'),
    path('', views.index, name='index'),

    path('select_client/', views.select_client, name='select_client'),
    path('clientObamacare/', views.clientObamacare, name='clientObamacare'),
    path('clientSupp/', views.clientSupp, name='clientSupp'),
    
    path('toggleObamaStatus/<obamacare_id>/', views.toggleObamaStatus, name='toggleObamaStatus'),
    path('toggleSuppStatus/<supp_id>/', views.toggleSuppStatus, name='toggleSuppStatus'),

    path('editClientObama/<obamacare_id>/', views.editClientObama, name='editClientObama'),

    # Json
    path('formCreatePlan/<client_id>/', views.formCreatePlan, name='formCreatePlan'),
    path('fetchAca/<client_id>/', views.fetchAca, name='fetchAca'),
    path('fetchSupp/<client_id>/', views.fetchSupp, name='fetchSupp'),
    path('fetchDependent/<client_id>/', views.fetchDependent, name='fetchDependent'),



    path('formCreatePlan/deleteDependent/<int:dependent_id>/', views.delete_dependent, name='delete_dependent'),
    path('formCreatePlan/deleteSupp/<int:supp_id>/', views.delete_supp, name='delete_supp'),

    path('table/', views.table, name='table')
]
