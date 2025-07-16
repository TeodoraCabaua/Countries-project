from django.contrib import admin
from .models import Tara
from .models import Produs


class TaraAdmin(admin.ModelAdmin):
    list_display = (
        'nume', 'capitala', 'populatie', 'suprafata', 
        'inaltime_maxima', 'inaltime_minima', 'cel_mai_mare_oras', 
        'moneda', 'limba', 'sistem_politic', 'conducator', 'imagine_principala'
    )
    
    search_fields = ('nume', 'capitala', 'moneda', 'limba')

    list_filter = ('sistem_politic', 'moneda', 'limba')

    fieldsets = (
        ("Informații Generale", {
            'fields': ('nume', 'capitala', 'cel_mai_mare_oras', 'sistem_politic', 'conducator')
        }),
        ("Geografie", {
            'fields': ('populatie', 'suprafata', 'inaltime_maxima', 'inaltime_minima')
        }),
        ("Economie & Cultură", {
            'fields': ('moneda', 'limba')
        }),
        ("Imagini", {
            'fields': ('imagine_principala', 'img1', 'img2', 'img3')
        }),
    )

    

admin.site.register(Tara, TaraAdmin)



@admin.register(Produs)
class ProdusAdmin(admin.ModelAdmin):
    list_display = ['nume', 'pret', 'categorie', 'in_stoc']
    list_filter = ['categorie', 'in_stoc']
    search_fields = ['nume', 'descriere']