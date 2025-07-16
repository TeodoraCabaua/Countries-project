from django import forms

class CheckoutForm(forms.Form):
    nume_complet = forms.CharField(
        max_length=100, 
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Numele complet'
        }),
        label='Nume complet'
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'adresa@email.com'
        }),
        label='Adresa de email'
    )
    
    telefon = forms.CharField(
        max_length=20, 
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '0721123456'
        }),
        label='Număr de telefon'
    )
    
    adresa = forms.CharField(
        max_length=200, 
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Strada, numărul, etc.'
        }),
        label='Adresa completă'
    )
    
    oras = forms.CharField(
        max_length=100, 
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'București'
        }),
        label='Oraș'
    )
    
    judet = forms.CharField(
        max_length=100, 
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ilfov'
        }),
        label='Județ'
    )
    
    cod_postal = forms.CharField(
        max_length=10, 
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '123456'
        }),
        label='Cod poștal'
    )
    
    observatii_livrare = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 3,
            'placeholder': 'Observații pentru curier (opțional)'
        }),
        label='Observații livrare (opțional)'
    )
    
    METODE_PLATA = [
        ('card', 'Card bancar'),
        ('ramburs', 'Ramburs'),
    ]
    
    metoda_plata = forms.ChoiceField(
        choices=METODE_PLATA, 
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        label='Metoda de plată'
    )
    
    accepta_termeni = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Accept termenii și condițiile'
    )
    
    newsletter = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Vreau să primesc oferte prin email'
    )