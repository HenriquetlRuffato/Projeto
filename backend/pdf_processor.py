import openai
from openai import OpenAI
import PyPDF2
import json
import io
import os
from datetime import datetime
from typing import Dict, Optional
from expense_classifier import ExpenseClassifier

class PDFProcessor:
    def __init__(self):
        """
        Inicializa o processador de PDF com cliente OpenAI e Gemini
        """
        openai_key = os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=openai_key) if openai_key else None
        
        # Lazy: não importe/instancie Gemini no startup
        # Apenas guarde chaves/nomes; importe quando necessário
        self.gemini_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
        self.gemini_model_name = os.getenv('GEMINI_MODEL_NAME')
        self.gemini_model = None  # será criado sob demanda

        # Lazy: não instancie o classificador no startup
        self.classifier = None
    
    def extract_text_from_pdf(self, pdf_file) -> str:
        """
        Extrai texto de um arquivo PDF
        """
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
        except Exception as e:
            raise Exception(f"Erro ao extrair texto do PDF: {str(e)}")
    
    def extract_invoice_data(self, pdf_text: str) -> dict:
        """
        Extrai dados estruturados da nota fiscal usando OpenAI GPT
        """
        prompt = f"""
        Você é um especialista em extração de dados de notas fiscais brasileiras.
        
        Analise o texto da nota fiscal abaixo e extraia EXATAMENTE as seguintes informações em formato JSON:
        
        {{
            "fornecedor": {{
                "razao_social": "string",
                "fantasia": "string ou null",
                "cnpj": "string (formato XX.XXX.XXX/XXXX-XX)"
            }},
            "faturado": {{
                "nome_completo": "string",
                "cpf": "string (formato XXX.XXX.XXX-XX)"
            }},
            "numero_nota_fiscal": "string",
            "data_emissao": "string (formato YYYY-MM-DD)",
            "descricao_produtos": "string (descrição detalhada de todos os produtos/serviços)",
            "valor_total": "number (valor decimal)",
            "data_vencimento": "string (formato YYYY-MM-DD)",
            "quantidade_parcelas": 1
        }}
        
        REGRAS IMPORTANTES:
        1. Se algum campo não for encontrado, use null
        2. Para datas, converta para o formato YYYY-MM-DD
        3. Para valores monetários, use apenas números (sem símbolos)
        4. Para CNPJ e CPF, mantenha a formatação com pontos e traços
        5. Na descrição dos produtos, inclua TODOS os itens listados na nota
        
        Texto da nota fiscal:
        {pdf_text}
        
        Responda APENAS com o JSON válido:
        """
        
        try:
            if self.client:
                response = self.client.completions.create(
                    model="gpt-3.5-turbo-instruct",
                    prompt=prompt,
                    max_tokens=1000,
                    temperature=0.1
                )
                json_response = response.choices[0].text.strip()
                try:
                    data = json.loads(json_response)
                except json.JSONDecodeError:
                    json_response = json_response.replace("```json", "").replace("```", "").strip()
                    data = json.loads(json_response)
                # Classificar
                if data.get("descricao_produtos"):
                    if self.classifier is None:
                        self.classifier = ExpenseClassifier()
                    classificacao = self.classifier.classify_expense(data["descricao_produtos"])
                    data["classificacao_despesa"] = classificacao
                return data
        except Exception as e:
            print(f"OpenAI error: {str(e)}")

        # Fallback: tentar Gemini; se falhar, heurísticas locais
        try:
            return self._extract_with_gemini(prompt)
        except Exception as gem_err:
            print(f"Gemini error: {str(gem_err)}")
            return self._extract_with_rules(pdf_text)
    
    def _extract_with_gemini(self, prompt: str) -> dict:
        """
        Extrai dados usando Google Gemini como fallback
        """
        # Exigir chave configurada
        if not (self.gemini_key):
            raise Exception("Erro na extração de dados: OpenAI indisponível e Gemini não configurado. Verifique as chaves de API.")
        
        # Importar e configurar Gemini apenas quando necessário
        import google.generativeai as genai
        try:
            genai.configure(api_key=self.gemini_key)
        except Exception as e:
            raise Exception(f"Falha ao configurar Gemini: {e}")

        candidates = [
            self.gemini_model_name,
            "gemini-1.5-flash-001",
            "gemini-1.5-flash-latest",
            "gemini-1.5-flash",
            "gemini-1.5-pro-001",
            "gemini-1.5-pro-latest",
            "gemini-1.5-pro",
            "gemini-pro"
        ]
        last_error = None
        
        # Tenta candidatos diretos
        for name in [c for c in candidates if c]:
            try:
                model = genai.GenerativeModel(name)
                response = model.generate_content(prompt)
                json_response = response.text.strip()
                try:
                    data = json.loads(json_response)
                except json.JSONDecodeError:
                    json_response = json_response.replace("```json", "").replace("```", "").strip()
                    data = json.loads(json_response)
                if data.get("descricao_produtos"):
                    if self.classifier is None:
                        self.classifier = ExpenseClassifier()
                    classificacao = self.classifier.classify_expense(data["descricao_produtos"])
                    data["classificacao_despesa"] = classificacao
                self.gemini_model = model
                return data
            except Exception as e:
                last_error = e
                continue

        # Evitar list_models durante execução local para reduzir chamadas remotas
        # Apenas retorne o último erro
        
        raise Exception(f"Erro na extração de dados: Tanto OpenAI quanto Gemini falharam. Gemini error: {str(last_error)}")

    def _extract_with_rules(self, pdf_text: str) -> dict:
        """
        Extração heurística local sem LLM: usa regex/padrões comuns para NF.
        """
        text = pdf_text or ""
        def find_regex(patterns):
            import re
            for p in patterns:
                m = re.search(p, text, re.IGNORECASE | re.MULTILINE)
                if m:
                    return m.group(1) if m.groups() else m.group(0)
            return None

        def norm_date(dt):
            if not dt:
                return None
            from datetime import datetime
            for fmt in ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d.%m.%Y"]:
                try:
                    return datetime.strptime(dt, fmt).date().isoformat()
                except Exception:
                    pass
            return None

        def norm_money(val):
            if not val:
                return None
            v = val.replace("R$", "").replace(" ", "")
            v = v.replace(".", "").replace(",", ".")
            try:
                return float(v)
            except Exception:
                return None

        cnpj = find_regex([r"CNPJ\s*[:\-]?\s*([0-9\.\/-]{14,18})"]) or find_regex([r"([0-9]{2}\.[0-9]{3}\.[0-9]{3}\/[0-9]{4}\-[0-9]{2})"])
        cpf = find_regex([r"CPF\s*[:\-]?\s*([0-9\.\/-]{11,14})", r"([0-9]{3}\.[0-9]{3}\.[0-9]{3}\-[0-9]{2})"])
        nf = find_regex([r"Nota Fiscal\s*(?:N[ºo]\s*)?([A-Za-z0-9\-]+)", r"NF\s*(?:N[ºo]\s*)?([A-Za-z0-9\-]+)"])
        emissao = norm_date(find_regex([r"Emiss[aã]o\s*[:\-]?\s*([0-9]{2}\/[0-9]{2}\/[0-9]{4})", r"([0-9]{4}\-[0-9]{2}\-[0-9]{2})"]))
        venc = norm_date(find_regex([r"Vencimento\s*[:\-]?\s*([0-9]{2}\/[0-9]{2}\/[0-9]{4})"]))
        total = norm_money(find_regex([r"Total\s*[:\-]?\s*R?\$?\s*([0-9\.,]+)", r"Valor Total\s*[:\-]?\s*R?\$?\s*([0-9\.,]+)"]))

        # Tentar razão social ao redor de CNPJ
        razao = None
        if cnpj:
            import re
            for m in re.finditer(re.escape(cnpj), text):
                start = max(0, m.start() - 120)
                snippet = text[start:m.start()]
                cand = find_regex([r"Raz[aã]o Social\s*[:\-]?\s*(.+)"]) or snippet.strip().split("\n")[-1].strip()
                if cand and len(cand) > 2:
                    razao = cand
                    break

        descricao = None
        # Buscar bloco de itens/descrição
        for key in ["Descrição", "Itens", "Produtos", "Serviços"]:
            import re
            m = re.search(key + r"[:\-]?\s*(.+)\n", text, re.IGNORECASE)
            if m:
                descricao = m.group(1)
                break
        if not descricao:
            # fallback: recortar trecho central
            descricao = text[:1000]

        data = {
            "fornecedor": {
                "razao_social": razao,
                "fantasia": None,
                "cnpj": cnpj
            },
            "faturado": {
                "nome_completo": None,
                "cpf": cpf
            },
            "numero_nota_fiscal": nf,
            "data_emissao": emissao,
            "descricao_produtos": descricao,
            "valor_total": total,
            "data_vencimento": venc or emissao,
            "quantidade_parcelas": 1
        }

        if data.get("descricao_produtos"):
            if self.classifier is None:
                self.classifier = ExpenseClassifier()
            cat = self.classifier.classify_expense(data["descricao_produtos"])
            data["classificacao_despesa"] = cat

        return data
    
    def process_pdf(self, pdf_file) -> dict:
        """
        Processa um arquivo PDF completo e retorna os dados extraídos
        """
        try:
            # Extrair texto do PDF
            pdf_text = self.extract_text_from_pdf(pdf_file)
            
            if not pdf_text:
                raise Exception("Não foi possível extrair texto do PDF")
            
            # Extrair dados estruturados
            invoice_data = self.extract_invoice_data(pdf_text)
            
            # Adicionar metadados
            invoice_data["processed_at"] = datetime.now().isoformat()
            # Removido campo 'pdf_text' do retorno conforme solicitado
            
            return {
                "success": True,
                "data": invoice_data
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }