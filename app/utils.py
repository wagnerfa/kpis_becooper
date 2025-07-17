import csv
from .models import Registro

def parse_csv(path):
    registros = []
    errors = []
    with open(path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for i, row in enumerate(reader, start=1):
            try:
                reg = Registro(
                    campo1=row['campo1'],
                    campo2=int(row['campo2'])
                )
                registros.append(reg)
            except Exception as e:
                errors.append(f'Linha {i}: {e}')
    return registros, errors
