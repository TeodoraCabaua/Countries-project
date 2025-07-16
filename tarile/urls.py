from django.urls import path
from .views import lista_tari, detalii_tara
from . import views

urlpatterns = [
    # Pagini principale
    path('', lista_tari, name='lista_tari'),
    path('<int:tara_id>/', detalii_tara, name='detalii_tara'),
    path('cauta/', views.cauta_tara, name='cauta_tara'),
    
    # Produse
    path('produse/', views.lista_produse, name='lista_produse'),
    path('produs/<int:produs_id>/', views.detalii_produs, name='detalii_produs'),
    
    # Coș de cumpărături
    path('cos/', views.vezi_cos, name='vezi_cos'),
    path('cos/adauga/<int:produs_id>/', views.adauga_in_cos, name='adauga_in_cos'),
    path('cos/actualizeaza/', views.actualizeaza_cos, name='actualizeaza_cos'),
    path('cos/sterge/<int:item_id>/', views.sterge_din_cos, name='sterge_din_cos'),
    path('cos/count/', views.cos_api_count, name='cos_api_count'),
    
    # Checkout și comenzi
    path('checkout/', views.checkout, name='checkout'),
    path('plata/<int:comanda_id>/', views.pagina_plata, name='pagina_plata'),
    path('proceseaza-plata/<int:comanda_id>/', views.proceseaza_plata, name='proceseaza_plata'),
    path('confirmare/<int:comanda_id>/', views.confirmare_comanda, name='confirmare_comanda'),
    path('comenzile-mele/', views.comenzile_mele, name='comenzile_mele'),
]