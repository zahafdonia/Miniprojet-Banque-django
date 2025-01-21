from django.urls import path
from . import views
from .views import  client_dashboard
from django.views.decorators.csrf import csrf_exempt
from django.contrib import admin
from django.urls import path,include
from authentication.views import  LogoutView, LoginView

urlpatterns = [
    path('expenses/dashboard', views.dashboard, name="dashboard"),  #vous devrer changer cette pour allez au dashboar admin
    path('expenses', views.index, name='expenses'),
    path('add-expenses', views.add_client, name="add-expenses"),
    path('edit-client/<int:client_id>/', views.edit_client, name="edit-client"),  
    path('delete-client/<int:client_id>/', views.delete_client, name="delete-client"),  
    path('comptes/', views.list_comptes, name="comptes"),
    path('create-account/', views.create_account, name="create-account"),
    path('delete-account/<int:pk>/', views.supprimer_compte, name='delete-account'),
    path('rechercher-compte/', views.rechercher_compte, name='rechercher-compte'),
    

    
    path('retrait/<int:compte_id>/', views.retrait_dargent, name='retrait-dargent'),
    path('versement/<int:compte_id>/', views.versement_dargent, name='versement-dargent'),
    path('loginClient/', views.login_client, name='loginClient'),
    path('client-dashboard/<int:client_id>/', views.client_dashboard, name='client_dashboard'),
    path('historique/<int:compte_id>/', views.historique_transactions, name='historique-transactions'),
]
    
