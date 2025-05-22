from django.urls import path, include
from . import views
from .views import (
    PasswordResetRequestView, 
    PasswordResetConfirmView,
    PasswordResetCodeVerifyView
)

urlpatterns = [
    # Landing page
    path('', views.LandingPage.as_view(), name='landing'),
    
    # Authentication URLs
    path('login/', views.LoginPage.as_view(), name='login'),
    path('register/', views.afficherform, name='register'),
    path('valider/', views.register, name='valider'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    # User Authentication
    path('home/', views.AuthUtilisateur.as_view(), name='home_user'),
    path('adm/login/', views.LoginPage.as_view(), name='admin_login'),
    path('home/adm', views.AuthAdmin.as_view(), name='home_admin'),

    path('adm/<int:admin_id>/', views.admin_profile, name='admin_profile'),
    path('modification_Admin/', views.profile_Admin_view, name='modification_Admin_profile'),

    path('utilisateurs/', views.liste_utilisateurs, name='liste_utilisateurs'),
    path('utilisateurs/tri', views.Tri_utilisateurs, name='Tri_utilisateurs'),
    path('utilisateurs/<int:user_id>/', views.details_utilisateur, name='details_utilisateur'),

    path('livres/', views.liste_livres, name='liste_livres'),
    path('livres/<int:id>/', views.detail_livre, name='Detaillivre'),
    path('livres/ajouter/', views.ajouter_livre, name='ajouter_livre'),
    path('livres/<int:pk>/modifier/', views.modifier_livre, name='modifier_livre'),
    path('livres/<int:pk>/supprimer/', views.supprimer_livre, name='supprimer_livre'),
    path('livres/tri', views.livres_par_categorie, name='livres'),
    path('recherche/', views.rechercher_livres, name='rechercher_livres'),
    path('livres/dispo', views.livres_disponibilite, name='livres_dispo'),
    
 
    path('modification_User/', views.profile_User_view, name='modification_User_profile'),

    # # Livres
    path('Livres/', views.ListeLivres.as_view(), name='ListeLivres'),
    path('livre/<int:livre_id>/', views.DetailLivre.as_view(), name='detail_livre'),

    #Favoris
    path('ajouter_favoris/<int:livre_id>/', views.AjouterAuxFavoris.as_view(), name='ajouter_favoris'),
    path('supprimer_favoris/<int:livre_id>/', views.SupprimerDesFavoris.as_view(), name='supprimer_des_favoris'),
    path('favoris/', views.AfficherFavoris.as_view(), name='favoris'),

    # Panier
    path('ajouter-au-panier/<int:livre_id>/', views.AjouterAuPanier.as_view(), name='ajouter_au_panier'),
    path('panier/', views.AfficherPanier.as_view(), name='panier'),
    path('supprimer-du-panier/<int:livre_id>/', views.SupprimerDuPanier.as_view(), name='supprimer_du_panier'),
    path('valider-panier/', views.ValiderPanier.as_view(), name='valider_panier'),

    path('acheter-panier/', views.AcheterPanier.as_view(), name='acheter_panier'),
    path('emprunter-panier/', views.EmprunterPanier.as_view(), name='emprunter_panier'),

    path('confirmation-achat/<int:commande_id>/', views.confirmation_achat, name='confirmation_achat'),
    path('confirmation-emprunt/<int:emprunt_id>/', views.confirmation_emprunt, name='confirmation_emprunt'),

    path('mes-emprunts/', views.MesEmprunts.as_view(), name='mes_emprunts'),
    path('mes-achats/', views.MesAchats.as_view(), name='mes_achats'),
    path('mes-livres/', views.Meslivres.as_view(), name='mes_livres'),

    #Categories
    path('genres/', views.CategoriesView.as_view(), name='genres'),
    path('genres/<str:genre>/', views.LivresParGenre.as_view(), name='livres_par_genre'),

    path('user/<int:user_id>/', views.user_profile, name='user_profile'),
    path('Emprunts/', views.Emprunts, name='Emprunts'),
    path('Achats/', views.liste_achats, name='Achats'),
      
    # urls.py
    path('users/<int:user_id>/deactivate/', views.user_deactivate, name='user_deactivate'),
    path('warn-user/<int:user_id>/', views.Warn_email, name='warn_user'),

    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/verify-code/', PasswordResetCodeVerifyView.as_view(), name='verify_reset_code'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    
    path('password-reset-admin/<int:admin_id>/', views.PasswordResetAdmin.as_view(), name='password_reset_admin'),
]
