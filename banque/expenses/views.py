from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Compte,Client
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .forms import RechercheCompteForm
from django.contrib.auth.hashers import make_password
from .models import Compte, Transaction
from decimal import Decimal
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.utils.dateformat import DateFormat
# Create your views here.
@login_required(login_url='/login')

def index(request):
    clients = Client.objects.all().order_by('firstname')  # Liste des clients triés par prénom
    return render(request, 'expenses/index.html', {'clients': clients})
    



@login_required(login_url='/login')

def add_expenses(request): #add clients
    return render(request,'expenses/add_expenses.html')



def add_client(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        firstname = request.POST.get('FirstName')
        lastname = request.POST.get('LastName')
        email = request.POST.get('Email')
        password = request.POST.get('Password')

        # Validation des données 
        if not username or not firstname or not lastname or not email or not password:
            messages.error(request, "Tous les champs sont obligatoires.")
            return redirect('add-client')  # Redirection vers la page d'ajout de client


        hashed_password = make_password(password)
        # Ajouter un nouveau client
        Client.objects.create(
            username=username,
            firstname=firstname,
            lastname=lastname,
            email=email,
            password=hashed_password,
        )
        messages.success(request, "Client ajouté avec succès.")
        return redirect('expenses')  # Redirection vers la liste des clients après l'ajout

    return render(request, 'expenses/add_expenses.html')


def delete_client(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    client.delete()
    messages.success(request, "Client supprimé avec succès.")
    return redirect('expenses')

def edit_client(request, client_id):
    client = get_object_or_404(Client, id=client_id)

    if request.method == 'POST':
        client.username = request.POST.get('username')
        client.firstname = request.POST.get('firstname')
        client.lastname = request.POST.get('lastname')
        client.email = request.POST.get('email')
        client.password = request.POST.get('password')
        client.save()

        messages.success(request, "Client modifié avec succès.")
        return redirect('expenses')

    return render(request, 'expenses/edit_client.html', {'client': client})

def create_account(request):
    if request.method == 'POST':
        identifiant = request.POST.get('identifiant')
        client_id = request.POST.get('client_id')
        solde = request.POST.get('solde')
        type_compte = request.POST.get('type')

        # Validation des données
        if not identifiant or not client_id or not solde or not type_compte:
            messages.error(request, "Tous les champs sont obligatoires.")
            return redirect('create-account')

        if Compte.objects.filter(identifiant=identifiant).exists():
            messages.error(request, "Un compte avec cet identifiant existe déjà.")
            return redirect('create-account')

        if float(solde) < 250:
            messages.error(request, "Le solde de base doit être supérieur à 250 DT.")
            return redirect('create-account')

        if type_compte not in ['courant', 'epargne']:
            messages.error(request, "Type de compte invalide.")
            return redirect('create-account')

        # Création du compte
        client = Client.objects.get(id=client_id)
        Compte.objects.create(
            identifiant=identifiant,
            client=client,
            solde=solde,
            type=type_compte
        )
        messages.success(request, "Compte créé avec succès.")
        return redirect('comptes')

    clients = Client.objects.all()  # Pour afficher les clients dans le formulaire
    return render(request, 'expenses/create_account.html', {'clients': clients})

def list_comptes(request):
    comptes = Compte.objects.all().order_by('date_ouverture')  # Trier par date d'ouverture
    return render(request, 'expenses/comptes.html', {'comptes': comptes})


def supprimer_compte(request, pk):
    compte = get_object_or_404(Compte, id=pk)  
    compte.delete()  
    messages.success(request, f"Le compte {compte.identifiant} a été supprimé avec succès.")
    return redirect('comptes')

def rechercher_compte(request):
    compte = None
    form = RechercheCompteForm(request.GET)  

    if form.is_valid():
        identifiant = form.cleaned_data['identifiant']
        try:
            compte = Compte.objects.get(identifiant=identifiant)  
        except Compte.DoesNotExist:
            compte = None  
        if identifiant:
            compte = Compte.objects.filter(identifiant=identifiant).first()
            if not compte:
                messages.warning(request, "Aucun compte trouvé avec ce numéro.")
                
    return render(request, 'expenses/rechercher_compte.html', {'form': form, 'compte': compte})


#class ClientLoginView(LoginView):
    #template_name = 'authentication/loginClient.html'
    #redirect_authenticated_user = True
    #next_page = reverse_lazy('client/client_dashboard')


def login_client(request):
    if request.method == "POST":
        
        username = request.POST.get('username')
        password = request.POST.get('password')

       
        user = authenticate(request, username=username, password=password)

        if user is not None:
            
            login(request, user)

            
            try:
                client = Client.objects.get(user=user)
                
                return redirect('client/client_dashboard.html', client_id=client.id)
            except Client.DoesNotExist:
                
                return render(request, 'authentication/loginClient.html', {
                    'error': "Aucun client associé à cet utilisateur."
                })
        else:
            
            return render(request, 'authentication/loginClient.html', {
                'error': "Nom d'utilisateur ou mot de passe incorrect."
            })

    
    return render(request, 'client/client_dashboard.html')




def client_dashboard(request, client_id):
    # Récupérer le client et ses comptes associés
    client = get_object_or_404(Client, id=client_id)
    comptes = client.comptes.all()

    # Calcul du total solde
    total_solde = sum(compte.solde for compte in comptes)

    # Préparation des données pour le graphique (solde de chaque compte par date d'ouverture)
    solde_data = [{
        'x': compte.date_ouverture.strftime('%Y-%m-%d'),
        'y': float(compte.solde)
    } for compte in comptes]

    # Contexte à passer au template
    context = {
        'client': client,
        'nombre_comptes': comptes.count(),
        'total_solde': total_solde,
        'solde_data': solde_data,
        'comptes': comptes
    }

    # Rendre la page avec les données
    return render(request, 'client/client_dashboard.html', context)


#@login_required
#def client_dashboard(request):
 #   user = request.user

 #   try:
  #      client = Client.objects.get(id=client_id)
       # client = user.client  # Accéder au client associé
        #comptes = Compte.objects.filter(client=client)  # Liste de comptes
   #     compte_id = comptes[0].identifiant if comptes.exists() else None  # Premier compte
    #    comptes = client.comptes.all()
    #except Client.DoesNotExist:
     #   comptes = []
      #  compte_id = 000

    #context = {
     #   'username': user.username,
      #  'comptes': comptes,
        # 'compte_id': compte_id,
        #'first_name': user.first_name,  
       # 'last_name': user.last_name,
   # }
    
   # return render(request, 'client/client_dashboard.html', context)



def retrait_dargent(request, compte_id):
    """
    Vue pour gérer le retrait d'argent et l'enregistrement de la transaction.
    """
    compte = get_object_or_404(Compte, id=compte_id)

    if request.method == 'POST':
        montant = request.POST.get('montant')
        try:
            montant = Decimal(montant)
        except (ValueError, TypeError):
            messages.error(request, "Le montant doit être un nombre valide.")
            return redirect('retrait-dargent', compte_id=compte.id)

        if montant <= 0:
            messages.error(request, "Le montant doit être positif.")
        elif montant > 500:
            messages.error(request, "Le montant ne doit pas dépasser 500 DT.")
        elif compte.solde >= montant:
            # Mettre à jour le solde du compte
            compte.solde -= montant
            compte.save()

            # Enregistrer la transaction
            Transaction.objects.create(
                compte=compte,
                type_transaction='retrait',
                montant=montant,
                solde_apres_transaction=compte.solde
            )
            messages.success(request, f"Vous avez retiré {montant} DT de votre compte.")
        else:
            messages.error(request, "Le solde est insuffisant pour effectuer ce retrait.")
        return redirect('retrait-dargent', compte_id=compte.id)

    return render(request, 'client/retrait.html', {'compte': compte})


def versement_dargent(request, compte_id):
    """
    Vue pour gérer le versement d'argent et afficher un tableau de bord avec le graphique.
    """
    compte = get_object_or_404(Compte, id=compte_id)
    client = compte.client
    comptes_client = client.comptes.all()
    total_solde = sum(compte.solde for compte in comptes_client)
    nombre_comptes = comptes_client.count()

    # Préparation des données pour le Scatter Plot
    solde_data = [
        {'x': compte.date_ouverture.strftime('%Y-%m-%d'), 'y': float(compte.solde)}
        for compte in comptes_client
    ]

    # Gestion de la soumission du formulaire
    if request.method == 'POST':
        montant = request.POST.get('montant')
        try:
            montant = Decimal(montant)
        except (ValueError, TypeError):
            messages.error(request, "Le montant doit être un nombre valide.")
            return redirect('versement-dargent', compte_id=compte.id)

        if montant <= 0:
            messages.error(request, "Le montant doit être positif.")
        else:
            # Mettre à jour le solde et enregistrer la transaction
            compte.solde += montant
            compte.save()

            Transaction.objects.create(
                compte=compte,
                type_transaction='versement',
                montant=montant,
                solde_apres_transaction=compte.solde
            )
            messages.success(request, f"Vous avez versé {montant} DT sur votre compte.")
            return redirect('versement-dargent', compte_id=compte.id)

    # Rendu de la page avec toutes les informations
    context = {
        'compte': compte,
        'total_solde': total_solde,
        'nombre_comptes': nombre_comptes,
        'solde_data': solde_data,
    }
    return render(request, 'client/versement.html', context)

def historique_transactions(request, compte_id):
    """
    Afficher l'historique des transactions pour un compte donné.
    """
    compte = get_object_or_404(Compte, id=compte_id)
    transactions = Transaction.objects.filter(compte=compte).order_by('-date_transaction')

    return render(request, 'client/historique.html', {'compte': compte, 'transactions': transactions})

def dashboard(request):
    # Calcul des données nécessaires
    total_clients = Client.objects.count()
    total_comptes = Compte.objects.count()
    comptes_data = {
        'courant_count': Compte.objects.filter(type='courant').count(),
        'epargne_count': Compte.objects.filter(type='epargne').count(),
    }

    return render(request, 'expenses/dashboard.html', {
        'total_clients': total_clients,
        'total_comptes': total_comptes,
        'comptes_data': comptes_data,
    })