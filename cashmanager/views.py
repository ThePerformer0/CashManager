import os
from textwrap import wrap
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import redirect, render, get_object_or_404


from .forms import PieceJustificativeForm

from .models import *
from django.contrib import messages



def landing(request):
    return render(request, 'cashmanager/landing.html')

def connection(request):
    if request.method == 'POST':
        nom = request.POST['nom']
        password = request.POST['password']

        user = authenticate(request, username=nom, password=password)

        if user is not None:
            login(request, user)
            return redirect('cashmanager:index')
        else:
            error_message = "Nom d'utilisateur ou mot de passe incorrect."
            return render(request, 'cashmanager/connection.html', {'error_message': error_message})
    else:
        return render(request, 'cashmanager/connection.html')


@login_required
def deconnection(request):
    logout(request)
    return redirect('cashmanager:landing')


@login_required
def index(request):
    today = timezone.now().date()
    today_add_count = Approvisionnement.objects.filter(date=today).count()
    today_retrait_count = Retrait.objects.filter(date=today).count()
    
    # Récupérer les 5 derniers approvisionnements
    last_approvisionnements = Approvisionnement.objects.order_by('-date')[:10]

    # Récupérer les 5 derniers retraits
    last_retraits = Retrait.objects.order_by('-date')[:10]

    # Récupérer la caisse de l'utilisateur connecté
    user_site = request.user.site
    user_caisse = Caisse.objects.get(site=user_site)
    user_caisse_solde = user_caisse.solde

    context = {
        'today_add_count': today_add_count,
        'today_retrait_count': today_retrait_count,
        'today_approvisionnement_list': last_approvisionnements,
        'today_retrait_list': last_retraits,
        'user_caisse_name': user_caisse.nom,
        'user_caisse_solde': user_caisse_solde
    }

    return render(request, 'cashmanager/index.html', context)


from django.db.models import F

def retrait_caisse(request):
    if request.method == 'POST':
        beneficiaire_id = request.POST.get('beneficiaire')
        montant = request.POST.get('montant')
        motif = request.POST.get('motif')

        today = datetime.now().date()
        # Récupérer le dernier numéro de retrait de la journée
        today_retraits = Retrait.objects.filter(date=today).order_by('-numero')
        if today_retraits:
            nouveau_numero = today_retraits.first().numero + 1
        else:
            nouveau_numero = 1

        # Récupérer la caisse du site de l'utilisateur connecté
        caisse = Caisse.objects.get(site=request.user.site)

        # Vérifier que le solde de la caisse est suffisant
        if caisse.solde >= float(montant):
            # Créer le nouveau retrait
            retrait = Retrait.objects.create(
                numero=nouveau_numero,
                make_by=request.user,
                beneficiaire_id=beneficiaire_id,
                montant=montant,
                motif=motif,
            )

            # Déduire le montant de la caisse
            caisse.solde = F('solde') - float(montant)
            caisse.save()

            return redirect('cashmanager:index')
        else:
            context = {
                'error_message': "Le solde de la caisse est insuffisant pour effectuer ce retrait.",
                'employes': Employe.objects.all()
            }
            return render(request, 'cashmanager/creer_retrait.html', context)

    employes = Employe.objects.all()
    return render(request, 'cashmanager/creer_retrait.html', {'employes': employes})


def approvisionnement_caisse(request):
    if request.method == 'POST':
        montant = request.POST.get('montant')
        motif = request.POST.get('motif')

        today = datetime.now().date()
        # Récupérer le dernier numéro de retrait de la journée
        today_approvisionnement = Approvisionnement.objects.filter(date=today).order_by('-numero')
        if today_approvisionnement:
            nouveau_numero = today_approvisionnement.first().numero + 1
        else:
            nouveau_numero = 1

        # Récupérer la caisse du site de l'utilisateur connecté
        caisse = Caisse.objects.get(site=request.user.site)
        # Vérifier que le solde de la caisse est suffisant
        if caisse:
            # Créer le nouveau retrait
            approvisionnement = Approvisionnement.objects.create(
                numero=nouveau_numero,
                make_by=request.user,
                montant=montant,
                motif=motif,
            )

            # Ajouter le montant de la caisse
            caisse.solde = F('solde') + float(montant)
            caisse.save()

            return redirect('cashmanager:index')
        else:
            context = {'envoyeurs': Utilisateur.objects.all()}
            return render(request, 'cashmanager/creer_approvisionnement.html', context)

    return render(request, 'cashmanager/creer_approvisionnement.html', {'envoyeurs': Utilisateur.objects.all()})


@login_required
def get_retrait_details(request, retrait_id):
    retrait = get_object_or_404(Retrait, id=retrait_id)
    context = {
        'retrait': retrait
    }
    return render(request, 'cashmanager/bon_details.html', context)

@login_required 
def get_approvisionnement_details(request, approvisionnement_id):
    approvisionnement = get_object_or_404(Approvisionnement, id=approvisionnement_id)
    context = {
        'approvisionnement': approvisionnement
    }
    return render(request, 'cashmanager/approvisionnement_details.html', context)


def ajouter_employe(request):
    if request.method == 'POST':
        nom = request.POST.get('nom')
        email = request.POST.get('email')
        role = request.POST.get('poste')

        employe = Employe.objects.create(
            added_by=request.user,
            nom=nom,
            email=email,
            role=role,
            site=request.user.site
        )
        employe.save()
        return redirect('cashmanager:index')
    
    return render(request, 'cashmanager/ajouter_employe.html')


from datetime import datetime
def bilan_transaction(request):
    if request.method == 'POST':
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        bilan_type = request.POST['bilan_type']
        jour = request.POST['jour']
        transaction_type = request.POST['transaction_type']

        date_debut = start_date
        date_fin = end_date
        day = jour

        if bilan_type == 'journée' :
            date_debut = day
            date_fin = day

        date_debut = datetime.strptime(date_debut, '%Y-%m-%d').date()
        date_fin = datetime.strptime(date_fin, '%Y-%m-%d').date()

        if date_debut > date_fin:
            temp = date_debut
            date_debut = date_fin
            date_fin = temp
        
        # Filtre les transactions en fonction du type sélectionné
        if transaction_type == 'retrait':
            # Récupère les transactions de retrait dans la période sélectionnée
            transactions = Retrait.objects.filter(date__range=[date_debut, date_fin])
            # Calcule le montant total des retraits

            total_amount = 0
            for transaction in transactions:
                total_amount += transaction.montant
            
            if not transactions:
                context = {
                    'jour': jour,
                    'start_date': start_date,
                    'end_date': end_date,
                    'error_message': 'Aucune transaction trouvée pour la période sélectionnée.',
                }
            else:
                context = {
                    'jour': jour,
                    'start_date': start_date,
                    'end_date': end_date,
                    'transactions': transactions,
                    'total_amount': total_amount,
                    'transaction_type': 'Retrait',
                }
        elif transaction_type == 'approvisionnement':
            # Récupère les transactions d'approvisionnement dans la période sélectionnée
            transactions = Approvisionnement.objects.filter(date__range=[date_debut, date_fin])
            # Calcule le montant total des approvisionnements
            total_amount = 0
            for transaction in transactions:
                total_amount += transaction.montant
            
            if not transactions:
                context = {
                    'jour': jour,
                    'start_date': start_date,
                    'end_date': end_date,
                    'error_message': 'Aucune transaction trouvée pour la période sélectionnée.',
                }
            else:
                context = {
                    'jour': jour,
                    'start_date': date_debut,
                    'end_date': date_fin,
                    'transactions': transactions,
                    'total_amount': total_amount,
                    'transaction_type': 'Approvisionnement',
                }
        else:
            # Récupère les transactions de retrait dans la période sélectionnée
            retrait_transactions = Retrait.objects.filter(date__range=[date_debut, date_fin])
                
            # Calcule le montant total des retraits
            retrait_total_amount = 0
            for retrait in retrait_transactions:
                retrait_total_amount += retrait.montant

            # Récupère les transactions d'approvisionnement dans la période sélectionnée
            approvisionnement_transactions = Approvisionnement.objects.filter(date__range=[date_debut, date_fin])
            # Calcule le montant total des approvisionnements
            approvisionnement_total_amount = 0
            for approvisionnement in approvisionnement_transactions:
                approvisionnement_total_amount += approvisionnement.montant
            
            if not retrait_transactions and not approvisionnement_transactions :
                context = {
                    'jour': jour,
                    'start_date': start_date,
                    'end_date': end_date,
                    'error_message': 'Aucune transaction trouvée pour la période sélectionnée.',
                }
            else:
                context = {
                    'jour': jour,
                    'start_date': date_debut,
                    'end_date': date_fin,
                    'retrait_transactions': retrait_transactions,
                    'retrait_total_amount': retrait_total_amount,
                    'approvisionnement_transactions': approvisionnement_transactions,
                    'approvisionnement_total_amount': approvisionnement_total_amount,
                    'transaction_type': 'Retrait et Approvisionnement',
                }

        return render(request, 'cashmanager/transaction_bilan.html', context)

    return render(request, 'cashmanager/transaction_bilan.html')


def ajouter_justificatif(request):
    if request.method == 'POST':
        retrait_id = request.POST.get('retrait_id')
        retrait = Retrait.objects.get(id=retrait_id)

        form = PieceJustificativeForm(request.POST, request.FILES)  # Inclure request.FILES
        if form.is_valid():
            piece_justificative = form.save(commit=False)
            piece_justificative.retrait = retrait  # Lier la pièce justificative au retrait
            piece_justificative.save()
            messages.success(request, "La pièce justificative a été ajoutée avec succès.")
            return redirect('cashmanager:index')  # Rediriger vers une page appropriée
    else:
        form = PieceJustificativeForm()

    retraits = Retrait.objects.all()  # Récupérer tous les retraits pour le menu déroulant

    context = {
        'form': form,
        'retraits': retraits
    }
    return render(request, 'cashmanager/ajouter_justificatif.html', context)


from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from textwrap import wrap
from num2words import num2words
import os
import io
from django.shortcuts import get_object_or_404
from django.http import FileResponse

def print_retrait(request, retrait_id):
    # Récupérer les détails du retrait à partir de la base de données
    retrait = get_object_or_404(Retrait, id=retrait_id)

    buffer = io.BytesIO()

    # Créer un PDF avec ReportLab
    p = canvas.Canvas(buffer, pagesize=A4)

    # Définir les dimensions de la page
    width, height = A4
    y_position = height - 50  # Position verticale de départ

    # Ajouter une image (en-tête)
    image_name = "top-img.jpg"
    image_path = os.path.join(settings.MEDIA_ROOT, image_name)
    try:
        p.drawImage(image_path, 50, y_position, width=130, height=50)
    except Exception as e:
        print(f"Erreur lors de l'ajout de l'image: {e}")
    y_position -= 70

    # En-tête
    p.setFont("Helvetica", 8)
    p.drawString(100, y_position, f"Ref. : BC/MGT/YDE/____________/N°{retrait.numero}")
    p.setFont("Helvetica", 10)
    p.drawString(400, y_position + 8, f"Yaoundé, le {retrait.date.strftime('%d/%m/%Y')}")
    y_position -= 30

    # Titre
    p.setFont("Helvetica-Bold", 16)
    text = "BON DE CAISSE"
    p.drawString(240, y_position, text)
    text_width = p.stringWidth(text, "Helvetica-Bold", 16)
    p.line(240, y_position - 2, 240 + text_width, y_position - 2)
    y_position -= 50

    # Paramètres pour le texte
    max_width = 400
    text_size = 12
    line_height = 15
    label_size = 14

    # Motif
    p.setFont("Helvetica", label_size)
    p.drawString(100, y_position, "Motif :")
    p.setFont("Helvetica", text_size)
    motif = retrait.motif
    char_width = p.stringWidth("a", "Helvetica", text_size)
    max_chars_per_line = int(max_width / char_width)
    wrapped_text = wrap(motif, max_chars_per_line)

    # Afficher chaque ligne du motif
    y_position -= 20
    for line in wrapped_text:
        p.drawString(120, y_position, line)
        y_position -= line_height
        if y_position < 50:  # Vérifier si on atteint le bas de la page
            p.showPage()
            y_position = height - 50

    # Montant en lettres et en chiffres
    y_position -= 20
    p.drawString(100, y_position, f"Montant en lettre: {num2words(retrait.montant, lang='fr')} Franc CFA")
    y_position -= line_height
    p.drawString(100, y_position, f"Montant en chiffres: {retrait.montant}")
    p.drawString(310, y_position, "F CFA")
    y_position -= 40

    # Signatures
    t1 = "Bénéficiaire"
    t2 = "Responsable"
    t3 = "Direction"
    p.drawString(100, y_position, t1)
    p.line(100, y_position - 2, 100 + p.stringWidth(t1, "Helvetica", 12), y_position - 2)
    p.drawString(290, y_position, t2)
    p.line(290, y_position - 2, 290 + p.stringWidth(t2, "Helvetica", 12), y_position - 2)
    p.drawString(480, y_position, t3)
    p.line(480, y_position - 2, 480 + p.stringWidth(t3, "Helvetica", 12), y_position - 2)
    y_position -= 50

    # Image (pied de page)
    image_name = "bottom-img.jpg"
    image_path = os.path.join(settings.MEDIA_ROOT, image_name)
    try:
        if y_position > 70:
            p.drawImage(image_path, 50, y_position - 70, width=500, height=70)
        else:
            p.showPage()
            y_position = height - 70
            p.drawImage(image_path, 50, y_position, width=500, height=70)
    except Exception as e:
        print(f"Erreur lors de l'ajout de l'image: {e}")

    # Finaliser le PDF
    p.showPage()
    p.save()

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f"bon_de_caisse_{retrait.numero}.pdf")
