from django.db import models
from django.contrib.auth.models import User
import uuid

class Tara(models.Model):
    nume = models.CharField(max_length=100, unique=True)
    capitala = models.CharField(max_length=100)
    populatie = models.PositiveIntegerField()
    suprafata = models.PositiveIntegerField()
    inaltime_maxima = models.PositiveIntegerField(blank=True, null=True)
    inaltime_minima = models.IntegerField(blank=True, null=True)
    cel_mai_mare_oras = models.CharField(max_length=100, blank=True, null=True)
    moneda = models.CharField(max_length=50)
    limba = models.CharField(max_length=50)
    sistem_politic = models.CharField(max_length=100)
    conducator = models.CharField(max_length=100, blank=True, null=True)

    # Câmpuri pentru imagini
    imagine_principala = models.ImageField(upload_to='imagini_tari/', blank=True, null=True)
    img1 = models.ImageField(upload_to='imagini_tari/', blank=True, null=True)
    img2 = models.ImageField(upload_to='imagini_tari/', blank=True, null=True)
    img3 = models.ImageField(upload_to='imagini_tari/', blank=True, null=True)

    def __str__(self):
        return self.nume
    
class Produs(models.Model):
    nume = models.CharField(max_length=200)
    descriere = models.TextField()
    pret = models.DecimalField(max_digits=10, decimal_places=2)
    pret_redus = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    imagine_principala = models.ImageField(upload_to='produse/')
    categorie = models.CharField(max_length=100)
    in_stoc = models.BooleanField(default=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    numar_reviewuri = models.IntegerField(default=0)
    data_adaugare = models.DateTimeField(auto_now_add=True)
    
    # Câmpuri pentru detalii
    descriere_detaliata = models.TextField(blank=True, null=True, help_text="Descriere completă a produsului")
    specificatii = models.TextField(blank=True, null=True, help_text="Specificații tehnice (JSON sau text simplu)")
    dimensiuni = models.CharField(max_length=100, blank=True, null=True)
    greutate = models.CharField(max_length=50, blank=True, null=True)
    material = models.CharField(max_length=100, blank=True, null=True)
    tara_origine = models.CharField(max_length=100, blank=True, null=True)
    garantie = models.CharField(max_length=100, blank=True, null=True)
    instructiuni_utilizare = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.nume

class ImaginiProdus(models.Model):
    produs = models.ForeignKey(Produs, on_delete=models.CASCADE, related_name='imagini')
    imagine = models.ImageField(upload_to='produse/imagini/')
    titlu = models.CharField(max_length=200, blank=True, null=True)
    ordine = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['ordine']
        verbose_name = "Imagine Produs"
        verbose_name_plural = "Imagini Produse"
    
    def __str__(self):
        return f"{self.produs.nume} - Imagine {self.ordine}"

class CodReducere(models.Model):
    cod = models.CharField(max_length=20, unique=True)
    tip = models.CharField(max_length=10, choices=[
        ('procent', 'Procent'),
        ('suma', 'Sumă fixă'),
        ('livrare', 'Livrare gratuită')
    ])
    valoare = models.DecimalField(max_digits=10, decimal_places=2)
    activ = models.BooleanField(default=True)
    data_expirare = models.DateTimeField()

class Cos(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    data_creare = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        if self.user:
            return f"Cos - {self.user.username}"
        return f"Cos - Session {self.session_key or 'Anonim'}"
    
    @property
    def total_produse(self):
        return sum(item.cantitate for item in self.items.all())
    
    @property
    def total_pret(self):
        total = 0
        for item in self.items.all():
            pret_produs = item.produs.pret_redus if item.produs.pret_redus else item.produs.pret
            total += item.cantitate * pret_produs
        return total
    
    @property
    def cost_transport(self):
        return 15 if self.total_pret < 100 else 0
    
    @property
    def total_cu_transport(self):
        return self.total_pret + self.cost_transport

class CosItem(models.Model):
    cos = models.ForeignKey(Cos, on_delete=models.CASCADE, related_name='items')
    produs = models.ForeignKey(Produs, on_delete=models.CASCADE)
    cantitate = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.produs.nume} x {self.cantitate}"
    
    @property
    def pret_unitar(self):
        return self.produs.pret_redus if self.produs.pret_redus else self.produs.pret
    
    @property
    def total_pret(self):
        return self.cantitate * self.pret_unitar

class ConfigurareTransport(models.Model):
    nume = models.CharField(max_length=100)
    pret = models.DecimalField(max_digits=10, decimal_places=2)
    timp_livrare = models.CharField(max_length=100)
    zile_livrare_standard = models.IntegerField(default=3)
    
    def __str__(self):
        return self.nume

class Comanda(models.Model):
    STATUS_CHOICES = [
        ('in_asteptare', 'În așteptare'),
        ('confirmed', 'Confirmată'),
        ('procesata', 'Procesată'),
        ('livrata', 'Livrată'),
        ('anulata', 'Anulată'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    numar_comanda = models.CharField(max_length=20, unique=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_asteptare')
    
    # Detalii client
    email = models.EmailField(null=True, blank=True)
    telefon = models.CharField(max_length=20, null=True, blank=True)
    nume_complet = models.CharField(max_length=100, null=True, blank=True)
    adresa = models.CharField(max_length=200, null=True, blank=True)
    oras = models.CharField(max_length=100, null=True, blank=True)
    judet = models.CharField(max_length=100, null=True, blank=True)
    cod_postal = models.CharField(max_length=10, null=True, blank=True)
    observatii_livrare = models.TextField(blank=True, null=True)
    
    # Detalii plată și transport
    metoda_plata = models.CharField(max_length=20, null=True, blank=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cost_transport = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    data_comanda = models.DateTimeField(auto_now_add=True)
    data_livrare_estimata = models.DateField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.numar_comanda:
            self.numar_comanda = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Comanda {self.numar_comanda}"

class ComandaItem(models.Model):
    comanda = models.ForeignKey(Comanda, on_delete=models.CASCADE, related_name='items')
    produs = models.ForeignKey(Produs, on_delete=models.CASCADE, null=True, blank=True)
    nume_produs = models.CharField(max_length=200)
    pret_unitar = models.DecimalField(max_digits=10, decimal_places=2)
    cantitate = models.PositiveIntegerField()
    total_pret = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.nume_produs} x {self.cantitate}"