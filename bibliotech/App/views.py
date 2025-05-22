# Standard Library
from datetime import date, datetime, timedelta
from email import message
from decimal import Decimal

# Django Core
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from django.views import View
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.utils import timezone
from .models import Livre, Utilisateur, Emprunt, Achats

from .models import Commande,Emprunt,Achats
from .forms import LivreForm,AdminProfileForm, UtilisateurProfileForm
from django.contrib.auth.decorators import login_required


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.views import View
from .models import Admin

import random
from django.core.cache import cache
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.conf import settings

# Local Models
from .models import (
    Admin,
    Commande,
    Emprunt,
    Facture,
    Favoris,
    Livre,
    Panier,
    Utilisateur
)

# Third Party

import requests


class LandingPage(View):
    def get(self, request):
        return render(request, 'landing.html')

class LoginPage(View):
   def get(self, request):
    if 'adm' in request.path:
        return render(request, 'Administrateur/loginPage.html')
    return render(request, 'Utilisateur/loginPage.html')

class AuthUtilisateur(View):
    def get_livres(self):
        """Récupère tous les livres avec optimisation"""
        return Livre.objects.all() # Optimisation des ForeignKey

    def get(self, request):
        if request.user.is_authenticated:
            livres = self.get_livres()
            paginator = Paginator(livres, 8)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            return render(request, 'Utilisateur/homePage.html', {
                'user': request.user,
                'livres': page_obj
            })
        return redirect('login_page')  # Redirige si non authentifié

    def post(self, request):
        """Gère l'authentification"""
        userEmail = request.POST.get('email')
        userPassword = request.POST.get('password')
        
        # Vérification du mot de passe via authenticate()
        userconnecte = authenticate(request, username=userEmail, password=userPassword)
        
        if userconnecte is not None:
            # Vérification compte admin
            if userconnecte.email.endswith('@adm.com'):
                return render(request, "Utilisateur/loginPage.html", {
                    "message": "Ce compte est un compte administrateur. Veuillez utiliser la connexion administrateur."
                })
            
            # Vérification compte désactivé
            if not userconnecte.compte_actif:
                return render(request, "Utilisateur/loginPage.html", {
                    "message": "Ce compte est désactivé. Veuillez contacter l'administrateur."
                })
            
            # Connexion réussie
            login(request, userconnecte)
            
            # Initialisation du panier
            request.session['cart_count'] = Panier.objects.filter(user=userconnecte).count()
            
            # Pagination des livres
            livres = self.get_livres()
            paginator = Paginator(livres, 8)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            
            return render(request, 'Utilisateur/homePage.html', {
                'user': userconnecte,
                'livres': page_obj
            })
        
        # Échec authentification
        return render(request, "Utilisateur/loginPage.html", {
            "message": "Email ou mot de passe incorrect. Veuillez réessayer."
        })

class AuthAdmin(View):

    def get_admin_context(self):
        last24h = Achats.objects.filter(date__gte=timezone.now()-timedelta(hours=24))
        return {
            'nbrLivre': Livre.objects.count(),
            'nbrUser': Utilisateur.objects.count(),
            'nbrEmp': Emprunt.objects.filter(date_fin__gt=timezone.now().date()).count(),
            'livres': Livre.objects.all(),  
            
            # Données journalières avec select_related
            'total_achats_jour': last24h.count(),
            'Emprunt_actifs': Emprunt.objects.all().order_by('-date_debut')[:10],
            'NVAchats': Achats.objects.all().order_by('-date')[:10],
            'today': timezone.now().date()
        }

    def get(self, request):
        if request.user.is_authenticated and request.user.email.endswith('@adm.com'):
            return render(request, 'Administrateur/homePage.html', self.get_admin_context())
        # Redirection vers la page de login si non authentifié ou non admin
        return redirect('admin_login') 
    def post(self, request):
        userEmail = request.POST.get('email')
        userPassword = request.POST.get('password')
        userconnecte = authenticate(request, username=userEmail, password=userPassword)

        if userconnecte is not None and userconnecte.email.endswith('@adm.com'):
            login(request, userconnecte)
            context = self.get_admin_context()
            
            context['user'] = userconnecte
            return render(request, 'Administrateur/homePage.html', context)
        
        messages.error(request,"Email ou mot de passe incorrect. Veuillez réessayer.")  
        return render(request, "Administrateur/loginPage.html")
    
class LogoutView(View):
    def get(self, request):
        if request.user.is_authenticated:
            logout(request)
            return render(request, 'landing.html', {'message': 'Vous avez été déconnecté avec succès.'})
        return render(request, 'landing.html')

def afficherform(request):
    if request.user.is_authenticated:
        if request.user.email.endswith('@adm.com'):
            return render(request, 'Administrateur/homePage.html', {'user': request.user})
        return render(request, 'Utilisateur/homePage.html', {'user': request.user})
    return render(request, 'Utilisateur/register.html')

def register(request):
    if request.method != 'POST':
        return render(request, 'Utilisateur/register.html')
    
    nom = request.POST.get('nom')
    prenom = request.POST.get('prenom')
    email = request.POST.get('email')
    adresse = request.POST.get('adresse')
    numeroTelephone = request.POST.get('numtel')
    cin = request.POST.get('cin')
    password = request.POST.get('password')
    solde = request.POST.get('solde')

    # Vérification si l'email existe déjà
    if Utilisateur.objects.filter(cin=cin).exists():
        message = "Cet email est déjà utilisé"
        return render(request, 'Utilisateur/register.html', {'message': message})

    try:
        
        hashed_password = make_password(password)
        utilisateur = Utilisateur.objects.create(
            nom=nom,
            prenom=prenom,
            email=email,
            adresse=adresse,
            numeroTelephone=numeroTelephone,
            cin=cin,
            solde=solde,
            password=hashed_password
        )
        message = "Compte créé avec succès ! Vous pouvez maintenant vous connecter."
        return render(request, 'Utilisateur/loginPage.html', {'message': message})
    except Exception as e:
        message = "Une erreur est survenue lors de la création du compte. Veuillez réessayer."
        messages.error("Une erreur est survenue lors de la création du compte. Veuillez réessayer")
        return render(request, 'Utilisateur/register.html', {'message': message})

#Interface Admin

def admin_profile(request, admin_id):
    admin = Admin.objects.get(id=admin_id)
    return render(request, 'Administrateur/ProfilAdm.html',
                {'admin': admin,
                'nbrLivre':Livre.objects.count(),
                'nbrUser':Utilisateur.objects.count()})

def liste_utilisateurs(request):
    return render(request, 'Administrateur/TotalUtilisateur.html', {
        'utilisateurs': Utilisateur.objects.all()
    })

def Tri_utilisateurs(request):
    # Récupération des paramètres
    statut = request.GET.get('is_active', 1)  
    tri = request.GET.get('tri', 'recent') 
    compte = request.GET.get('compte_actif',1)      
    
    # Filtrage de base
    utilisateurs = Utilisateur.objects.all()
    
    # Filtrage par statut
    utilisateurs = utilisateurs.filter(is_active=statut)
    
    # Filtrage par compte_actif
    utilisateurs = utilisateurs.filter(compte_actif=compte)

    # Tri des résultats
    if tri == 'recent':
        utilisateurs = utilisateurs.order_by('-date_joined')
    elif tri == 'ancien':
        utilisateurs = utilisateurs.order_by('date_joined')
    elif tri == 'nom':
        utilisateurs = utilisateurs.order_by('nom')
    
    return render(request, 'Administrateur/TotalUtilisateur.html', {
        'utilisateurs': utilisateurs
    } )
   
def details_utilisateur(request, user_id):
    return render(request, 'Administrateur/detail_Utilisateur.html', {
        'utilisateur': get_object_or_404(Utilisateur, id=user_id)
    })

def user_deactivate(request, user_id):
    user = get_object_or_404(Utilisateur, id=user_id)
    user.compte_actif = False
    user.save()

     # Paramètres du message
    subject = " Désactivation de compte"
    message = f"""
    Bonjour {user.nom},
    
    Votre compte a été désactivé en raison d'inactivité.
    
    L'équipe du site
    """
    from_email = "noreply@monsite.com"
    recipient_list = [user.email]
    
    # Envoyer l'email
    send_mail(subject, message, from_email, recipient_list)
    
    messages.success(request, f"Un avertissement a été envoyé à {user.email}")

    return redirect('liste_utilisateurs')


def liste_livres(request):

    livres = Livre.objects.all()
    paginator = Paginator(livres, 8)  # Show 10 books per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Livre.objects.values_list('genre', flat=True).distinct()

    return render(request, 'Administrateur/Livres.html', {'livres': page_obj,'categories':categories})

def detail_livre(request, id):
    return render(request, 'Administrateur/detail_livre.html', {
        'livre': Livre.objects.get(id=id)
    })

def ajouter_livre(request):
    if request.method == 'POST':
        form = LivreForm(request.POST)
        if form.is_valid():
            nouveau_livre = form.save()
            return redirect('Detaillivre', id=nouveau_livre.id)
    else:
        form = LivreForm()
    return render(request, 'Administrateur/ajouter_livre.html', {'form': form})

def supprimer_livre(request, pk):
    livre = get_object_or_404(Livre, id=pk)
    livre.delete()
    return redirect('liste_livres')
    
def modifier_livre(request, pk):
    livre = get_object_or_404(Livre, pk=pk)
    if request.method == 'POST':
        form = LivreForm(request.POST, instance=livre)
        if form.is_valid():
            form.save()
            return redirect('Detaillivre',id = pk)
    else:
        form = LivreForm(instance=livre)
    return render(request, 'Administrateur/modifier_livre.html', {'form': form, 'livre':livre})

def livres_par_categorie(request):
    categorie = request.GET.get('genre', '')
    
    if categorie != 'Tous les livres':
        Livres = Livre.objects.filter(genre=categorie)
        paginator = Paginator(Livres, 8)  # Show 10 books per page
        page_number = request.GET.get('page')
        livres = paginator.get_page(page_number)

    else:
        Livres = Livre.objects.all()
        paginator = Paginator(Livres, 8)  # Show 10 books per page
        page_number = request.GET.get('page')
        livres = paginator.get_page(page_number)
    categories = Livre.objects.values_list('genre', flat=True).distinct()
    
    return render(request, 'Administrateur/Livres.html', {
        'livres': livres,
        'categories': categories,
        'categorie_actuelle': categorie
    })

def rechercher_livres(request):
    query = request.GET.get('q', '')
    
    if query:
        Livres = Livre.objects.filter(
            Q(titre__icontains=query) | 
            Q(auteur__icontains=query))
        paginator = Paginator(Livres, 8)  # Show 10 books per page
        page_number = request.GET.get('page')
        livres = paginator.get_page(page_number)
    else:
        Livres = Livre.objects.all()
        paginator = Paginator(Livres, 8)  # Show 10 books per page
        page_number = request.GET.get('page')
        livres = paginator.get_page(page_number)

    if request.user.email.endswith('@adm.com'):
     return render(request, 'Administrateur/Livres.html', {'livres': livres, 'query': query})
    else:
     return render(request, 'Utilisateur/homePage.html', {'livres': livres, 'query': query}) 
    
def livres_disponibilite(request):
    disponibilite = request.GET.get('Disponiblite', '')

    if disponibilite == 'Rupture':
        livres_queryset = Livre.objects.filter(quantite=0)
    elif disponibilite == 'Disponible':
        livres_queryset = Livre.objects.filter(quantite__gt=0)
    
    paginator = Paginator(livres_queryset, 8)  # 8 livres par page
    page_number = request.GET.get('page')
    livres = paginator.get_page(page_number)

    return render(request, 'Administrateur/Livres.html', {
        'livres': livres,
    })
    
@login_required

def profile_Admin_view(request):
    if request.method == 'POST':
        form = AdminProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            admin = form.save()
            return redirect('admin_profile',admin_id=admin.id)
    else:
        form = AdminProfileForm(instance=request.user)

    return render(request, 'Administrateur/modifier_profile.html', {'form': form})
   
def profile_User_view(request):
    if request.method == 'POST':
        form = UtilisateurProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save()
            return redirect('user_profile',user_id=user.id)
    else:
        form = UtilisateurProfileForm(instance=request.user)
     
    return render(request, 'Utilisateur/Modifier.html', {'form': form})  

class PasswordResetAdmin(LoginRequiredMixin,View):
    def get(self, request, admin_id):
        # Vérifie que l'admin existe avant d'afficher le formulaire
        get_object_or_404(Admin, id=admin_id)
        return render(request, 'Administrateur/password_reset_admin.html', {'admin_id': admin_id})

    def post(self, request, admin_id):
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validation des champs vides
        if not password or not confirm_password:
            messages.error(request, "Veuillez remplir tous les champs")
            return render(request, 'Administrateur/password_reset_admin.html', {'admin_id': admin_id})
        
        # Validation de la correspondance
        if password != confirm_password:
            messages.error(request, "Les mots de passe ne correspondent pas")
            return render(request, 'Administrateur/password_reset_admin.html', {'admin_id': admin_id})
        
        
        # Récupération et mise à jour sécurisée
        admin = Admin.objects.get(id=admin_id)
        admin.password = make_password(password)
        admin.save()
        
        messages.success(request, "Mot de passe réinitialisé avec succès")
        return redirect('admin_login') 

def Warn_email(request, user_id):
    # Récupérer l'utilisateur
    user = get_object_or_404(Utilisateur, id=user_id)
    print(user.last_login)
    # Paramètres du message
    subject = "Avertissement de désactivation de compte"
    message = f"""
    Bonjour {user.nom},
    
    Votre compte sera désactivé dans 7 jours en raison d'inactivité.
    
    Connectez-vous avant le {user.last_login.date() + timedelta(days=7)} pour conserver votre compte.
    
    L'équipe du site
    """
    from_email = "noreply@monsite.com"
    recipient_list = [user.email]
  
    
    # Envoyer l'email
    send_mail(subject, message, from_email, recipient_list)
    
    messages.success(request, f"Un avertissement a été envoyé à {user.email}")
    return redirect('liste_utilisateurs')    

#Interface Utilisateur

from django.core.paginator import Paginator


class ListeLivres(View):
    def get(self, request):
        try:
            livres = Livre.objects.all()
            paginator = Paginator(livres, 10)  # Affiche 10 livres par page

            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            return render(request, 'Utilisateur/homePage.html', {'livres': page_obj})
        except Exception as e:
            print("Erreur lors de la récupération des livres:", str(e))  # Pour le débogage
            return render(request, 'Utilisateur/homePage.html', {'livres': [], 'error': str(e)})

class DetailLivre(View):
    def get(self, request, livre_id):
        livre = get_object_or_404(Livre, id=livre_id)
        return render(request, 'Utilisateur/detail_livre.html', {'livre': livre})

# Panier
class AjouterAuPanier(LoginRequiredMixin, View):
    login_url = '/login/'

    def post(self, request, livre_id):
      livre = Livre.objects.get(id=livre_id)
      panier_existant = Panier.objects.filter(user_id=request.user.id, livre_id=livre).first()

      if not panier_existant:
                panier = Panier.objects.create(user=request.user, livre_id=livre.id,prix=livre.prix)
                if panier.livre.quantite > 0:
                    panier.quantite = 1
                    panier.save()
                messages.success(request, 'Livre ajouté au panier avec succès!')
                
      else:
                messages.info(request, 'Ce livre est déjà dans votre panier.')
                     
      request.session['cart_count'] = Panier.objects.filter(user=request.user).count()
      return redirect('ListeLivres')

class SupprimerDuPanier(LoginRequiredMixin, View):
    login_url = '/login/'

    def post(self, request, livre_id):
        panier_item = get_object_or_404(Panier, user=request.user, livre_id=livre_id)
        panier_item.delete()
        messages.success(request, 'Livre retiré du panier avec succès!')
     # Mettre à jour le compteur du panier
        request.session['cart_count'] = Panier.objects.filter(user=request.user).count()
        return redirect('panier')

class AfficherPanier(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        items_panier = Panier.objects.filter(user=request.user).select_related('livre')

        total = sum(
            (item.livre.prix / 2) if item.quantite == 0 
            else (item.livre.prix * item.quantite) 
            for item in items_panier
        )
        SomRup = sum(1 for item in items_panier if item.livre.quantite == 0)
        SomDis = sum(1 for item in items_panier if item.livre.quantite > 0)
        
        if SomRup != 0:
         messages.info(
                request,
                "Certains livres de votre panier sont en rupture de stock. En confirmant la commande, vous recevrez uniquement leurs liens (URL) avec une réduction de 50 % sur leur prix."
            )
        
        return render(request, 'Utilisateur/panier.html', {
            'items_panier': items_panier,
            'total': total,
            'Rup' : SomRup,
            'Dispo' : SomDis,
        })

    def post(self, request):
        livre_id = request.POST.get('livre_id')
        action = request.POST.get('action')
        
        
        panier_item = Panier.objects.get(user=request.user, livre_id=livre_id)
        
        if action == 'incrementer':
            panier_item.quantite += 1
        elif action == 'decrementer':
            if panier_item.quantite > 1:  # Empêche la quantité négative
                panier_item.quantite -= 1
        
        panier_item.save()

        return redirect('panier')

#Favoris    
class AjouterAuxFavoris(LoginRequiredMixin, View):
    login_url = '/login/'

    def post(self, request, livre_id):
        livre = get_object_or_404(Livre, id=livre_id)
        if livre is not None:
            favori_existant = Favoris.objects.filter(user=request.user, livre=livre).first()
            if not favori_existant:
                # Create a new favorite entry
                Favoris.objects.create(user=request.user, livre=livre)
                messages.success(request, 'Livre ajouté aux favoris avec succès!')
                return redirect('favoris') 
            else:
                messages.info(request, 'Ce livre est déjà dans vos favoris.')
                return redirect('ListeLivres')
        else:
            messages.error(request, 'Livre non trouvé.')
            return redirect('ListeLivres')
        
class SupprimerDesFavoris(LoginRequiredMixin, View):
    login_url = '/login/'

    def post(self, request, livre_id):
        favori_item = get_object_or_404(Favoris, user=request.user, livre_id=livre_id)
        favori_item.delete()
        messages.success(request, 'Livre retiré des favoris avec succès!')
        return redirect('favoris')
    
class AfficherFavoris(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        favoris = Favoris.objects.filter(user=request.user).select_related('livre')
        return render(request, 'Utilisateur/favoris.html', {
            'favoris': favoris
        })


class ValiderPanier(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        user = request.user

        items_panier = Panier.objects.filter(user=user).select_related('livre')

        total_panier = sum(
            (item.livre.prix / 2) if item.quantite == 0 
            else (item.livre.prix * item.quantite) 
            for item in items_panier
        )
    
        if total_panier == 0:
            messages.info(request, "Votre panier est vide.")
            return redirect('home_user')

        if user.solde < total_panier:
            messages.info(request, "Solde insuffisant. Veuillez recharger votre compte pour valider le panier.")
            return redirect('home_user')
        
        choix = request.GET.get('action_type')
        # Si solde suffisant, afficher les options "Emprunter" et "Acheter"
        return render(request, 'Utilisateur/valider_panier.html', {
            'total_panier': total_panier,
            'items_panier': items_panier,
            'user_solde': user.solde,
            'choix' : choix,
        })
    
class AcheterPanier(LoginRequiredMixin, View):
    login_url = '/login/'

    @transaction.atomic
    def post(self, request):
        items_panier = Panier.objects.filter(user=request.user).select_related('livre')
        if not items_panier.exists():
            messages.error(request, "Votre panier est vide.")
            return redirect('panier')
        
        total = sum(
            (item.livre.prix / 2) if item.quantite == 0 
            else (item.livre.prix * item.quantite) 
            for item in items_panier
        )

        quantite = sum(item.quantite for item in items_panier if item.livre.quantite > 0)

        for item in items_panier:
            item.livre.quantite -= item.quantite
            item.livre.save()

        if request.user.solde < total:
            messages.error(request, "Solde insuffisant.")
            return redirect('panier')

        # Déduction du solde utilisateur
        utilisateur = request.user
        utilisateur.solde -= total
        utilisateur.save()

        # Création de la commande
        commande = Commande.objects.create(
                user=utilisateur,
                titre=f"Commande N°{Commande.objects.count() + 1}",
                date_commande=date.today(),
                montant_total=total,
                quantite = quantite
            )
        

            # Création de la facture
        Facture.objects.create(
                commande=commande,
                date_facture=date.today(),
                montant=total
            )

            # Préparation des URLs de téléchargement
        livres_details = [
                f"- {item.livre.titre}: {item.livre.download_url}"
                for item in items_panier
            ]
        
        achats_crees = []
        for item in items_panier:
            achat = Achats.objects.create(
                user=utilisateur,
                livre=item.livre,
                total=total,
                quantite=quantite
            )
            achats_crees.append(achat)

            # Envoi d'email
        send_mail(
                subject=f"Confirmation de votre commande N°{commande.id}",
                message=(
                    f"Bonjour,\n\n"
                    f"Merci pour votre achat ! Voici les détails :\n\n"
                    f"Livres achetés :\n" + "\n".join(livres_details) + "\n\n"
                    f"Montant total : {total} €\n"
                    f"Date : {commande.date_commande}\n\n"
                    f"Cordialement,\nL'équipe de votre librairie"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[utilisateur.email],  # Utiliser l'email de l'utilisateur
                fail_silently=False,
            )

           # Vider le panier
        items_panier.delete()
        request.session['cart_count'] = Panier.objects.filter(user=request.user).count()
        messages.success(request, "Achat réussi. Un email avec les liens vous a été envoyé.")
        Panier.objects.filter(user=request.user).count()

        return redirect('confirmation_achat', commande_id=commande.id)

def confirmation_achat(request, commande_id):
    try:
        commande = Commande.objects.get(id=commande_id, user=request.user)
        if not request.user.is_active:  # Évite des sauvegardes inutiles
         request.user.is_active = True
         request.user.save()
        
        return render(request, 'Utilisateur/confirmation_achat.html', {'commande': commande, 'user': request.user})
    except Commande.DoesNotExist:
        return redirect('ListeLivres')  # Rediriger si la commande n'existe pas

class EmprunterPanier(LoginRequiredMixin, View):
    login_url = '/login/'

    def post(self, request):
        try:
            # jours_emprunt = int(request.POST.get('jours_emprunt', 1))
            duree_emprunt = request.POST.get('date_fin')
            dt = datetime.strptime(duree_emprunt, "%Y-%m-%dT%H:%M")
            
            if dt <= datetime.now():
              messages.error(request, "La date de fin doit être dans le futur.")
              return redirect('valider_panier')
            
            duree_timedelta = dt - datetime.now()
            
            #duree_jours = Decimal(duree_timedelta.days)  # Conversion en Decimal
            duree_jours = Decimal(duree_timedelta.total_seconds()) / Decimal(86400)
            

            # Validation de la durée
            if duree_jours <= Decimal(0):
                messages.error(request, "La durée ne peut pas être nulle ou négative.")
                return redirect('valider_panier')

            if duree_jours < Decimal(1/1440) or duree_jours > Decimal(30):  # 1 minute = 1/1440 jour
                messages.error(request, "La durée doit être d'au moins 1 minute et ≤ 30 jours.")
                return redirect('valider_panier')

            # Calcul du total
            items_panier = Panier.objects.filter(user=request.user)
            total = Decimal('0.0')
           
            # total = sum(item.livre.prix * Decimal('0.2') * duree_jours 
            #          for item in items_panier)

            total = sum(
                (item.livre.prix * Decimal('0.005')) * item.quantite *duree_jours  # 0.5% du prix/jour
                for item in items_panier
            )
            
            montant_total = total.quantize(Decimal('0.0001'))
           
            # Vérifier le solde utilisateur
            if request.user.solde < montant_total:
              messages.error(request, "Solde insuffisant.")
              return redirect('panier')
            
            # Créer l'emprunt et sauvegarder l'ID
            
            for item in items_panier:
               emprunt = Emprunt.objects.create(
               user=request.user,
               livre=item.livre,
               date_debut=timezone.now(),
               date_fin=dt,
               duree_emprunt=duree_jours,  # Stocke la durée en jours
               )

            
            # Débiter le solde et sauvegarder
            utilisateur = request.user
            utilisateur.solde -= montant_total
            utilisateur.save()


            message = (
                f"Merci pour votre Emprunte !\n\n"
                f"Montant total: {montant_total} Euro\n"
            )

            
            send_mail(
                subject="Votre emprunte de livres",
                message= message,
                from_email=settings.DEFAULT_FROM_EMAIL,  # Utilise l'email configuré
                recipient_list=[utilisateur.email],
                fail_silently=False,
            )

            # Vider le panier
            items_panier.delete()
            request.session['cart_count'] = Panier.objects.filter(user=request.user).count()
            messages.success(request, "Emprunt réussi. Un email avec les liens vous a été envoyé.")
            request.session['emprunt_total'] = str(total)  
            return redirect('confirmation_emprunt', emprunt_id=emprunt.id)
        
        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")
            return redirect('panier')
    
@login_required

def confirmation_emprunt(request, emprunt_id):
    emprunt = None  # Initialisation de la variable
    try:
        emprunt = Emprunt.objects.get(id=emprunt_id, user=request.user)

        if not request.user.is_active:  # Évite des sauvegardes inutiles
         request.user.is_active = True
         request.user.save()

        total = Decimal(request.session.get('emprunt_total', '0'))
        total = total.quantize(Decimal('0.0001'))
    except Emprunt.DoesNotExist:
        return redirect('ListeLivres')
    
    # Si on arrive ici, c'est que l'emprunt existe
    return render(request, 'Utilisateur/confirmation_emprunt.html', {
        'emprunt': emprunt,
        'user': request.user,
        'total':total
    })


# CategoriesView

class CategoriesView(View):
    def get(self, request):
        # Récupérer tous les genres distincts disponibles
        genres = Livre.objects.values_list('genre', flat=True).distinct()
        return render(request, 'Utilisateur/categories.html', {'genres': genres})

class LivresParGenre(View):
    def get(self, request, genre):
        livres = Livre.objects.filter(genre=genre)
        return render(request, 'Utilisateur/livres_par_genre.html', {
            'livres': livres,
            'genre': genre
        })

class MesEmprunts(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        # Fetch all emprunts for the user
        local_dt = datetime.now()

        Emprunt.objects.filter(user=request.user, date_fin__lte=local_dt).delete()

        # Fetch remaining emprunts after deletion
        emprunts = Emprunt.objects.filter(user=request.user)
        if not emprunts.exists():
            messages.info(request, "Vous n'avez aucun emprunt en cours.")
            return render(request, 'Utilisateur/mes_emprunts.html', {'emprunts': []})

        # Prepare details for the template
        emprunt_details = []
        for emprunt in emprunts:
            livre = emprunt.livre
           
            emprunt_details.append({
                'titre': livre.titre,
                'url': livre.download_url if hasattr(livre, 'download_url') else '#',
                'duree_emprunt': emprunt.duree_emprunt,
                'date_debut': emprunt.date_debut,
                'date_fin': emprunt.date_fin,
                
            })
        emprunt_details_tries = sorted(
            emprunt_details,
            key=lambda x: x['date_debut'],  # On extrait la clé 'date' pour le tri
            reverse=True
        )
        return render(request, 'Utilisateur/mes_emprunts.html', {'emprunts': emprunt_details_tries})

class MesAchats(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        # Récupérer les emprunts de l'utilisateur
        achats = Commande.objects.filter(user=request.user).order_by('-id')[:5]
        
        if not achats.exists():
            messages.info(request, "Vous n'avez aucun achats en cours.")
            return render(request, 'Utilisateur/mes_achats.html', {'achats': []})

        # Préparer les données pour le template
        achat_details = []
        for achat in achats:
            achat_details.append({
                'mail':achat.user.email,
                'nom':achat.user.nom,
                'prenom':achat.user.prenom,
                'titre':achat.titre,
                'date_Commande': achat.date_commande,
                'montant_total': achat.montant_total,
                'quantite':achat.quantite
            })
        return render(request, 'Utilisateur/mes_achats.html', {'achats': achat_details})

def user_profile(request, user_id):
    return render(request, 'Utilisateur/Profil_Utilisateur.html', {
        'utilisateur': get_object_or_404(Utilisateur, id=user_id)
    })

class Meslivres(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        # Récupérer les emprunts de l'utilisateur
        achats = Achats.objects.filter(user=request.user)  

        if not achats.exists():
            messages.info(request, "Vous n'avez aucun achats en cours.")
            return render(request, 'Utilisateur/mes_achats.html', {'achats': []})

        # Préparer les données pour le template
        achat_details = []
        for achat in achats:
            achat_details.append({
                'titre':achat.livre.titre,
                'auteur':achat.livre.auteur,
                'url':achat.livre.download_url,
                'image':achat.livre.image_url
            })

        return render(request, 'Utilisateur/mes_livres.html', {'mes_livres': achat_details})

from django.utils import timezone

@login_required
def Emprunts(request):
    emprunts = Emprunt.objects.select_related('user', 'livre').all().order_by('-date_debut')

    # Configurer la pagination (par exemple, 10 éléments par page)
    paginator = Paginator(emprunts, 10)
    page_number = request.GET.get('page')  # Récupère le numéro de page depuis l'URL
    page_obj = paginator.get_page(page_number)
    
    aujourdhui = timezone.now()  # Date et heure actuelles (avec timezone)
    print(aujourdhui)
    print(Emprunt.objects.filter(date_fin__lte=aujourdhui).count())
    return render(request, 'Administrateur/Emprunts.html', {
        'emprunts': page_obj,
        'aujourdhui': timezone.now(),
        'nbrEmpC': Emprunt.objects.filter(date_debut__lte=aujourdhui, date_fin__gt=aujourdhui).count(),
        'nbrEmpT': Emprunt.objects.filter(date_fin__lte=aujourdhui).count(),

        # 'nbrEmpC':Emprunt.objects.filter(date_debut__gt=aujourdhui).count(),
        # 'nbrEmpT': Emprunt.objects.filter(date_fin__lte=aujourdhui).count(),
    })

@login_required
def liste_achats(request):
    achats_list = Achats.objects.select_related('user', 'livre').all().order_by('-date')
    
    # Configurer la pagination (par exemple, 10 éléments par page)
    paginator = Paginator(achats_list, 10)
    page_number = request.GET.get('page')  # Récupère le numéro de page depuis l'URL
    page_obj = paginator.get_page(page_number)

    return render(request, 'Administrateur/Achats.html', {
        'achats': page_obj,
        'aujourdhui': timezone.now(),
        'nbrAchats' : Achats.objects.count()

    })

class PasswordResetRequestView(View):
    def get(self, request):
        return render(request, 'Utilisateur/password_reset_request.html')
    
    def post(self, request):
        email = request.POST.get('email')
        
        # Vérifier si l'email existe
        try:
            user = Utilisateur.objects.get(email=email)
        except Utilisateur.DoesNotExist:
            messages.error(request, "Aucun compte trouvé avec cet email.")
            return render(request, 'Utilisateur/password_reset_request.html')
        
        # Générer un code de vérification (6 chiffres)
        verification_code = str(random.randint(1000, 9999))
        
        # Stocker le code dans le cache (valide 15 minutes)
        cache.set(f'password_reset_{email}', verification_code, 120)
        
        # Envoyer l'email
        subject = "Réinitialisation de votre mot de passe"
        message = f"""
        Bonjour,
        
        Vous avez demandé à réinitialiser votre mot de passe. 
        Voici votre code de vérification :
        
        {verification_code}
        
        Ce code est valable pendant 2 minutes.
        
        Si vous n'avez pas fait cette demande, veuillez ignorer cet email.
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        
        # Stocker l'email en session pour les étapes suivantes
        request.session['reset_email'] = email
        
        messages.success(request, "Un code de vérification a été envoyé à votre adresse email.")
        return redirect('verify_reset_code')

class PasswordResetCodeVerifyView(View):
    def get(self, request):
        if 'reset_email' not in request.session:
            return redirect('password_reset_request')
        return render(request, 'Utilisateur/verify_reset_code.html')
    
    def post(self, request):
        email = request.session.get('reset_email')
        user_code = request.POST.get('verification_code')
        cached_code = cache.get(f'password_reset_{email}')
        
        if not cached_code or cached_code != user_code:
            messages.error(request, "Code invalide ou expiré.")
            return render(request, 'Utilisateur/verify_reset_code.html')
        
        # Code valide, passer à l'étape de confirmation
        return redirect('password_reset_confirm')

class PasswordResetConfirmView(View):
    def get(self, request):
        if 'reset_email' not in request.session:
            return redirect('password_reset_request')
        return render(request, 'Utilisateur/password_reset_confirm.html')
    
    def post(self, request):
        email = request.session.get('reset_email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password != confirm_password:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return render(request, 'Utilisateur/password_reset_confirm.html')
        
        try:
            user = Utilisateur.objects.get(email=email)
            user.password = make_password(password)
            user.save()
            
            # Nettoyer la session et le cache
            del request.session['reset_email']
            cache.delete(f'password_reset_{email}')
            
            messages.success(request, "Votre mot de passe a été réinitialisé avec succès. Vous pouvez maintenant vous connecter.")
            return redirect('login')
        except Utilisateur.DoesNotExist:
            messages.error(request, "Une erreur est survenue. Veuillez réessayer.")
            return redirect('password_reset_request')