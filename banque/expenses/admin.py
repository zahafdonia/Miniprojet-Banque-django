from django.contrib import admin
from django.contrib import admin
from .models import Client, Compte, Transaction
from django.db.models import Count
from django.utils.html import format_html
import json
from django.http import JsonResponse
from django.urls import path
# Register your models here.


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('firstname', 'lastname', 'email', 'username')  
    ordering = ('firstname',) 



@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('compte', 'type_transaction', 'montant', 'date_transaction')

#  Dashboard personnalisé
@admin.register(Compte)
class CompteAdmin(admin.ModelAdmin):
    list_display = ('identifiant', 'client', 'solde', 'type', 'date_ouverture')
    change_list_template = "admin/dashboard.html"

    def changelist_view(self, request, extra_context=None):
        # Récupérer le nombre total de clients et de comptes
        total_clients = Client.objects.count()
        total_comptes = Compte.objects.count()

        print("Total Clients:", total_clients)
        print("Total Comptes:", total_comptes)

        # Récupérer la répartition des types de comptes
        comptes_data = Compte.objects.values('type').annotate(total=Count('type'))
        comptes_data_dict = {compte['type']: compte['total'] for compte in comptes_data}

        # Nombre de comptes courants et épargne
        courant_count = comptes_data_dict.get('Courant', 0)
        epargne_count = comptes_data_dict.get('Epargne', 0)

        # Passer les données au template
        extra_context = extra_context or {}
        extra_context.update({
            'total_clients': total_clients,
            'total_comptes': total_comptes,
            'comptes_data': {
                'courant_count': courant_count,
                'epargne_count': epargne_count
            },
        })
        return super().changelist_view(request, extra_context=extra_context)
