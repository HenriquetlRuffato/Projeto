from flask import request, jsonify
from app import app, db
from models import *
import os
import math
import json
import re

# LLM providers
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

def _cosine_similarity(a, b):
    if not a or not b:
        return 0.0
    s = 0.0
    na = 0.0
    nb = 0.0
    for i in range(min(len(a), len(b))):
        s += a[i] * b[i]
        na += a[i] * a[i]
        nb += b[i] * b[i]
    denom = math.sqrt(na) * math.sqrt(nb)
    return (s / denom) if denom else 0.0

def _call_llm(question, contexts):
    """Call LLM (OpenAI preferred, fallback to Gemini) with provided context.
    Returns the answer string or None if LLM unavailable/failed.
    """
    system_prompt = (
        "Você é um assistente financeiro. Responda à pergunta usando APENAS o contexto fornecido do banco de dados. "
        "Se algo não estiver no contexto, explique que não há dados suficientes. Seja objetivo e cite itens relevantes."
    )
    context_text = "\n\n".join([c[:4000] for c in contexts])
    user_msg = f"Contexto:\n{context_text}\n\nPergunta:\n{question}"

    # Try OpenAI
    if OPENAI_API_KEY:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY)
            resp = client.chat.completions.create(
                model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_msg},
                ],
                temperature=0.2,
            )
            return resp.choices[0].message.content
        except Exception as e:
            print(f"OpenAI chat completion error: {e}")

    # Fallback Gemini (dinâmico)
    if GOOGLE_API_KEY:
        try:
            import google.generativeai as genai
            genai.configure(api_key=GOOGLE_API_KEY)

            def pick_gemini_model():
                env_model = os.getenv('GOOGLE_MODEL')
                preferred = [
                    'gemini-2.0-flash',
                    'gemini-1.5-pro',
                    'gemini-1.5-flash',
                    'gemini-pro',
                ]
                try:
                    available = []
                    for m in genai.list_models():
                        methods = getattr(m, 'supported_generation_methods', None)
                        name = getattr(m, 'name', '')
                        base = name.replace('models/', '')
                        if methods and 'generateContent' in methods:
                            if any(suf in base for suf in ['-exp', '-preview']) or base.endswith('-latest'):
                                continue
                            available.append(base)
                    # respeita env se existir
                    if env_model and env_model in available:
                        return env_model, available
                    for name in preferred:
                        if name in available:
                            return name, available
                    if available:
                        return available[0], available
                except Exception:
                    pass
                # fallback conservador
                return (env_model or 'gemini-1.5-pro'), []

            first_model, available = pick_gemini_model()
            tried = set()
            candidates = []
            if first_model:
                candidates.append(first_model)
            # adicionar preferidos e os disponíveis, mantendo ordem e sem duplicar
            for n in ['gemini-2.0-flash', 'gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-pro']:
                if n not in candidates:
                    candidates.append(n)
            for n in available:
                if n not in candidates:
                    candidates.append(n)

            last_err = None
            for name in candidates:
                if name in tried:
                    continue
                tried.add(name)
                try:
                    model = genai.GenerativeModel(name)
                    resp = model.generate_content([system_prompt, user_msg])
                    return resp.text
                except Exception as e:
                    last_err = e
                    print(f"Gemini generate_content error for {name}: {e}")
                    continue
            # Do not surface error string to user; signal failure
            return None
        except Exception as e:
            print(f"Gemini client error: {e}")
            return None

    # No provider available
    return None

def _embed_text(text):
    """Create embedding for text using OpenAI or Gemini. Returns list[float]."""
    if OPENAI_API_KEY:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY)
            resp = client.embeddings.create(
                model=os.getenv('OPENAI_EMBEDDINGS_MODEL', 'text-embedding-3-small'),
                input=text,
            )
            return resp.data[0].embedding
        except Exception:
            pass
    if GOOGLE_API_KEY:
        # Gemini não tem embeddings públicos padronizados; como fallback simples, retorne None
        return None
    return None

def _entity_texts():
    """Yield tuples (entity_type, id, text) for indexing."""
    # Fornecedores
    for f in Fornecedor.query.all():
        txt = f"Fornecedor: {f.razao_social} | Fantasia: {f.fantasia or ''} | CNPJ: {f.cnpj} | Ativo: {f.is_active}"
        yield ("fornecedor", f.id, txt)
    # Faturados
    for p in Faturado.query.all():
        txt = f"Faturado: {p.nome_completo} | CPF: {p.cpf} | Ativo: {p.is_active}"
        yield ("faturado", p.id, txt)
    # Tipos de despesa
    for t in TipoDespesa.query.all():
        txt = f"TipoDespesa: {t.nome} | Descricao: {t.descricao or ''} | Ativo: {t.is_active}"
        yield ("tipo_despesa", t.id, txt)
    # Contas a pagar (inclui descrição, nota e fornecedor)
    for c in ContaPagar.query.all():
        txt = (
            f"ContaPagar: NF {c.numero_nota_fiscal} | Emissao: {c.data_emissao} | Valor: {c.valor_total} | "
            f"Fornecedor: {c.fornecedor.razao_social} ({c.fornecedor.cnpj}) | Faturado: {c.faturado.nome_completo} | "
            f"Descricao: {c.descricao_produtos} | Ativo: {c.is_active}"
        )
        yield ("conta_pagar", c.id, txt)

@app.route('/api/rag/embeddings/build', methods=['POST'])
def rag_build_embeddings():
    """Build embeddings for key entities and store in EmbeddingIndex."""
    try:
        created = 0
        updated = 0
        if not OPENAI_API_KEY and not GOOGLE_API_KEY:
            return jsonify({"error": "LLM/Embeddings não configurado"}), 400
        for entity_type, entity_id, text in _entity_texts():
            vec = _embed_text(text)
            if vec is None:
                continue
            existing = EmbeddingIndex.query.filter_by(entity_type=entity_type, entity_id=entity_id).first()
            if existing:
                existing.text = text
                existing.set_embedding(vec)
                updated += 1
            else:
                idx = EmbeddingIndex(entity_type=entity_type, entity_id=entity_id, text=text)
                idx.set_embedding(vec)
                db.session.add(idx)
                created += 1
        db.session.commit()
        return jsonify({"message": "Embeddings construídos", "created": created, "updated": updated}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/api/rag/embeddings/query', methods=['POST'])
def rag_embeddings_query():
    """Query embeddings index, retrieve top-k contexts and answer via LLM."""
    try:
        data = request.get_json() or {}
        question = data.get('question') or ''
        top_k = int(data.get('top_k') or 5)
        if not question.strip():
            return jsonify({"error": "Pergunta vazia"}), 400
        qvec = _embed_text(question)
        if not qvec:
            return jsonify({"error": "Embeddings não disponíveis"}), 400
        items = EmbeddingIndex.query.all()
        scored = []
        for it in items:
            vec = it.get_embedding()
            score = _cosine_similarity(qvec, vec)
            scored.append((score, it.text))
        scored.sort(key=lambda x: x[0], reverse=True)
        contexts = [t for _, t in scored[:top_k]]
        answer = _call_llm(question, contexts)
        if answer is None:
            # Fallback: return contexts without LLM answer
            summary = f"LLM indisponível. {len(contexts)} contextos relevantes encontrados."
            return jsonify({"answer": summary, "contexts": contexts}), 200
        return jsonify({"answer": answer, "contexts": contexts}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/rag/simple', methods=['POST'])
def rag_simple():
    """Simple RAG: keyword search across text columns, then answer via LLM."""
    try:
        data = request.get_json() or {}
        question = data.get('question') or ''
        top_k = int(data.get('top_k') or 5)
        no_llm = bool(data.get('no_llm'))
        if not question.strip():
            return jsonify({"error": "Pergunta vazia"}), 400

        # Heurísticas para perguntas comuns: entregar dados diretamente
        ql = question.lower()
        contexts = []

        # 1) Listar tipos de despesa cadastrados
        if (('tipo' in ql) or ('tipos' in ql)) and ('despesa' in ql):
            tipos_all = TipoDespesa.query.order_by(TipoDespesa.nome.asc()).all()
            if tipos_all:
                contexts = [f"TipoDespesa: {t.nome} | {t.descricao or ''}" for t in tipos_all]
                nomes = [t.nome for t in tipos_all]
                answer = "Tipos de despesa cadastrados: " + ", ".join(nomes)
                return jsonify({"answer": answer, "contexts": contexts}), 200

        # 2) Perguntas sobre contas a pagar
        if ('contas a pagar' in ql) or (('contas' in ql) and ('pagar' in ql)):
            contas = ContaPagar.query.order_by(ContaPagar.data_emissao.desc()).limit(max(top_k, 10)).all()
            if contas:
                contexts = [
                    (
                        f"ContaPagar: NF {c.numero_nota_fiscal} | Emissao {c.data_emissao} | Valor {c.valor_total} | "
                        f"Fornecedor {c.fornecedor.razao_social} | Desc { (c.descricao_produtos or '')[:200] }"
                    )
                    for c in contas
                ]
                resumo = [f"NF {c.numero_nota_fiscal} (R$ {c.valor_total})" for c in contas[:5]]
                answer = f"Total de contas a pagar listadas: {len(contas)}. Principais: " + ", ".join(resumo)
                return jsonify({"answer": answer, "contexts": contexts}), 200

        # 3) Perguntas sobre fornecedores
        if 'fornecedor' in ql or 'fornecedores' in ql:
            fornecedores = Fornecedor.query.order_by(Fornecedor.razao_social.asc()).limit(max(top_k, 10)).all()
            if fornecedores:
                contexts = [
                    f"Fornecedor: {f.razao_social} | CNPJ: {f.cnpj} | Ativo: {f.is_active}"
                    for f in fornecedores
                ]
                nomes = [f.razao_social for f in fornecedores[:10]]
                answer = f"Fornecedores cadastrados (amostra): " + ", ".join(nomes)
                return jsonify({"answer": answer, "contexts": contexts}), 200

        # Keywords: split by spaces, filter small tokens
        tokens = [re.sub(r"[^\w\d]", "", t) for t in question.split()]
        tokens = [t for t in tokens if len(t) > 2]
        
        # fallback para busca por palavras-chave
        contexts = []

        def like_any(col, toks):
            from sqlalchemy import or_
            return or_(*[col.ilike(f"%{tok}%") for tok in toks])

        # Fornecedores
        if tokens:
            fornecedores = Fornecedor.query.filter(like_any(Fornecedor.razao_social, tokens)).limit(top_k).all()
            for f in fornecedores:
                contexts.append(f"Fornecedor: {f.razao_social} | CNPJ: {f.cnpj} | Ativo: {f.is_active}")

        # Tipos de despesa
        tipos = TipoDespesa.query.filter(like_any(TipoDespesa.nome, tokens)).limit(top_k).all()
        for t in tipos:
            contexts.append(f"TipoDespesa: {t.nome} | {t.descricao or ''}")

        # Contas a pagar (nota, descrição)
        contas = ContaPagar.query.filter(
            like_any(ContaPagar.numero_nota_fiscal, tokens)
        ).limit(top_k).all()
        for c in contas:
            contexts.append(
                f"ContaPagar: NF {c.numero_nota_fiscal} | Valor {c.valor_total} | Fornecedor {c.fornecedor.razao_social} | Desc {c.descricao_produtos[:200]}"
            )

        # Se nada encontrado, amplie por descrição de produtos
        if not contexts:
            contas2 = ContaPagar.query.filter(like_any(ContaPagar.descricao_produtos, tokens)).limit(top_k).all()
            for c in contas2:
                contexts.append(
                    f"ContaPagar: NF {c.numero_nota_fiscal} | Valor {c.valor_total} | Fornecedor {c.fornecedor.razao_social} | Desc {c.descricao_produtos[:200]}"
                )

        if no_llm:
            resumo = ", ".join([c.split("|")[0].strip() for c in contexts[:5]]) if contexts else "Sem contextos"
            answer = f"{len(contexts)} contextos relevantes encontrados. Principais: {resumo}"
            return jsonify({"answer": answer, "contexts": contexts}), 200

        answer = _call_llm(question, contexts)
        if answer is None:
            resumo = ", ".join([c.split("|")[0].strip() for c in contexts[:5]]) if contexts else "Sem contextos"
            answer = f"LLM indisponível. {len(contexts)} contextos relevantes encontrados. Principais: {resumo}"
            return jsonify({"answer": answer, "contexts": contexts}), 200

        return jsonify({"answer": answer, "contexts": contexts}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500