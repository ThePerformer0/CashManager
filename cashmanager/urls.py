from django.urls import path
from . import views

app_name = 'cashmanager'

urlpatterns = [
    path('', views.landing, name='landing'),
    path('home/', views.index, name='index'),
    path('connection/', views.connection, name='connection'),
    path('deconnection/', views.deconnection, name='deconnection'),
    path('retrait_caisse/', views.retrait_caisse, name='creer_retrait'),
    path('approvisionner_caisse/', views.approvisionnement_caisse, name='approvisionner_caisse'),
    path('retrait/<int:retrait_id>/', views.get_retrait_details, name='get_retrait_details'),
    path('approvisionnement/<int:approvisionnement_id>/', views.get_approvisionnement_details, name='get_approvisionnement_details'),
    path('ajouter_employe/', views.ajouter_employe, name='ajouter_employe'),
    path('bilan_transaction/', views.bilan_transaction, name='bilan_transaction'),
    path('ajouter-justificatif/', views.ajouter_justificatif, name='ajouter_justificatif'),
    path('print_retrait/<int:retrait_id>/', views.print_retrait, name='print_retrait'),
]