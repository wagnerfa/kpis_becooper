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
from .models import *
from datetime import datetime

bp = Blueprint('main', __name__)
ALLOWED_EXTENSIONS = {'csv'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def conv_num(s):
    s = s.strip().replace('.', '').replace(',', '.')
    return Decimal(s) if s else None


def conv_int(s):
    return int(s.strip()) if s.strip() else None


def conv_date(s):
    s = s.strip()
    if s and s != '':
        try:
            return datetime.strptime(s, '%d/%m/%Y').date()
        except ValueError:
            return None
    return None


def allowed_file(fn):
    return '.' in fn and fn.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/ping')
def ping():
    db.session.execute(text('SELECT 1'))
    return 'pong', 200


@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/tr_resultado', methods=['GET', 'POST'])
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

                if len(row) != 6:
                    errors.append(f"Linha {i}: número de colunas inválido ({len(row)})")
                    continue
                try:

                    desc = row[0].strip()
                    v1 = row[1].strip().replace(',', '.')
                    v2 = row[2].strip().replace(',', '.')
                    v3 = row[3].strip().replace(',', '.')
                    v4 = row[4].strip().replace(',', '.')
                    v5 = row[5].strip().replace(',', '.')
                    reg = TrResultado(
                        Tr_ResultadoAno=2025,
                        Tr_ResultadoMes='Janeiro',
                        Tr_ResultadoConta=desc,
                        Tr_ResultadoOrcado=Decimal(v1) if v1 else None,
                        Tr_ResultadoRealizado=Decimal(v2) if v2 else None,
                        Tr_ResultadoRealAntxAtu=Decimal(v3) if v3 else None,
                        Tr_ResultadoRealxOrc=Decimal(v4) if v4 else None,
                        Tr_ResultadoAnoAnterior=Decimal(v5) if v5 else None,
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


@bp.route('/tr_balancete', methods=['GET', 'POST'])
def upload_tr_balancete():
    if request.method == 'POST':
        f = request.files.get('csv_file')
        if not f or not allowed_file(f.filename):
            flash('Selecione um arquivo .csv válido.', 'danger')
            return redirect(request.url)

        # salva o CSV
        upload_dir = os.path.join(current_app.instance_path, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        filename = secure_filename(f.filename)
        path = os.path.join(upload_dir, filename)
        f.save(path)

        registros = []
        errors = []

        def conv_num(s):
            s = s.strip().replace('.', '').replace(',', '.')
            return Decimal(s) if s else Decimal('0')

        with open(path, newline='', encoding='latin1') as fp:
            reader = csv.reader(fp, delimiter=';')
            for i, row in enumerate(reader, start=1):
                # aceita 13 ou 14 colunas
                if len(row) not in (13, 14):
                    errors.append(f"Linha {i}: colunas inválidas ({len(row)}) – esperava 13 ou 14")
                    continue

                try:
                    conta = row[0].strip()
                    bacen = row[1].strip()
                    titulo = row[2].strip()
                    saldo_an = conv_num(row[3])
                    saldo_at = conv_num(row[4])
                    debito = conv_num(row[5])
                    credito = conv_num(row[6])
                    n_credito = row[7].strip()
                    n_debito = row[8].strip()
                    sate90 = row[9].strip()
                    sapos90 = row[10].strip()
                    titulo_rel = row[11].strip()
                    mes_ano = row[12].strip()

                    # 14ª coluna opcional
                    if len(row) == 14:
                        centro = row[13].strip() or None
                    else:
                        centro = 'Null'

                    reg = TrBalancete(
                        Tr_BalanceteConta=conta,
                        Tr_BalanceteBacen=bacen,
                        Tr_BalanceteTitulo=titulo,
                        Tr_BalanceteSaldoAn=saldo_an,
                        Tr_BalanceteSaldoAt=saldo_at,
                        Tr_BalanceteDebito=debito,
                        Tr_BalanceteCredito=credito,
                        Tr_BalanceteNCredito=n_credito,
                        Tr_BalanceteNDebito=n_debito,
                        Tr_BalanceteSate90=sate90,
                        Tr_BalanceteSapos90=sapos90,
                        Tr_BalanceteTituloRel=titulo_rel,
                        Tr_BalanceteMesAno=mes_ano,
                        Tr_BalanceteCentroCusto=centro,
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

        return redirect(url_for('main.upload_tr_balancete'))

    ultimos = (
        TrBalancete.query
        .order_by(TrBalancete.Tr_BalanceteId.desc())
        .limit(50)
        .all()
    )
    return render_template('upload_balancete.html', balancetes=ultimos)


@bp.route('/tr_empandamento', methods=['GET', 'POST'])
def upload_tr_empandamento():
    if request.method == 'POST':
        # Pegando dados do formulário
        ano = request.form.get('ano')
        mes = request.form.get('mes')

        if not ano or not mes:
            flash('Por favor, preencha o ano e o mês.', 'danger')
            return redirect(request.url)

        f = request.files.get('csv_file')
        if not f or not allowed_file(f.filename):
            flash('Selecione um arquivo .csv válido.', 'danger')
            return redirect(request.url)

        # salva o CSV
        upload_dir = os.path.join(current_app.instance_path, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        filename = secure_filename(f.filename)
        path = os.path.join(upload_dir, filename)
        f.save(path)

        registros = []
        errors = []

        with open(path, newline='', encoding='latin1') as fp:
            reader = csv.reader(fp, delimiter=';')
            for i, row in enumerate(reader, start=1):
                # Esperando 46 colunas conforme o cabeçalho do exemplo
                if len(row) != 46:
                    errors.append(f"Linha {i}: número de colunas inválido ({len(row)}) – esperava 46")
                    continue

                try:
                    reg = TrEmpandamento(
                        Tr_EmpandamentoAno=int(ano),
                        Tr_EmpandamentoMes=mes,
                        Tr_EmpandamentoDataBase=conv_int(row[0]),
                        Tr_EmpandamentoContrato=row[1].strip() or None,
                        Tr_EmpandamentoCodTaxa=row[2].strip() or None,
                        Tr_EmpandamentoConta=row[3].strip() or None,
                        Tr_EmpandamentoCodLF=conv_int(row[4]),
                        Tr_EmpandamentoDtEmissao=conv_date(row[5]),
                        Tr_EmpandamentoNumParc=conv_int(row[6]),
                        Tr_EmpandamentoParcGer=conv_int(row[7]),
                        Tr_EmpandamentoVencFim=conv_date(row[8]),
                        Tr_EmpandamentoPgtoFim=conv_date(row[9]),
                        Tr_EmpandamentoSaldo=conv_num(row[10]),
                        Tr_EmpandamentoRestantes=conv_int(row[11]),
                        Tr_EmpandamentoSituacao=conv_int(row[12]),
                        Tr_EmpandamentoNivelRisco=conv_int(row[13]),
                        Tr_EmpandamentoDiaFixo=conv_int(row[14]),
                        Tr_EmpandamentoValor=conv_num(row[15]),
                        Tr_EmpandamentoTipoVenc=conv_int(row[16]),
                        Tr_EmpandamentoDiaBase=conv_int(row[17]),
                        Tr_EmpandamentoMatSet=row[18].strip() or None,
                        Tr_EmpandamentoIdGpsol=row[19].strip() or None,
                        Tr_EmpandamentoIdOpGpsol=row[20].strip() or None,
                        Tr_EmpandamentoValorContabil=conv_num(row[21]),
                        Tr_EmpandamentoNome=row[22].strip() or None,
                        Tr_EmpandamentoCodUnid=row[23].strip() or None,
                        Tr_EmpandamentoSit=row[24].strip() or None,
                        Tr_EmpandamentoNomeUnid=row[25].strip() or None,
                        Tr_EmpandamentoCodCart=row[26].strip() or None,
                        Tr_EmpandamentoCodSet=row[27].strip() or None,
                        Tr_EmpandamentoVencIni=conv_date(row[28]),
                        Tr_EmpandamentoNomeTaxa=row[29].strip() or None,
                        Tr_EmpandamentoNomeLF=row[30].strip() or None,
                        Tr_EmpandamentoJuros=conv_num(row[31]),
                        Tr_EmpandamentoNomeCart=row[32].strip() or None,
                        Tr_EmpandamentoRaa=conv_num(row[33]),
                        Tr_EmpandamentoCidade=row[34].strip() or None,
                        Tr_EmpandamentoCodCid=conv_int(row[35]),
                        Tr_EmpandamentoSaldoAtual=conv_num(row[36]),
                        Tr_EmpandamentoCicloCliente=conv_int(row[37]),
                        Tr_EmpandamentoNomeAgente=row[38].strip() or None,
                        Tr_EmpandamentoCodCnae=row[39].strip() or None,
                        Tr_EmpandamentoCodAgencia=conv_int(row[40]),
                        Tr_EmpandamentoAgencia=row[41].strip() or None,
                        Tr_EmpandamentoDoc=row[42].strip() or None,
                        Tr_EmpandamentoCodBanco=row[43].strip() or None,
                        Tr_EmpandamentoBancoC=row[44].strip() or None,
                        Tr_EmpandamentoAnoMes=row[45].strip() or None,
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

        return redirect(url_for('main.upload_tr_empandamento'))

    ultimos = (
        TrEmpandamento.query
        .order_by(TrEmpandamento.Tr_EmpandamentoID.desc())
        .limit(50)
        .all()
    )
    return render_template('upload_empandamento.html', empandamentos=ultimos)


@bp.route('/tr_restituidos', methods=['GET', 'POST'])
def upload_tr_restituidos():
    if request.method == 'POST':
        f = request.files.get('csv_file')
        if not f or not allowed_file(f.filename):
            flash('Selecione um arquivo .csv válido.', 'danger')
            return redirect(request.url)

        # salva o CSV
        upload_dir = os.path.join(current_app.instance_path, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        filename = secure_filename(f.filename)
        path = os.path.join(upload_dir, filename)
        f.save(path)

        registros, errors = [], []

        # CSV usa ';' e encoding latin1
        with open(path, newline='', encoding='latin1') as fp:
            reader = csv.reader(fp, delimiter=';')
            for i, row in enumerate(reader, start=1):
                if len(row) != 6:
                    errors.append(f"Linha {i}: colunas inválidas ({len(row)}) – esperava 6")
                    continue
                try:
                    conta      = row[0].strip()
                    nome       = row[1].strip()
                    lanc       = row[2].strip()
                    data       = conv_date(row[3])
                    valor      = conv_num(row[4])
                    codunid    = row[5].strip() or None

                    reg = TrRestituidos(
                        Tr_RestituidoConta      = conta,
                        Tr_RestituidoNome       = nome,
                        Tr_RestituidoLancamento = lanc,
                        Tr_RestituidoData       = data,
                        Tr_RestituidoValor      = valor,
                        Tr_RestituidoCodUnid    = codunid,
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

        return redirect(url_for('main.upload_tr_restituidos'))

    # GET: mostra os últimos 50
    ultimos = (
        TrRestituidos.query
        .order_by(TrRestituidos.Tr_RestituidoId.desc())
        .limit(50)
        .all()
    )
    return render_template('upload_restituidos.html', restituidos=ultimos)


@bp.route('/tr_saldos', methods=['GET', 'POST'])
def upload_tr_saldos():
    if request.method == 'POST':
        # valida arquivo
        f = request.files.get('csv_file')
        if not f or not allowed_file(f.filename):
            flash('Selecione um arquivo .csv válido.', 'danger')
            return redirect(request.url)

        # salva o CSV
        upload_dir = os.path.join(current_app.instance_path, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        filename = secure_filename(f.filename)
        path = os.path.join(upload_dir, filename)
        f.save(path)  # :contentReference[oaicite:1]{index=1}

        registros, errors = [], []
        EXPECTED_COLS = 43  # número de colunas do CSV (sem o ID)

        with open(path, newline='', encoding='latin1') as fp:
            reader = csv.reader(fp, delimiter=';')
            for i, row in enumerate(reader, start=1):
                if len(row) != EXPECTED_COLS:
                    errors.append(f"Linha {i}: colunas inválidas ({len(row)}) – esperava {EXPECTED_COLS}")
                    continue
                try:
                    reg = Tr_Saldos(
                        Tr_SaldosDataBase       = conv_int(row[0]),
                        Tr_SaldosContrato       = row[1].strip() or None,
                        Tr_SaldosTaxa           = row[2].strip() or None,
                        Tr_SaldosConta          = row[3].strip() or None,
                        Tr_SaldosCodLinha       = conv_int(row[4]),
                        Tr_SaldosDtEmissao      = conv_date(row[5]),
                        Tr_SaldosNumParc        = conv_int(row[6]),
                        Tr_SaldosParcGer        = conv_int(row[7]),
                        Tr_SaldosVencFim        = conv_date(row[8]),
                        Tr_SaldosPgtoFim        = conv_date(row[9]),
                        Tr_SaldosSaldo          = conv_num(row[10]),
                        Tr_SaldosRestante       = conv_int(row[11]),
                        Tr_SaldosSituacao       = conv_int(row[12]),
                        Tr_SaldosNvAtual        = conv_int(row[13]),
                        Tr_SaldosDiaFixo        = conv_int(row[14]),
                        Tr_SaldosValor          = conv_num(row[15]),
                        Tr_SaldosTipoVenc       = conv_int(row[16]),
                        Tr_SaldosDiaBase        = conv_int(row[17]),
                        Tr_SaldosValorContabil  = conv_num(row[18]),
                        Tr_SaldosNome           = row[19].strip() or None,
                        Tr_SaldosCodUnid        = conv_int(row[20]),
                        Tr_SaldosSit            = row[21].strip() or None,
                        Tr_SaldosNomeUnid       = row[22].strip() or None,
                        Tr_SaldosCodCart        = conv_int(row[23]),
                        Tr_SaldosVencIni        = conv_date(row[24]),
                        Tr_SaldosNomeTaxa       = row[25].strip() or None,
                        Tr_SaldosNomeLinha      = row[26].strip() or None,
                        Tr_SaldosJuros          = conv_num(row[27]),
                        Tr_SaldosNomeCart       = row[28].strip() or None,
                        Tr_SaldosRaa            = conv_num(row[29]),
                        Tr_SaldosCidade         = row[30].strip() or None,
                        Tr_SaldosCodCid         = conv_int(row[31]),
                        Tr_SaldosCodAge         = conv_int(row[32]),
                        Tr_SaldosAgencia        = row[33].strip() or None,
                        Tr_SaldosDOC            = row[34].strip() or None,
                        Tr_SaldosRaaFuturas     = conv_num(row[35]),
                        Tr_SaldosCodBanco       = row[36].strip() or None,
                        Tr_SaldosNomeSetor      = row[37].strip() or None,
                        Tr_SaldosIof            = conv_num(row[38]),
                        Tr_SaldosProvisao       = conv_num(row[39]),
                        Tr_SaldosMatSet         = row[40].strip() or None,
                        Tr_SaldosCodSet         = row[41].strip() or None,
                        Tr_SaldosAnoMes         = row[42].strip() or None,
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

        return redirect(url_for('main.upload_tr_saldos'))

    # GET: exibe os últimos 50 saldos importados
    ultimos = (
        Tr_Saldos.query
                .order_by(Tr_Saldos.Tr_SaldosId.desc())
                .limit(50)
                .all()
    )
    return render_template('upload_saldos.html', saldos=ultimos)  # :contentReference[oaicite:2]{index=2}
