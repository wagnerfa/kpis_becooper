from . import db

class TrResultado(db.Model):
    __tablename__ = 'Tr_Resultado'

    Tr_ResultadoID          = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    Tr_ResultadoAno         = db.Column(db.SmallInteger, nullable=False)
    Tr_ResultadoMes         = db.Column(db.String(20),   nullable=False)
    Tr_ResultadoConta       = db.Column(db.String(120),  nullable=False)
    Tr_ResultadoOrcado      = db.Column(db.Float,        nullable=True)
    Tr_ResultadoRealizado   = db.Column(db.Float,        nullable=True)
    Tr_ResultadoRealAntxAtu = db.Column(db.Float,        nullable=True)
    Tr_ResultadoRealxOrc    = db.Column(db.Float,        nullable=True)
    Tr_ResultadoAnoAnterior = db.Column(db.Float,        nullable=True)


class TrBalancete(db.Model):
    __tablename__ = 'Tr_Balancete'

    Tr_BalanceteId         = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    Tr_BalanceteConta      = db.Column(db.String(200),  nullable=False)
    Tr_BalanceteBacen      = db.Column(db.String(200),  nullable=False)
    Tr_BalanceteTitulo     = db.Column(db.String(200),  nullable=False)
    Tr_BalanceteSaldoAn    = db.Column(db.Numeric(14,2), nullable=False)
    Tr_BalanceteSaldoAt    = db.Column(db.Numeric(14,2), nullable=False)
    Tr_BalanceteDebito     = db.Column(db.Numeric(14,2), nullable=False)
    Tr_BalanceteCredito    = db.Column(db.Numeric(14,2), nullable=False)
    Tr_BalanceteNCredito   = db.Column(db.String(200),  nullable=False)
    Tr_BalanceteNDebito    = db.Column(db.String(200),  nullable=False)
    Tr_BalanceteSate90     = db.Column(db.String(200),  nullable=False)
    Tr_BalanceteSapos90    = db.Column(db.String(200),  nullable=False)
    Tr_BalanceteTituloRel  = db.Column(db.String(200), nullable=False)
    Tr_BalanceteMesAno     = db.Column(db.String(7),   nullable=False)
    Tr_BalanceteCentroCusto= db.Column(db.String(200))
