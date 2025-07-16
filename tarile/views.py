from django.shortcuts import render, get_object_or_404, redirect
from .models import Tara, Produs, Cos, CosItem, Comanda, ComandaItem, ConfigurareTransport
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.urls import reverse
from .forms import CheckoutForm
import json
from decimal import Decimal
from datetime import datetime, timedelta


def welcome_page(request):
    return render(request, 'tarile/welcome.html')


def lista_tari(request):
    tari = Tara.objects.all()
    return render(request, 'tarile/lista_tari.html', {'tari': tari})


def detalii_tara(request, tara_id):
    tara = get_object_or_404(Tara, id=tara_id)
    return render(request, 'tarile/detalii_tara.html', {'tara': tara})


def cauta_tara(request):
    query = request.GET.get('q', '')
   
    if query:
        rezultate = Tara.objects.filter(nume__icontains=query)
       
        if rezultate.count() == 1:
            return redirect('detalii_tara', rezultate.first().id)
       
        if rezultate.exists():
            return render(request, 'tarile/lista_tari.html', {'tari': rezultate, 'query': query})
       
    tari = Tara.objects.all()
    return render(request, 'tarile/lista_tari.html', {'tari': tari})


def lista_produse(request):
    produse = Produs.objects.filter(in_stoc=True).order_by('-data_adaugare')
    categorii = Produs.objects.values_list('categorie', flat=True).distinct()
    
    for produs in produse:
        if produs.pret_redus and produs.pret_redus < produs.pret:
            produs.discount_percent = int(((produs.pret - produs.pret_redus) / produs.pret) * 100)
        else:
            produs.discount_percent = 0
   
    # Filtru după categorie
    categorie_selectata = request.GET.get('categorie')
    if categorie_selectata:
        produse = produse.filter(categorie=categorie_selectata)
   
    # Sortare
    sortare = request.GET.get('sortare')
    if sortare == 'pret_asc':
        produse = produse.order_by('pret')
    elif sortare == 'pret_desc':
        produse = produse.order_by('-pret')
    elif sortare == 'rating':
        produse = produse.order_by('-rating')
    elif sortare == 'nume':
        produse = produse.order_by('nume')
   
    return render(request, 'tarile/lista_produse.html', {
        'produse': produse,
        'categorii': categorii,
        'categorie_selectata': categorie_selectata,
        'sortare': sortare
    })


def detalii_produs(request, produs_id):
    produs = get_object_or_404(Produs, id=produs_id)
   
    # Calculăm discount_percent pentru produs
    if produs.pret_redus and produs.pret_redus < produs.pret:
        produs.discount_percent = int(((produs.pret - produs.pret_redus) / produs.pret) * 100)
    else:
        produs.discount_percent = 0
   
    # Produse similare din aceeași categorie
    produse_similare = Produs.objects.filter(
        categorie=produs.categorie,
        in_stoc=True
    ).exclude(id=produs.id)[:4]
   
    # Calculăm discount pentru produse similare
    for prod in produse_similare:
        if prod.pret_redus and prod.pret_redus < prod.pret:
            prod.discount_percent = int(((prod.pret - prod.pret_redus) / prod.pret) * 100)
        else:
            prod.discount_percent = 0
   
    context = {
        'produs': produs,
        'produse_similare': produse_similare
    }
   
    return render(request, 'tarile/detalii_produs.html', context)


def get_or_create_cos(request):
    """Helper function pentru a obține sau crea coșul utilizatorului"""
    if request.user.is_authenticated:
        cos, created = Cos.objects.get_or_create(user=request.user)
    else:
        # Pentru utilizatori neautentificați, folosim session
        if not request.session.session_key:
            request.session.create()
        cos, created = Cos.objects.get_or_create(session_key=request.session.session_key)
    return cos


@require_POST
def adauga_in_cos(request, produs_id):
    """Adaugă produs în coș și redirecționează către coș"""
    produs = get_object_or_404(Produs, id=produs_id)
   
    if not produs.in_stoc:
        messages.error(request, 'Produsul nu este în stoc')
        return redirect('detalii_produs', produs_id=produs_id)
   
    cantitate = int(request.POST.get('cantitate', 1))
   
    # Validare cantitate
    if cantitate < 1 or cantitate > 10:
        messages.error(request, 'Cantitatea trebuie să fie între 1 și 10')
        return redirect('detalii_produs', produs_id=produs_id)
   
    cos = get_or_create_cos(request)
   
    # Verifică dacă produsul există deja în coș
    cos_item, created = CosItem.objects.get_or_create(
        cos=cos,
        produs=produs,
        defaults={'cantitate': cantitate}
    )
   
    if not created:
        # Produsul există deja, actualizează cantitatea
        cos_item.cantitate = min(cos_item.cantitate + cantitate, 10)
        cos_item.save()
        messages.success(request, f"Cantitatea pentru {produs.nume} a fost actualizată în coș")
    else:
        messages.success(request, f"{produs.nume} a fost adăugat în coș")
   
    # Redirecționează către pagina coșului
    return redirect('vezi_cos')


def vezi_cos(request):
    """Afișează conținutul coșului"""
    cos = get_or_create_cos(request)
    items = cos.items.select_related('produs').all()
    
    # Calculează cât mai trebuie pentru transport gratuit
    remaining = max(0, 100 - float(cos.total_pret))
   
    context = {
        'cos': cos,
        'items': items,
        'remaining_for_free_shipping': remaining,
    }
    return render(request, 'tarile/cos.html', context)


@require_POST
def actualizeaza_cos(request):
    """Actualizează cantitățile din coș"""
    cos = get_or_create_cos(request)
   
    for key, value in request.POST.items():
        if key.startswith('cantitate_'):
            item_id = int(key.replace('cantitate_', ''))
            cantitate = int(value)
           
            if cantitate <= 0:
                # Șterge itemul dacă cantitatea este 0
                CosItem.objects.filter(id=item_id, cos=cos).delete()
            else:
                # Actualizează cantitatea
                CosItem.objects.filter(id=item_id, cos=cos).update(
                    cantitate=min(cantitate, 10)
                )
   
    messages.success(request, 'Coșul a fost actualizat')
    return redirect('vezi_cos')


@require_POST
def sterge_din_cos(request, item_id):
    """Șterge un item din coș"""
    cos = get_or_create_cos(request)
    item = get_object_or_404(CosItem, id=item_id, cos=cos)
    nume_produs = item.produs.nume
    item.delete()
   
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'{nume_produs} a fost eliminat din coș',
            'cos_count': cos.total_produse,
            'cos_total': float(cos.total_pret)
        })
   
    messages.success(request, f'{nume_produs} a fost eliminat din coș')
    return redirect('vezi_cos')


def checkout(request):
    """View pentru checkout"""
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Obține coșul
            cos = get_or_create_cos(request)
            
            # Verifică dacă coșul nu este gol
            if not cos.items.exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Coșul este gol.'
                })
            
            # Creează comanda FĂRĂ să golească coșul încă
            try:
                comanda = creeaza_comanda_temporara(request, cos, form)
                
                # Redirecționează către pagina de plată
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'redirect_url': reverse('pagina_plata', args=[comanda.id])
                    })
                else:
                    return redirect('pagina_plata', comanda_id=comanda.id)
                    
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'message': f'A apărut o eroare: {str(e)}'
                })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Datele introduse nu sunt valide.',
                'errors': form.errors
            })
   
    # GET request - afișează formularul
    items = get_cart_items(request)
    
    if not items:
        messages.warning(request, 'Coșul este gol.')
        return redirect('vezi_cos')
    
    # Calculează totalurile
    cos = get_or_create_cos(request)
    subtotal = cos.total_pret
    cost_livrare = cos.cost_transport
    total = cos.total_cu_transport
   
    context = {
        'form': CheckoutForm(),
        'items': items,
        'subtotal': subtotal,
        'cost_livrare': cost_livrare,
        'total': total
    }
    return render(request, 'tarile/checkout.html', context)


def get_cart_items(request):
    """Helper function pentru a obține itemii din coș"""
    cos = get_or_create_cos(request)
    return cos.items.select_related('produs').all()


@transaction.atomic
def creeaza_comanda_temporara(request, cos, form):
    """Creează comanda în status 'in_asteptare' fără să golească coșul"""
   
    # Calculează totalurile
    items = cos.items.all()
    subtotal = cos.total_pret
    
    # Calculează costul de transport
    cost_transport = cos.cost_transport
    
    # Adaugă taxa pentru ramburs dacă este cazul
    if form.cleaned_data['metoda_plata'] == 'ramburs':
        cost_transport += 5
    
    total = subtotal + cost_transport
    
    # Calculează data estimată de livrare
    config = ConfigurareTransport.objects.first()
    zile_livrare = config.zile_livrare_standard if config else 3
    data_livrare_estimata = datetime.now().date() + timedelta(days=zile_livrare)
   
    # Creează comanda în status 'in_asteptare'
    comanda = Comanda.objects.create(
        user=request.user if request.user.is_authenticated else None,
        email=form.cleaned_data['email'],
        telefon=form.cleaned_data['telefon'],
        nume_complet=form.cleaned_data['nume_complet'],
        adresa=form.cleaned_data['adresa'],
        oras=form.cleaned_data['oras'],
        judet=form.cleaned_data['judet'],
        cod_postal=form.cleaned_data['cod_postal'],
        observatii_livrare=form.cleaned_data.get('observatii_livrare', ''),
        metoda_plata=form.cleaned_data['metoda_plata'],
        subtotal=subtotal,
        cost_transport=cost_transport,
        total=total,
        status='in_asteptare',  # Status temporar
        data_livrare_estimata=data_livrare_estimata
    )
   
    # Creează itemii comenzii
    for cos_item in items:
        ComandaItem.objects.create(
            comanda=comanda,
            nume_produs=cos_item.produs.nume,
            pret_unitar=cos_item.pret_unitar,
            cantitate=cos_item.cantitate,
            total_pret=cos_item.total_pret,
            produs=cos_item.produs
        )
   
    # NU șterge coșul încă - o vom face după plată
    
    return comanda


def pagina_plata(request, comanda_id):
    """Pagina pentru introducerea datelor de plată"""
    comanda = get_object_or_404(Comanda, id=comanda_id)
    
    # Verifică dacă utilizatorul are dreptul să vadă această comandă
    if request.user.is_authenticated and comanda.user != request.user:
        messages.error(request, 'Nu aveți permisiunea să accesați această pagină')
        return redirect('lista_tari')
    
    # Dacă comanda este deja confirmată, redirecționează
    if comanda.status == 'confirmed':
        return redirect('confirmare_comanda', comanda_id=comanda.id)
    
    context = {
        'comanda': comanda,
    }
    
    return render(request, 'tarile/pagina_plata.html', context)


@require_POST
def proceseaza_plata(request, comanda_id):
    """Procesează plata și confirmă comanda"""
    comanda = get_object_or_404(Comanda, id=comanda_id)
    
    # Verifică dacă utilizatorul are dreptul să proceseze această comandă
    if request.user.is_authenticated and comanda.user != request.user:
        return JsonResponse({
            'success': False,
            'message': 'Nu aveți permisiunea să procesați această comandă'
        })
    
    if comanda.metoda_plata == 'card':
        # Procesează plata cu cardul
        numar_card = request.POST.get('numar_card', '').replace(' ', '')
        data_expirare = request.POST.get('data_expirare', '')
        cvv = request.POST.get('cvv', '')
        nume_card = request.POST.get('nume_card', '')
        
        # Validări simple
        if len(numar_card) < 16:
            return JsonResponse({
                'success': False,
                'message': 'Numărul cardului trebuie să aibă cel puțin 16 cifre'
            })
        
        if len(cvv) != 3:
            return JsonResponse({
                'success': False,
                'message': 'CVV-ul trebuie să aibă 3 cifre'
            })
        
        if not nume_card.strip():
            return JsonResponse({
                'success': False,
                'message': 'Numele de pe card este obligatoriu'
            })
        
        # Simulare procesare plată (în realitate aici ai integra cu un processor de plăți)
        # Pentru demo, considerăm plata reușită
        
        comanda.status = 'confirmed'
        comanda.save()
        
        # Golește coșul după plata reușită
        cos = get_or_create_cos(request)
        cos.items.all().delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Plata a fost procesată cu succes!',
            'redirect_url': reverse('confirmare_comanda', args=[comanda.id])
        })
        
    elif comanda.metoda_plata == 'ramburs':
        # Pentru ramburs, confirmă direct comanda
        comanda.status = 'confirmed'
        comanda.save()
        
        # Golește coșul
        cos = get_or_create_cos(request)
        cos.items.all().delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Comanda a fost confirmată! Veți plăti la livrare.',
            'redirect_url': reverse('confirmare_comanda', args=[comanda.id])
        })
    
    return JsonResponse({
        'success': False,
        'message': 'Metodă de plată nerecunoscută'
    })


def confirmare_comanda(request, comanda_id):
    """Pagina de confirmare a comenzii"""
    comanda = get_object_or_404(Comanda, id=comanda_id)
   
    # Verifică dacă utilizatorul are dreptul să vadă această comandă
    if request.user.is_authenticated:
        if comanda.user != request.user:
            messages.error(request, 'Nu aveți permisiunea să vizualizați această comandă')
            return redirect('lista_tari')
   
    context = {
        'comanda': comanda,
    }
    return render(request, 'tarile/confirmare_comanda.html', context)


# API pentru coș (pentru AJAX requests)
def cos_api_count(request):
    """Returnează numărul de produse din coș"""
    cos = get_or_create_cos(request)
    return JsonResponse({
        'count': cos.total_produse,
        'total': float(cos.total_pret)
    })


@login_required
def comenzile_mele(request):
    """Listează comenzile utilizatorului autentificat"""
    comenzi = Comanda.objects.filter(user=request.user).prefetch_related('items')
   
    context = {
        'comenzi': comenzi,
    }
    return render(request, 'tarile/comenzile_mele.html', context)