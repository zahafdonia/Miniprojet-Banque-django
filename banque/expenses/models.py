from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.models import Group, Permission
from decimal import Decimal
from django.contrib.auth.models import User

class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client', null=True, blank=True)
    firstname = models.CharField(max_length=100, verbose_name="Prénom")
    lastname = models.CharField(max_length=100, verbose_name="Nom")
    username = models.CharField(max_length=150, unique=True, verbose_name="Nom d'utilisateur")
    email = models.EmailField(unique=True, verbose_name="Email")
    password = models.CharField(max_length=128, verbose_name="Mot de passe")

    def __str__(self):
        return f"{self.firstname} {self.lastname} ({self.username})"

    class Meta:
        ordering = ['firstname']  # Tri par ordre alphabétique du prénom
    
    

class Compte(models.Model):
    TYPE_CHOICES = [
        ('courant', 'Compte Courant'),
        ('epargne', 'Compte Épargne'),
    ]

    identifiant = models.CharField(max_length=50, unique=True)
    client = models.ForeignKey('Client', on_delete=models.CASCADE, related_name='comptes')  
    solde = models.DecimalField(max_digits=10, decimal_places=2)
    date_ouverture = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)  

    def __str__(self):
        return f"{self.identifiant} - {self.client.firstname} {self.client.lastname}"

    
class Transaction(models.Model):
    TYPE_CHOICES = [
        ('retrait', 'Retrait'),
        ('versement', 'Versement'),
    ]

    compte = models.ForeignKey('Compte', on_delete=models.CASCADE)
    type_transaction = models.CharField(max_length=10, choices=TYPE_CHOICES)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date_transaction = models.DateTimeField(auto_now_add=True)
    description = models.TextField(null=True, blank=True)
    solde_apres_transaction = models.DecimalField(max_digits=10, decimal_places=2)


    def __str__(self):
        return f"{self.type_transaction.capitalize()} de {self.montant} DT sur {self.compte.identifiant} le {self.date_transaction}"