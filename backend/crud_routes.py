from flask import request, jsonify
from app import app, db
from models import *
from datetime import datetime
from decimal import Decimal

def _to_decimal(val):
    try:
        if val is None:
            return Decimal('0')
        if isinstance(val, (int, float, Decimal)):
            try:
                return Decimal(str(val))
            except Exception:
                return Decimal('0')
        s = str(val).strip().replace('\xa0', '')
        if not s:
            return Decimal('0')
        s = s.replace('R$', '').replace('BRL', '').replace(' ', '')
        import re
        s = re.sub(r"[^0-9,.-]", "", s)
        if s.count(',') == 1 and s.count('.') >= 1:
            s = s.replace('.', '').replace(',', '.')
        else:
            s = s.replace(',', '.')
        return Decimal(s)
    except Exception:
        return Decimal('0')
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

@app.route('/api/faturados', methods=['POST'])
def create_faturado():
    try:
        data = request.get_json() or {}
        nome = (data.get('nome_completo') or '').strip()
        cpf = (data.get('cpf') or '').strip()
        if not cpf:
            return jsonify({'error': 'CPF é obrigatório'}), 400
        existing = Faturado.query.filter_by(cpf=cpf).first()
        if existing:
            return jsonify({'error': 'CPF já cadastrado'}), 400
        if not nome:
            nome = cpf
        faturado = Faturado(nome_completo=nome, cpf=cpf)
        db.session.add(faturado)
        db.session.commit()
        return jsonify({'id': faturado.id, 'message': 'Faturado criado com sucesso'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/faturados/<int:faturado_id>', methods=['PUT'])
def update_faturado(faturado_id):
    try:
        faturado = Faturado.query.get_or_404(faturado_id)
        data = request.get_json() or {}
        if data.get('cpf') and data.get('cpf') != faturado.cpf:
            existing = Faturado.query.filter_by(cpf=data.get('cpf')).first()
            if existing:
                return jsonify({'error': 'CPF já cadastrado'}), 400
        faturado.nome_completo = data.get('nome_completo', faturado.nome_completo)
        faturado.cpf = data.get('cpf', faturado.cpf)
        db.session.commit()
        return jsonify({'message': 'Faturado atualizado com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/faturados/<int:faturado_id>/inativar', methods=['PATCH'])
def inactivate_faturado(faturado_id):
    try:
        faturado = Faturado.query.get_or_404(faturado_id)
        faturado.is_active = False
        db.session.commit()
        return jsonify({'message': 'Faturado inativado com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/faturados/<int:faturado_id>/reativar', methods=['PATCH'])
def reactivate_faturado(faturado_id):
    try:
        faturado = Faturado.query.get_or_404(faturado_id)
        faturado.is_active = True
        db.session.commit()
        return jsonify({'message': 'Faturado reativado com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
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

@app.route('/api/tipos-despesa/<int:tipo_id>', methods=['PUT'])
def update_tipo_despesa(tipo_id):
    try:
        tipo = TipoDespesa.query.get_or_404(tipo_id)
        data = request.get_json() or {}
        if data.get('nome') and data.get('nome') != tipo.nome:
            existing = TipoDespesa.query.filter_by(nome=data.get('nome')).first()
            if existing:
                return jsonify({'error': 'Tipo de despesa já cadastrado'}), 400
        tipo.nome = data.get('nome', tipo.nome)
        tipo.descricao = data.get('descricao', tipo.descricao)
        db.session.commit()
        return jsonify({'message': 'Tipo de despesa atualizado com sucesso'}), 200
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

@app.route('/api/tipos-receita/<int:tipo_id>', methods=['PUT'])
def update_tipo_receita(tipo_id):
    try:
        tipo = TipoReceita.query.get_or_404(tipo_id)
        data = request.get_json() or {}
        if data.get('nome') and data.get('nome') != tipo.nome:
            existing = TipoReceita.query.filter_by(nome=data.get('nome')).first()
            if existing:
                return jsonify({'error': 'Tipo de receita já cadastrado'}), 400
        tipo.nome = data.get('nome', tipo.nome)
        tipo.descricao = data.get('descricao', tipo.descricao)
        db.session.commit()
        return jsonify({'message': 'Tipo de receita atualizado com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/tipos-receita/<int:tipo_id>/inativar', methods=['PATCH'])
def inactivate_tipo_receita(tipo_id):
    try:
        tipo = TipoReceita.query.get_or_404(tipo_id)
        tipo.is_active = False
        db.session.commit()
        return jsonify({'message': 'Tipo de receita inativado com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/tipos-receita/<int:tipo_id>/reativar', methods=['PATCH'])
def reactivate_tipo_receita(tipo_id):
    try:
        tipo = TipoReceita.query.get_or_404(tipo_id)
        tipo.is_active = True
        db.session.commit()
        return jsonify({'message': 'Tipo de receita reativado com sucesso'}), 200
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
            valor_total=_to_decimal(data.get('valor_total')),
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

@app.route('/api/contas-pagar/<int:conta_id>', methods=['PUT'])
def update_conta_pagar(conta_id):
    try:
        conta = ContaPagar.query.get_or_404(conta_id)
        data = request.get_json() or {}
        if data.get('numero_nota_fiscal'):
            conta.numero_nota_fiscal = data.get('numero_nota_fiscal')
        if data.get('data_emissao'):
            conta.data_emissao = datetime.strptime(data.get('data_emissao'), '%Y-%m-%d').date()
        if data.get('descricao_produtos'):
            conta.descricao_produtos = data.get('descricao_produtos')
        if data.get('valor_total') is not None:
            conta.valor_total = _to_decimal(data.get('valor_total'))
        db.session.commit()
        return jsonify({'message': 'Conta a pagar atualizada com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/contas-receber/<int:conta_id>', methods=['PUT'])
def update_conta_receber(conta_id):
    try:
        conta = ContaReceber.query.get_or_404(conta_id)
        data = request.get_json() or {}
        if data.get('numero_documento'):
            conta.numero_documento = data.get('numero_documento')
        if data.get('data_emissao'):
            conta.data_emissao = datetime.strptime(data.get('data_emissao'), '%Y-%m-%d').date()
        if data.get('descricao'):
            conta.descricao = data.get('descricao')
        if data.get('valor_total') is not None:
            conta.valor_total = _to_decimal(data.get('valor_total'))
        db.session.commit()
        return jsonify({'message': 'Conta a receber atualizada com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/seed-test-data', methods=['POST'])
def seed_test_data():
    try:
        payload = (request.get_json(silent=True) or {})
        n = int(request.args.get('n') or payload.get('n') or 200)
        created = {'fornecedores': 0, 'clientes': 0, 'faturados': 0, 'tipos_despesa': 0, 'tipos_receita': 0, 'contas_pagar': 0, 'contas_receber': 0}
        for i in range(n):
            f = Fornecedor(razao_social=f'Fornecedor {i}', fantasia=f'Fantasia {i}', cnpj=f'{i%90:02d}.{(i*3)%1000:03d}.{(i*7)%1000:03d}/{(i*11)%10000:04d}-{i%100:02d}')
            db.session.add(f)
            db.session.flush()
            created['fornecedores'] += 1
            cli = Cliente(nome_completo=f'Cliente {i}', cpf=f'{(i*13)%1000:03d}.{(i*17)%1000:03d}.{(i*19)%1000:03d}-{i%100:02d}')
            db.session.add(cli)
            db.session.flush()
            created['clientes'] += 1
            fat = Faturado(nome_completo=f'Faturado {i}', cpf=f'{(i*23)%1000:03d}.{(i*29)%1000:03d}.{(i*31)%1000:03d}-{(i+1)%100:02d}')
            db.session.add(fat)
            db.session.flush()
            created['faturados'] += 1
            td = TipoDespesa(nome=f'Despesa {i}', descricao=f'Categoria automática {i}')
            db.session.add(td)
            db.session.flush()
            created['tipos_despesa'] += 1
            tr = TipoReceita(nome=f'Receita {i}', descricao=f'Categoria automática {i}')
            db.session.add(tr)
            db.session.flush()
            created['tipos_receita'] += 1
            cp = ContaPagar(numero_nota_fiscal=f'NF-{i}', data_emissao=datetime.utcnow().date(), descricao_produtos=f'Itens {i}', valor_total=Decimal('100.00'), fornecedor_id=f.id, faturado_id=fat.id)
            db.session.add(cp)
            db.session.flush()
            created['contas_pagar'] += 1
            cr = ContaReceber(numero_documento=f'DOC-{i}', data_emissao=datetime.utcnow().date(), descricao=f'Descricao {i}', valor_total=Decimal('150.00'), cliente_id=cli.id)
            db.session.add(cr)
            db.session.flush()
            created['contas_receber'] += 1
        db.session.commit()
        return jsonify({'message': 'Seed concluído', 'created': created}), 201
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
            valor=_to_decimal(data.get('valor')),
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
            valor=_to_decimal(data.get('valor')),
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
