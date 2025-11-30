from flask import request, jsonify
from app import app, db
from models import *
from datetime import datetime
from decimal import Decimal

# ==================== FORNECEDORES ====================

@app.route('/api/fornecedores', methods=['POST'])
def create_fornecedor():
    """Criar novo fornecedor"""
    try:
        data = request.get_json()
        
        # Verificar se CNPJ já existe
        existing = Fornecedor.query.filter_by(cnpj=data.get('cnpj')).first()
        if existing:
            return jsonify({'error': 'CNPJ já cadastrado'}), 400
        
        fornecedor = Fornecedor(
            razao_social=data.get('razao_social'),
            fantasia=data.get('fantasia'),
            cnpj=data.get('cnpj')
        )
        
        db.session.add(fornecedor)
        db.session.commit()
        
        return jsonify({
            'id': fornecedor.id,
            'message': 'Fornecedor criado com sucesso'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==================== FATURADOS ====================

@app.route('/api/faturados', methods=['GET'])
def get_faturados():
    """Listar faturados ativos"""
    try:
        faturados = Faturado.query.filter_by(is_active=True).all()
        result = []
        for f in faturados:
            result.append({
                'id': f.id,
                'nome_completo': f.nome_completo,
                'cpf': f.cpf,
                'created_at': f.created_at.isoformat()
            })
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/fornecedores/<int:fornecedor_id>', methods=['PUT'])
def update_fornecedor(fornecedor_id):
    """Atualizar fornecedor"""
    try:
        fornecedor = Fornecedor.query.get_or_404(fornecedor_id)
        data = request.get_json()
        
        # Verificar se CNPJ já existe em outro fornecedor
        if data.get('cnpj') != fornecedor.cnpj:
            existing = Fornecedor.query.filter_by(cnpj=data.get('cnpj')).first()
            if existing:
                return jsonify({'error': 'CNPJ já cadastrado'}), 400
        
        fornecedor.razao_social = data.get('razao_social', fornecedor.razao_social)
        fornecedor.fantasia = data.get('fantasia', fornecedor.fantasia)
        fornecedor.cnpj = data.get('cnpj', fornecedor.cnpj)
        
        db.session.commit()
        
        return jsonify({'message': 'Fornecedor atualizado com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/fornecedores/<int:fornecedor_id>/inativar', methods=['PATCH'])
def inactivate_fornecedor(fornecedor_id):
    """Inativar fornecedor (não excluir)"""
    try:
        fornecedor = Fornecedor.query.get_or_404(fornecedor_id)
        fornecedor.is_active = False
        
        db.session.commit()
        
        return jsonify({'message': 'Fornecedor inativado com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/fornecedores/<int:fornecedor_id>/reativar', methods=['PATCH'])
def reactivate_fornecedor(fornecedor_id):
    """Reativar fornecedor"""
    try:
        fornecedor = Fornecedor.query.get_or_404(fornecedor_id)
        fornecedor.is_active = True
        
        db.session.commit()
        
        return jsonify({'message': 'Fornecedor reativado com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==================== CLIENTES ====================

@app.route('/api/clientes', methods=['GET'])
def get_clientes():
    """Listar clientes (ativos e inativos)"""
    try:
        clientes = Cliente.query.all()
        result = []
        
        for cliente in clientes:
            result.append({
                'id': cliente.id,
                'nome_completo': cliente.nome_completo,
                'cpf': cliente.cpf,
                'cnpj': cliente.cnpj,
                'is_active': cliente.is_active,
                'created_at': cliente.created_at.isoformat()
            })
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clientes', methods=['POST'])
def create_cliente():
    """Criar novo cliente"""
    try:
        data = request.get_json()
        
        # Verificar se CPF ou CNPJ já existe
        if data.get('cpf'):
            existing = Cliente.query.filter_by(cpf=data.get('cpf')).first()
            if existing:
                return jsonify({'error': 'CPF já cadastrado'}), 400
        
        if data.get('cnpj'):
            existing = Cliente.query.filter_by(cnpj=data.get('cnpj')).first()
            if existing:
                return jsonify({'error': 'CNPJ já cadastrado'}), 400
        
        cliente = Cliente(
            nome_completo=data.get('nome_completo'),
            cpf=data.get('cpf'),
            cnpj=data.get('cnpj')
        )
        
        db.session.add(cliente)
        db.session.commit()
        
        return jsonify({
            'id': cliente.id,
            'message': 'Cliente criado com sucesso'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/clientes/<int:cliente_id>/inativar', methods=['PATCH'])
def inactivate_cliente(cliente_id):
    """Inativar cliente"""
    try:
        cliente = Cliente.query.get_or_404(cliente_id)
        cliente.is_active = False
        
        db.session.commit()
        
        return jsonify({'message': 'Cliente inativado com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/clientes/<int:cliente_id>/reativar', methods=['PATCH'])
def reactivate_cliente(cliente_id):
    """Reativar cliente"""
    try:
        cliente = Cliente.query.get_or_404(cliente_id)
        cliente.is_active = True
        db.session.commit()
        return jsonify({'message': 'Cliente reativado com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/clientes/<int:cliente_id>', methods=['PUT'])
def update_cliente(cliente_id):
    """Atualizar cliente"""
    try:
        cliente = Cliente.query.get_or_404(cliente_id)
        data = request.get_json()
        # Verificar CPF único
        if data.get('cpf') and data.get('cpf') != cliente.cpf:
            existing = Cliente.query.filter_by(cpf=data.get('cpf')).first()
            if existing:
                return jsonify({'error': 'CPF já cadastrado'}), 400
        # Verificar CNPJ único
        if data.get('cnpj') and data.get('cnpj') != cliente.cnpj:
            existing = Cliente.query.filter_by(cnpj=data.get('cnpj')).first()
            if existing:
                return jsonify({'error': 'CNPJ já cadastrado'}), 400
        cliente.nome_completo = data.get('nome_completo', cliente.nome_completo)
        cliente.cpf = data.get('cpf', cliente.cpf)
        cliente.cnpj = data.get('cnpj', cliente.cnpj)
        db.session.commit()
        return jsonify({'message': 'Cliente atualizado com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==================== TIPOS DE DESPESA ====================

@app.route('/api/tipos-despesa', methods=['GET'])
def get_tipos_despesa():
    """Listar tipos de despesa (ativos e inativos)"""
    try:
        tipos = TipoDespesa.query.all()
        result = []
        
        for tipo in tipos:
            result.append({
                'id': tipo.id,
                'nome': tipo.nome,
                'descricao': tipo.descricao,
                'is_active': tipo.is_active,
                'created_at': tipo.created_at.isoformat()
            })
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tipos-despesa', methods=['POST'])
def create_tipo_despesa():
    """Criar novo tipo de despesa"""
    try:
        data = request.get_json()
        
        # Verificar se nome já existe
        existing = TipoDespesa.query.filter_by(nome=data.get('nome')).first()
        if existing:
            return jsonify({'error': 'Tipo de despesa já cadastrado'}), 400
        
        tipo = TipoDespesa(
            nome=data.get('nome'),
            descricao=data.get('descricao')
        )
        
        db.session.add(tipo)
        db.session.commit()
        
        return jsonify({
            'id': tipo.id,
            'message': 'Tipo de despesa criado com sucesso'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/tipos-despesa/<int:tipo_id>/inativar', methods=['PATCH'])
def inactivate_tipo_despesa(tipo_id):
    """Inativar tipo de despesa"""
    try:
        tipo = TipoDespesa.query.get_or_404(tipo_id)
        tipo.is_active = False
        
        db.session.commit()
        
        return jsonify({'message': 'Tipo de despesa inativado com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/tipos-despesa/<int:tipo_id>/reativar', methods=['PATCH'])
def reactivate_tipo_despesa(tipo_id):
    """Reativar tipo de despesa"""
    try:
        tipo = TipoDespesa.query.get_or_404(tipo_id)
        tipo.is_active = True
        db.session.commit()
        return jsonify({'message': 'Tipo de despesa reativado com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==================== TIPOS DE RECEITA ====================

@app.route('/api/tipos-receita', methods=['GET'])
def get_tipos_receita():
    """Listar tipos de receita ativos"""
    try:
        tipos = TipoReceita.query.filter_by(is_active=True).all()
        result = []
        
        for tipo in tipos:
            result.append({
                'id': tipo.id,
                'nome': tipo.nome,
                'descricao': tipo.descricao,
                'created_at': tipo.created_at.isoformat()
            })
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tipos-receita', methods=['POST'])
def create_tipo_receita():
    """Criar novo tipo de receita"""
    try:
        data = request.get_json()
        
        # Verificar se nome já existe
        existing = TipoReceita.query.filter_by(nome=data.get('nome')).first()
        if existing:
            return jsonify({'error': 'Tipo de receita já cadastrado'}), 400
        
        tipo = TipoReceita(
            nome=data.get('nome'),
            descricao=data.get('descricao')
        )
        
        db.session.add(tipo)
        db.session.commit()
        
        return jsonify({
            'id': tipo.id,
            'message': 'Tipo de receita criado com sucesso'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==================== CONTAS A RECEBER ====================

@app.route('/api/contas-receber', methods=['GET'])
def get_contas_receber():
    """Listar contas a receber ativas"""
    try:
        contas = ContaReceber.query.filter_by(is_active=True).all()
        result = []
        
        for conta in contas:
            result.append({
                'id': conta.id,
                'numero_documento': conta.numero_documento,
                'data_emissao': conta.data_emissao.isoformat(),
                'valor_total': float(conta.valor_total),
                'cliente': {
                    'nome_completo': conta.cliente.nome_completo,
                    'cpf': conta.cliente.cpf,
                    'cnpj': conta.cliente.cnpj
                }
            })
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/contas-receber', methods=['POST'])
def create_conta_receber():
    """Criar nova conta a receber"""
    try:
        data = request.get_json()
        
        conta = ContaReceber(
            numero_documento=data.get('numero_documento'),
            data_emissao=datetime.strptime(data.get('data_emissao'), '%Y-%m-%d').date(),
            descricao=data.get('descricao'),
            valor_total=Decimal(str(data.get('valor_total'))),
            cliente_id=data.get('cliente_id')
        )
        
        db.session.add(conta)
        db.session.commit()
        
        return jsonify({
            'id': conta.id,
            'message': 'Conta a receber criada com sucesso'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/contas-pagar/<int:conta_id>/inativar', methods=['PATCH'])
def inactivate_conta_pagar(conta_id):
    """Inativar conta a pagar"""
    try:
        conta = ContaPagar.query.get_or_404(conta_id)
        conta.is_active = False
        
        db.session.commit()
        
        return jsonify({'message': 'Conta a pagar inativada com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/contas-pagar/<int:conta_id>/reativar', methods=['PATCH'])
def reactivate_conta_pagar(conta_id):
    try:
        conta = ContaPagar.query.get_or_404(conta_id)
        conta.is_active = True
        db.session.commit()
        return jsonify({'message': 'Conta a pagar reativada com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/contas-receber/<int:conta_id>/inativar', methods=['PATCH'])
def inactivate_conta_receber(conta_id):
    """Inativar conta a receber"""
    try:
        conta = ContaReceber.query.get_or_404(conta_id)
        conta.is_active = False
        
        db.session.commit()
        
        return jsonify({'message': 'Conta a receber inativada com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/contas-receber/<int:conta_id>/reativar', methods=['PATCH'])
def reactivate_conta_receber(conta_id):
    try:
        conta = ContaReceber.query.get_or_404(conta_id)
        conta.is_active = True
        db.session.commit()
        return jsonify({'message': 'Conta a receber reativada com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/contas-pagar/<int:conta_id>/parcelas', methods=['POST'])
def add_parcela_conta_pagar(conta_id):
    """Adicionar parcela a uma conta a pagar"""
    try:
        conta = ContaPagar.query.get_or_404(conta_id)
        data = request.get_json()
        parcela = ParcelaPagar(
            numero_parcela=data.get('numero_parcela'),
            data_vencimento=datetime.strptime(data.get('data_vencimento'), '%Y-%m-%d').date(),
            valor=Decimal(str(data.get('valor'))),
            conta_pagar_id=conta.id
        )
        db.session.add(parcela)
        db.session.commit()
        return jsonify({'message': 'Parcela adicionada com sucesso', 'parcela_id': parcela.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/contas-receber/<int:conta_id>/parcelas', methods=['POST'])
def add_parcela_conta_receber(conta_id):
    """Adicionar parcela a uma conta a receber"""
    try:
        conta = ContaReceber.query.get_or_404(conta_id)
        data = request.get_json()
        parcela = ParcelaReceber(
            numero_parcela=data.get('numero_parcela'),
            data_vencimento=datetime.strptime(data.get('data_vencimento'), '%Y-%m-%d').date(),
            valor=Decimal(str(data.get('valor'))),
            conta_receber_id=conta.id
        )
        db.session.add(parcela)
        db.session.commit()
        return jsonify({'message': 'Parcela adicionada com sucesso', 'parcela_id': parcela.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/contas-pagar/<int:conta_id>/classificacoes', methods=['POST'])
def add_classificacoes_conta_pagar(conta_id):
    """Adicionar múltiplas classificações de despesa a uma conta a pagar"""
    try:
        conta = ContaPagar.query.get_or_404(conta_id)
        data = request.get_json() or {}
        nomes = data.get('tipos') or []
        created = []
        for nome in nomes:
            tipo = TipoDespesa.query.filter_by(nome=nome).first()
            if not tipo:
                tipo = TipoDespesa(nome=nome, descricao=f"Categoria: {nome}")
                db.session.add(tipo)
                db.session.flush()
            classificacao = ClassificacaoDespesa(conta_pagar_id=conta.id, tipo_despesa_id=tipo.id)
            db.session.add(classificacao)
            db.session.flush()
            created.append({'tipo': nome, 'classificacao_id': classificacao.id})
        db.session.commit()
        return jsonify({'message': 'Classificações adicionadas', 'criados': created}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/contas-receber/<int:conta_id>/classificacoes', methods=['POST'])
def add_classificacoes_conta_receber(conta_id):
    """Adicionar múltiplas classificações de receita a uma conta a receber"""
    try:
        conta = ContaReceber.query.get_or_404(conta_id)
        data = request.get_json() or {}
        nomes = data.get('tipos') or []
        created = []
        for nome in nomes:
            tipo = TipoReceita.query.filter_by(nome=nome).first()
            if not tipo:
                tipo = TipoReceita(nome=nome, descricao=f"Categoria: {nome}")
                db.session.add(tipo)
                db.session.flush()
            classificacao = ClassificacaoReceita(conta_receber_id=conta.id, tipo_receita_id=tipo.id)
            db.session.add(classificacao)
            db.session.flush()
            created.append({'tipo': nome, 'classificacao_id': classificacao.id})
        db.session.commit()
        return jsonify({'message': 'Classificações adicionadas', 'criados': created}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==================== LISTAGENS DE PARCELAS E CLASSIFICAÇÕES (DESPESA) ====================

@app.route('/api/parcelas-pagar', methods=['GET'])
def get_parcelas_pagar():
    """Listar parcelas de contas a pagar ativas"""
    try:
        parcelas = ParcelaPagar.query.filter_by(is_active=True).all()
        result = []
        for p in parcelas:
            result.append({
                'id': p.id,
                'numero_parcela': p.numero_parcela,
                'data_vencimento': p.data_vencimento.isoformat(),
                'valor': float(p.valor),
                'conta_pagar': {
                    'id': p.conta_pagar.id,
                    'numero_nota_fiscal': p.conta_pagar.numero_nota_fiscal
                }
            })
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/classificacoes-despesa', methods=['GET'])
def get_classificacoes_despesa():
    """Listar classificações de despesa ativas"""
    try:
        classificacoes = ClassificacaoDespesa.query.filter_by(is_active=True).all()
        result = []
        for c in classificacoes:
            result.append({
                'id': c.id,
                'conta_pagar': {
                    'id': c.conta_pagar.id,
                    'numero_nota_fiscal': c.conta_pagar.numero_nota_fiscal
                },
                'tipo_despesa': {
                    'id': c.tipo_despesa.id,
                    'nome': c.tipo_despesa.nome
                }
            })
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500