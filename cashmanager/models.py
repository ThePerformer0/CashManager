from django.db import models
from django.contrib.auth.models import AbstractUser


class Site(models.Model):
    nom = models.CharField(max_length=30, default="Megatim")
    pays = models.CharField(max_length=30)
    ville = models.CharField(max_length=30)

    def __str__(self):
        return f"Site {self.nom} : {self.pays} dans la ville de {self.ville}"


class Caisse(models.Model):
    nom = models.CharField(max_length=20)
    solde = models.DecimalField(max_digits=100, decimal_places=2)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)

    def __str__(self) :
        return f"Ciasse de {self.site.nom} - pays : {self.site.pays} - ville : {self.site.ville}"
    

class Utilisateur(AbstractUser):
    site = models.ForeignKey(Site, on_delete=models.DO_NOTHING, default="1")
    role = models.CharField(max_length=30, default="directeur")

    def __str__(self):
        return self.username
    

class Employe(models.Model):
    added_by = models.ForeignKey(Utilisateur, on_delete=models.DO_NOTHING, related_name="superviseur", default="0")
    nom = models.CharField(max_length=100, default='jean')
    email = models.EmailField(max_length=100, default='nom@gmail.com')
    role = models.CharField(max_length=100, default='développeur')
    site = models.ForeignKey(Site, on_delete=models.CASCADE, default='1')


    def __str__(self):
        return self.nom


class Approvisionnement(models.Model):
    numero = models.IntegerField()
    make_by = models.ForeignKey(Utilisateur, on_delete=models.DO_NOTHING)
    montant = models.DecimalField(max_digits=30, decimal_places=2)
    motif = models.TextField(max_length=255)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Approvisionnement N°{self.numero} d'un montant de {self.montant} à la date : {self.date}"


class Retrait(models.Model):
    numero = models.IntegerField()
    make_by = models.ForeignKey(Utilisateur, on_delete=models.DO_NOTHING)
    beneficiaire = models.ForeignKey(Employe, on_delete=models.DO_NOTHING)
    montant = models.DecimalField(max_digits=30, decimal_places=2)
    motif = models.TextField(max_length=255)
    date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"Retrait N°{self.numero} d'un montant de {self.montant} à la date : {self.date}"
    
class PieceJustificative(models.Model):
    retrait = models.ForeignKey(Retrait, on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    fichier = models.FileField(upload_to='pieces_justificatives/')
    date_ajoutee = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.description} pour {self.retrait.numero}"


