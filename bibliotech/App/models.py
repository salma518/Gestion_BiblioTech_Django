from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Group,Permission

class Utilisateur(AbstractBaseUser, PermissionsMixin):
    cin = models.CharField(max_length=20, unique=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    numeroTelephone = models.CharField(max_length=20)
    email = models.EmailField(max_length=191)               
    adresse = models.CharField(max_length=255)
    password = models.CharField(max_length=128)
    solde = models.DecimalField(max_digits=10, decimal_places=2) 
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    compte_actif = models.BooleanField(default=True)

    REQUIRED_FIELDS = ['nom', 'prenom', 'numeroTelephone', 'cin']
    USERNAME_FIELD ='email'

    groups = models.ManyToManyField(
        Group,
        related_name='utilisateur_set',
        blank=True,
        help_text='The groups this utilisateur belongs to.',
        related_query_name='utilisateur',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='utilisateur_permissions',
        blank=True,
        help_text='Specific permissions for this utilisateur.',
        related_query_name='utilisateur',
    )
     # Adjust as needed

class Admin(AbstractBaseUser, PermissionsMixin):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    numeroTelephone = models.CharField(max_length=20)
    email = models.EmailField(max_length=191)               
    adresse = models.CharField(max_length=255)
    cin = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)

    REQUIRED_FIELDS = ['nom', 'prenom', 'numeroTelephone', 'cin']
    USERNAME_FIELD = 'email'

    groups = models.ManyToManyField(
        Group,
        related_name='admin_set',
        blank=True,
        help_text='The groups this admin belongs to.',
        related_query_name='admin',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='admin_permissions',
        blank=True,
        help_text='Specific permissions for this admin.',
        related_query_name='admin',
    )

class Commande(models.Model):
    user = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='commandes')
    titre = models.CharField(max_length=100)
    quantite = models.PositiveIntegerField(default=0) 
    date_commande = models.DateField()           
    montant_total = models.DecimalField(max_digits=10, decimal_places=2)

class Facture(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='factures')
    date_facture = models.DateField()
    montant = models.DecimalField(max_digits=10, decimal_places=2)

class Livre(models.Model):
    titre = models.CharField(max_length=100)  # Correspond à title
    auteur = models.TextField(max_length=255)  # Correspond à authors (concaténation des noms)
    date_pub = models.DateField(null=True, blank=True)  # Correspond à une date de publication (non précisée dans l'API)
    genre = models.CharField(max_length=255, blank=True)  # Peut correspondre à subjects ou bookshelves
    detail = models.TextField()  # Correspond à summaries
    prix = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Pas d'équivalent dans l'API
    image_url = models.URLField(max_length=500, blank=True)  # Correspond à image/jpeg (URL de l'image)
    download_url = models.URLField(max_length=500, blank=True) 
    quantite = models.PositiveIntegerField(default=0)  # Ajouté pour l'URL de téléchargement
          

class Emprunt(models.Model):
    user = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='emprunts')
    livre = models.ForeignKey(Livre, on_delete=models.CASCADE, related_name='emprunts')
    duree_emprunt = models.DecimalField(max_digits=10, decimal_places=2)  
    date_debut = models.DateTimeField(default=timezone.now())        
    date_fin = models.DateTimeField(default=timezone.now())

class Achats(models.Model):
    user = models.ForeignKey('Utilisateur', on_delete=models.CASCADE,related_name='achats')
    livre = models.ForeignKey('Livre', on_delete=models.CASCADE,related_name='achats')
    date = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    quantite = models.PositiveIntegerField(default=0) 

class Panier(models.Model):
    user = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='paniers')
    livre = models.ForeignKey(Livre, on_delete=models.CASCADE, related_name='paniers')
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    quantite = models.PositiveIntegerField(default=0) 

class Favoris(models.Model):
    user = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='favoris')
    livre = models.ForeignKey(Livre, on_delete=models.CASCADE, related_name='favoris')

