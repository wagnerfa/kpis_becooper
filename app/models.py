# app/models.py
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
