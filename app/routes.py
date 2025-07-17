import os
import csv
from decimal import Decimal
from flask import (
    Blueprint, render_template, request,
    flash, redirect, url_for, current_app
)
from werkzeug.utils import secure_filename
from sqlalchemy import text
from . import db
from .models import TrResultado

bp = Blueprint('main', __name__)
ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(fn):
    return '.' in fn and fn.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/ping')
def ping():
    db.session.execute(text('SELECT 1'))
    return 'pong', 200

@bp.route('/', methods=['GET', 'POST'])
def upload_tr_resultado():
    if request.method == 'POST':
        f = request.files.get('csv_file')
        if not f or not allowed_file(f.filename):
            flash('Selecione um arquivo .csv válido.', 'danger')
            return redirect(request.url)

        upload_dir = os.path.join(current_app.instance_path, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        filename = secure_filename(f.filename)
        path = os.path.join(upload_dir, filename)
        f.save(path)

        registros, errors = [], []
        # Atenção: CSV usa ';' e codificação latin1 (ISO-8859-1)
        with open(path, newline='', encoding='latin1') as fp:
            reader = csv.reader(fp, delimiter=';')
            for i, row in enumerate(reader, start=1):
                # cada linha deve ter exatamente 6 colunas
                if len(row) != 6:
                    errors.append(f"Linha {i}: número de colunas inválido ({len(row)})")
                    continue
                try:
                    # mapeia colunas fixas por posição
                    desc  = row[0].strip()
                    v1 = row[1].strip().replace(',', '.')
                    v2 = row[2].strip().replace(',', '.')
                    v3 = row[3].strip().replace(',', '.')
                    v4 = row[4].strip().replace(',', '.')
                    v5 = row[5].strip().replace(',', '.')
                    reg = TrResultado(
                        Tr_ResultadoAno         = 2025,
                        Tr_ResultadoMes         = 'Janeiro',
                        Tr_ResultadoConta       = desc,
                        Tr_ResultadoOrcado      = Decimal(v1) if v1 else None,
                        Tr_ResultadoRealizado   = Decimal(v2) if v2 else None,
                        Tr_ResultadoRealAntxAtu = Decimal(v3) if v3 else None,
                        Tr_ResultadoRealxOrc    = Decimal(v4) if v4 else None,
                        Tr_ResultadoAnoAnterior = Decimal(v5) if v5 else None,
                    )
                    registros.append(reg)
                except Exception as e:
                    errors.append(f"Linha {i}: {e}")

        if errors:
            flash('Erros no CSV:<br>' + '<br>'.join(errors), 'danger')
        else:
            db.session.bulk_save_objects(registros)
            db.session.commit()
            flash(f'{len(registros)} registros importados com sucesso!', 'success')

        return redirect(url_for('main.upload_tr_resultado'))

    ultimos = (
        TrResultado.query
        .order_by(TrResultado.Tr_ResultadoID.desc())
        .limit(50)
        .all()
    )
    return render_template('upload.html', resultados=ultimos)
