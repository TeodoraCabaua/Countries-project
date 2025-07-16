from django import forms
from .models import Comanda

class CheckoutForm(forms.Form):
    # Informații contact
    email = forms.EmailField(
        label='Email *',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'exemplu@email.com'
        })
    )
    
    telefon = forms.CharField(
        label='Telefon *',
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '0712345678'
        })
    )
    
    # Informații livrare
    nume_complet = forms.CharField(
        label='Nume complet *',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nume și prenume'
        })
    )
    
    adresa = forms.CharField(
        label='Adresa *',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Strada, numărul, bloc, scară, etaj, apartament'
        })
    )
    
    oras = forms.CharField(
        label='Oraș *',
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'București'
        })
    )
    
    judet = forms.CharField(
        label='Județ *',
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'București'
        })
    )
    
    cod_postal = forms.CharField(
        label='Cod poștal *',
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '012345'
        })
    )
    
    observatii_livrare = forms.CharField(
        label='Observații livrare',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Instrucțiuni speciale pentru livrare (opțional)'
        })
    )
    
    # Metoda de plată
    metoda_plata = forms.ChoiceField(
        choices=Comanda.METODA_PLATA_CHOICES,
        label='Metoda de plată *',
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        })
    )
    
    # Acceptare termeni
    accepta_termeni = forms.BooleanField(
        required=True,
        label='Accept termenii și condițiile *',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    newsletter = forms.BooleanField(
        required=False,
        label='Doresc să primesc oferte prin email',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    def clean_telefon(self):
        telefon = self.cleaned_data['telefon']
        # Îndepărtează spațiile și caracterele speciale
        telefon_curat = ''.join(filter(str.isdigit, telefon))
        
        if len(telefon_curat) < 10:
            raise forms.ValidationError('Numărul de telefon trebuie să aibă cel puțin 10 cifre')
        
        return telefon
    
    def clean_cod_postal(self):
        cod_postal = self.cleaned_data['cod_postal']
        # Verifică dacă codul poștal conține doar cifre
        if not cod_postal.isdigit():
            raise forms.ValidationError('Codul poștal trebuie să conțină doar cifre')
        
        if len(cod_postal) != 6:
            raise forms.ValidationError('Codul poștal trebuie să aibă 6 cifre')
        
        return cod_postal