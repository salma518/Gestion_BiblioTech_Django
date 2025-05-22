from django import forms
from .models import Livre,Admin,Utilisateur
from django.contrib.auth.forms import UserChangeForm

class LivreForm(forms.ModelForm):
    class Meta:
        model = Livre
        fields = '__all__'
        widgets = {
            'date_pub': forms.DateInput(attrs={'type': 'date'}),
            'detail': forms.Textarea(attrs={'rows': 4}),
        }

# class AdminProfileForm(UserChangeForm):
#     password = None  # On ne montre pas le mot de passe ici

#     class Meta:
#         model = Admin
#         fields = ['nom', 'prenom', 'email', 'numeroTelephone', 'adresse', 'cin']
#         widgets = {
#             'email': forms.EmailInput(attrs={'class': 'form-control'}),
#             'nom': forms.TextInput(attrs={'class': 'form-control'}),
#             'prenom': forms.TextInput(attrs={'class': 'form-control'}),
#             'numeroTelephone': forms.TextInput(attrs={'class': 'form-control'}),
#             'adresse': forms.TextInput(attrs={'class': 'form-control'}),
#             'cin': forms.TextInput(attrs={'class': 'form-control'}),
#         }


class BaseProfileForm(UserChangeForm):
    password = None
    class Meta:
        fields = ['nom', 'prenom', 'email', 'numeroTelephone', 'adresse', 'cin']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'numeroTelephone': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control'}),
            'cin': forms.TextInput(attrs={'class': 'form-control'}),
        }

class AdminProfileForm(BaseProfileForm):
    class Meta(BaseProfileForm.Meta):
        model = Admin

class UtilisateurProfileForm(BaseProfileForm):
    class Meta(BaseProfileForm.Meta):
        model = Utilisateur
        fields = BaseProfileForm.Meta.fields + ['solde']  # Ajoute juste le champ solde
        widgets = {
            **BaseProfileForm.Meta.widgets,  # Conserve tous les widgets existants
            'solde': forms.NumberInput(attrs={'class': 'form-control'})
        }
        
