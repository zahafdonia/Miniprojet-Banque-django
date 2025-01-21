from django import forms

class RechercheCompteForm(forms.Form):
    identifiant = forms.CharField(max_length=100, required=True, label="Numéro du compte")
