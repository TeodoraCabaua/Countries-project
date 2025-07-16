import csv
import os
from django.core.files import File
from django.conf import settings
from tarile.models import Tara

# Calea către fișierul CSV
csv_file = r"C:\Users\Teodora\Desktop\databasecs.csv"

with open(csv_file, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        tara = Tara(
            nume=row['TARA'],
            capitala=row['CAPITALA'],
            populatie=row['POPULATIE'],
            suprafata=row['SUPRAFATA (km²)'],
            inaltime_maxima=row['Inaltime maxima (m)'] or None,
            inaltime_minima=row['Inaltimea minima (m)'] or None,
            cel_mai_mare_oras=row['Cel mai mare oras'] or None,
            moneda=row['Moneda oficiala'],
            limba=row['Cea mai vorbita limba'],
            sistem_politic=row['Sistem politic'],
            conducator=row['Conducator (F/M)'] or None
        )

        # Adăugare imagine principală
        if row['Imagine principala']:
            image_path = os.path.join(settings.MEDIA_ROOT, 'imagini_tari', row['Imagine principala'])
            if os.path.exists(image_path):
                with open(image_path, 'rb') as img_file:
                    tara.imagine_principala.save(row['Imagine principala'], File(img_file))

        # Adăugare imagini suplimentare
        for i in range(1, 4):  # Img 1, Img 2, Img 3
            img_col = f'Img {i}'
            if row[img_col]:
                image_path = os.path.join(settings.MEDIA_ROOT, 'imagini_tari', row[img_col])
                if os.path.exists(image_path):
                    with open(image_path, 'rb') as img_file:
                        getattr(tara, f"imagine_{i}").save(row[img_col], File(img_file))

        tara.save()

print("✅ Import din CSV finalizat!")