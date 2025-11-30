from app import db
from datetime import datetime
from sqlalchemy.orm import relationship
import json

class BaseModel(db.Model):
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

class Fornecedor(BaseModel):
    __tablename__ = 'fornecedores'
    
    razao_social = db.Column(db.String(255), nullable=False)
    fantasia = db.Column(db.String(255))
    cnpj = db.Column(db.String(18), unique=True, nullable=False)
    
    # Relacionamentos
    contas_pagar = relationship("ContaPagar", back_populates="fornecedor")

class Cliente(BaseModel):
    __tablename__ = 'clientes'
    
    nome_completo = db.Column(db.String(255), nullable=False)
    cpf = db.Column(db.String(14), unique=True)
    cnpj = db.Column(db.String(18), unique=True)
    
    # Relacionamentos
    contas_receber = relationship("ContaReceber", back_populates="cliente")

class Faturado(BaseModel):
    __tablename__ = 'faturados'
    
    nome_completo = db.Column(db.String(255), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    
    # Relacionamentos
    contas_pagar = relationship("ContaPagar", back_populates="faturado")

class TipoReceita(BaseModel):
    __tablename__ = 'tipos_receita'
    
    nome = db.Column(db.String(100), nullable=False, unique=True)
    descricao = db.Column(db.Text)

class TipoDespesa(BaseModel):
    __tablename__ = 'tipos_despesa'
    
    nome = db.Column(db.String(100), nullable=False, unique=True)
    descricao = db.Column(db.Text)

class ContaPagar(BaseModel):
    __tablename__ = 'contas_pagar'
    
    numero_nota_fiscal = db.Column(db.String(50), nullable=False)
    data_emissao = db.Column(db.Date, nullable=False)
    descricao_produtos = db.Column(db.Text, nullable=False)
    valor_total = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Chaves estrangeiras
    fornecedor_id = db.Column(db.Integer, db.ForeignKey('fornecedores.id'), nullable=False)
    faturado_id = db.Column(db.Integer, db.ForeignKey('faturados.id'), nullable=False)
    
    # Relacionamentos
    fornecedor = relationship("Fornecedor", back_populates="contas_pagar")
    faturado = relationship("Faturado", back_populates="contas_pagar")
    parcelas = relationship("ParcelaPagar", back_populates="conta_pagar", cascade="all, delete-orphan")
    classificacoes = relationship("ClassificacaoDespesa", back_populates="conta_pagar", cascade="all, delete-orphan")

class ContaReceber(BaseModel):
    __tablename__ = 'contas_receber'
    
    numero_documento = db.Column(db.String(50), nullable=False)
    data_emissao = db.Column(db.Date, nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    valor_total = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Chaves estrangeiras
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    
    # Relacionamentos
    cliente = relationship("Cliente", back_populates="contas_receber")
    parcelas = relationship("ParcelaReceber", back_populates="conta_receber", cascade="all, delete-orphan")
    classificacoes = relationship("ClassificacaoReceita", back_populates="conta_receber", cascade="all, delete-orphan")

class ParcelaPagar(BaseModel):
    __tablename__ = 'parcelas_pagar'
    
    numero_parcela = db.Column(db.Integer, nullable=False)
    data_vencimento = db.Column(db.Date, nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    data_pagamento = db.Column(db.Date)
    valor_pago = db.Column(db.Numeric(10, 2))
    
    # Chaves estrangeiras
    conta_pagar_id = db.Column(db.Integer, db.ForeignKey('contas_pagar.id'), nullable=False)
    
    # Relacionamentos
    conta_pagar = relationship("ContaPagar", back_populates="parcelas")

class ParcelaReceber(BaseModel):
    __tablename__ = 'parcelas_receber'
    
    numero_parcela = db.Column(db.Integer, nullable=False)
    data_vencimento = db.Column(db.Date, nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    data_recebimento = db.Column(db.Date)
    valor_recebido = db.Column(db.Numeric(10, 2))
    
    # Chaves estrangeiras
    conta_receber_id = db.Column(db.Integer, db.ForeignKey('contas_receber.id'), nullable=False)
    
    # Relacionamentos
    conta_receber = relationship("ContaReceber", back_populates="parcelas")

class ClassificacaoDespesa(BaseModel):
    __tablename__ = 'classificacoes_despesa'
    
    # Chaves estrangeiras
    conta_pagar_id = db.Column(db.Integer, db.ForeignKey('contas_pagar.id'), nullable=False)
    tipo_despesa_id = db.Column(db.Integer, db.ForeignKey('tipos_despesa.id'), nullable=False)
    
    # Relacionamentos
    conta_pagar = relationship("ContaPagar", back_populates="classificacoes")
    tipo_despesa = relationship("TipoDespesa")

class ClassificacaoReceita(BaseModel):
    __tablename__ = 'classificacoes_receita'
    
    # Chaves estrangeiras
    conta_receber_id = db.Column(db.Integer, db.ForeignKey('contas_receber.id'), nullable=False)
    tipo_receita_id = db.Column(db.Integer, db.ForeignKey('tipos_receita.id'), nullable=False)
    
    # Relacionamentos
    conta_receber = relationship("ContaReceber", back_populates="classificacoes")
    tipo_receita = relationship("TipoReceita")

class EmbeddingIndex(BaseModel):
    __tablename__ = 'embedding_index'

    entity_type = db.Column(db.String(50), nullable=False)
    entity_id = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)
    embedding_json = db.Column(db.Text, nullable=False)  # armazenar lista de floats como JSON

    def set_embedding(self, vector):
        self.embedding_json = json.dumps(vector)

    def get_embedding(self):
        try:
            return json.loads(self.embedding_json)
        except Exception:
            return []