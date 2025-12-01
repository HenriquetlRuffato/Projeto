import io
import re
import json
from datetime import datetime
from typing import Any, Dict, Optional

from PyPDF2 import PdfReader


# --------------------------------------------------------------------
# Funções auxiliares de parsing
# --------------------------------------------------------------------


def _extract_first_group(pattern: str, text: str, flags: int = re.MULTILINE) -> Optional[str]:
    """Retorna o primeiro grupo de captura de um regex ou None."""
    m = re.search(pattern, text, flags)
    if not m:
        return None
    return m.group(1).strip()


def _parse_brazilian_number(value: str) -> Optional[float]:
    """
    Converte '163.520,00' -> 163520.00 (float).
    Retorna None se não conseguir converter.
    """
    if not value:
        return None
    try:
        v = value.replace(".", "").replace(",", ".")
        return float(v)
    except Exception:
        return None


def _extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Lê todo o texto de um PDF em memória usando PyPDF2.
    """
    with io.BytesIO(file_bytes) as pdf_buffer:
        reader = PdfReader(pdf_buffer)
        pages_text = []
        for page in reader.pages:
            try:
                pages_text.append(page.extract_text() or "")
            except Exception:
                continue
    # Junta tudo em um único texto para regex
    return "\n".join(pages_text)


# --------------------------------------------------------------------
# Funções específicas para DANFE
# --------------------------------------------------------------------


def _extract_faturado(text: str) -> Dict[str, Optional[str]]:
    """
    Extrai os dados do DESTINATÁRIO/REMETENTE (faturado) do texto do DANFE.
    Estrutura típica (como no PDF que você mandou):

    DESTINATÁRIO/REMETENTE
    NOME/RAZÃO SOCIAL
    BELTRANO DE SOUZA
    C.N.P.J./C.P.F.
    111.111.111-11
    """
    # Tenta pegar o bloco começando em DESTINATÁRIO/REMETENTE até LOCAL DE ENTREGA (ou até DATA DA EMISSÃO).
    bloco_pattern = (
        r"DESTINATÁRIO/REMETENTE\s+"
        r"(?:NOME/RAZÃO SOCIAL\s+)?"
        r"(?P<nome>.+?)\s+"
        r"C\.N\.P\.J\.\/C\.P\.F\.\s+"
        r"(?P<cpf>[\d\.\-\/]+)"
    )

    m = re.search(bloco_pattern, text, flags=re.DOTALL)
    if not m:
        return {"nome_completo": None, "cpf": None}

    nome = m.group("nome").strip()
    cpf = m.group("cpf").strip()

    return {
        "nome_completo": nome or None,
        "cpf": cpf or None,
    }


def _extract_fornecedor(text: str) -> Dict[str, Optional[str]]:
    """
    Extrai os dados do FORNECEDOR (emitente).
    No seu DANFE:

    CTVA PROTECAO DE CULTIVOS LTDA.
    ...
    INSCRIÇÃO ESTADUAL DO SUBST. TRIB. CNPJ
    47.180.625/0058-81
    """
    # CNPJ do fornecedor (na linha logo após a frase de CNPJ do emitente)
    cnpj = _extract_first_group(
        r"INSCRIÇÃO ESTADUAL DO SUBST\. TRIB\. CNPJ\s+([\d\./\-]+)",
        text,
        flags=re.MULTILINE,
    )

    # Razão social: linha imediatamente anterior à parte de endereço inicial,
    # aqui é o bloco de remetente, normalmente perto do topo.
    # Vamos pegar a primeira linha em MAIÚSCULO completa que pareça com razão social.
    razao_social = None
    lines = text.splitlines()
    for idx, line in enumerate(lines):
        l = line.strip()
        if not l:
            continue
        # heurística simples: contem LTDA ou é muito parecida com nome de empresa
        if " LTDA" in l.upper() or "S.A" in l.upper():
            razao_social = l
            break

    # Fantasia geralmente não aparece nesse modelo de DANFE, então deixamos None
    fantasia = None

    return {
        "cnpj": cnpj,
        "razao_social": razao_social,
        "fantasia": fantasia,
    }


def _extract_datas(text: str) -> Dict[str, Optional[str]]:
    """
    Extrai datas de emissão e vencimento (se houver). No DANFE, a data de vencimento pode estar em FATURA/DUPLICATAS.
    Ex.:

    DATA DA EMISSÃO
    30/04/2025
    ...
    FATURA/DUPLICATAS
    001: 05/05/2025 R$163.520,00;
    """
    emissao = _extract_first_group(
        r"DATA DA EMISSÃO\s+(\d{2}/\d{2}/\d{4})",
        text,
        flags=re.MULTILINE,
    )

    # Data de vencimento: pega a primeira data no bloco de FATURA/DUPLICATAS
    vencimento = _extract_first_group(
        r"FATURA/DUPLICATAS\s+.*?(\d{2}/\d{2}/\d{4})",
        text,
        flags=re.DOTALL,
    )

    def _to_iso(date_str: Optional[str]) -> Optional[str]:
        if not date_str:
            return None
        try:
            d = datetime.strptime(date_str, "%d/%m/%Y")
            return d.date().isoformat()
        except Exception:
            return None

    return {
        "data_emissao": _to_iso(emissao),
        "data_vencimento": _to_iso(vencimento),
    }


def _extract_valor_total(text: str) -> Optional[float]:
    """
    Extrai o VALOR TOTAL DA NOTA.
    Ex.:

    VALOR TOTAL DA NOTA
    163.520,00
    """
    valor_str = _extract_first_group(
        r"VALOR TOTAL DA NOTA\s+([\d\.\,]+)",
        text,
        flags=re.MULTILINE,
    )
    return _parse_brazilian_number(valor_str)


def _extract_numero_nota(text: str) -> Optional[str]:
    """
    Extrai o número da NF-e (pode aparecer como 'No. 000.012.776').
    """
    numero = _extract_first_group(r"No\.\s*([\d\.]{5,})", text, flags=re.MULTILINE)
    return numero


def _extract_descricao_produtos(text: str) -> str:
    """
    Extrai uma descrição consolidada dos produtos.

    Estratégia:
    - Pegar o bloco entre 'DADOS DOS PRODUTOS/SERVIÇOS' e 'DADOS ADICIONAIS'.
    - Ignorar a primeira linha de cabeçalho.
    - Juntar as linhas de texto que tenham letras (descrição), não apenas números.
    """
    bloco = _extract_first_group(
        r"DADOS DOS PRODUTOS/SERVIÇOS\s+(.+?)DADOS ADICIONAIS",
        text,
        flags=re.DOTALL,
    )
    if not bloco:
        return ""

    linhas = [l.strip() for l in bloco.splitlines()]
    descricoes = []

    for l in linhas:
        if not l:
            continue
        # Ignora claramente o cabeçalho
        if "CÓDIGO DESCRIÇÃO" in l.upper():
            continue
        # Ignora linhas que são majoritariamente numéricas (códigos/totais)
        if re.fullmatch(r"[\d\.\, \/A-Z]+", l) and not re.search(r"[a-z]", l):
            # linha cheia de números/letras maiúsculas sem contexto textual => provavelmente tabela
            continue
        descricoes.append(l)

    return " ".join(descricoes)


# --------------------------------------------------------------------
# Função principal usada pelas rotas
# --------------------------------------------------------------------


def process_pdf(file_bytes: bytes) -> Dict[str, Any]:
    """
    Processa um PDF de nota fiscal (DANFE) e retorna o dicionário
    usado pelo frontend.

    Estrutura de retorno (exemplo):

    {
      "classificacao_despesa": "ADMINISTRATIVAS",
      "data_emissao": "2025-04-30",
      "data_vencimento": "2025-04-30",
      "descricao_produtos": "...",
      "faturado": {
        "cpf": "...",
        "nome_completo": "..."
      },
      "fornecedor": {
        "cnpj": "...",
        "fantasia": null,
        "razao_social": "..."
      },
      "numero_nota_fiscal": "000.012.776",
      "processed_at": "2025-12-01T00:41:56.066297",
      "quantidade_parcelas": 1,
      "valor_total": 163520.00
    }
    """
    text = _extract_text_from_pdf(file_bytes)

    datas = _extract_datas(text)
    faturado = _extract_faturado(text)
    fornecedor = _extract_fornecedor(text)
    valor_total = _extract_valor_total(text)
    numero_nota = _extract_numero_nota(text)
    descricao_produtos = _extract_descricao_produtos(text)

    # Quantidade de parcelas: se aparecer em FATURA/DUPLICATAS na forma "001:", usamos 1;
    # se aparecer "001: ...; 002: ...", poderíamos contar, mas por enquanto assumimos 1.
    qtd_parcelas = 1

    result: Dict[str, Any] = {
        "classificacao_despesa": "ADMINISTRATIVAS",  # regra/IA pode sobrescrever depois
        "data_emissao": datas["data_emissao"],
        "data_vencimento": datas["data_vencimento"],
        "descricao_produtos": descricao_produtos,
        "faturado": faturado,
        "fornecedor": fornecedor,
        "numero_nota_fiscal": numero_nota or "ELETR",
        "processed_at": datetime.utcnow().isoformat(),
        "quantidade_parcelas": qtd_parcelas,
        "valor_total": valor_total,
    }

    return result
