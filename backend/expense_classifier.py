import openai
from openai import OpenAI
import json
import os
from typing import List, Dict

class ExpenseClassifier:
    def __init__(self):
        """
        Inicializa o classificador com cliente OpenAI e Gemini
        """
        openai_key = os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=openai_key) if openai_key else None
        
        # Configurar Gemini como fallback
        gemini_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
        if gemini_key:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            # Seleciona dinamicamente um modelo Gemini disponível que suporte generateContent
            model_name = os.getenv('GEMINI_MODEL_NAME')
            if not model_name:
                try:
                    preferred = [
                        "gemini-2.5-flash",
                        "gemini-2.0-flash",
                        "gemini-1.5-flash",
                        "gemini-1.5-pro",
                    ]
                    available = []
                    for m in genai.list_models():
                        methods = getattr(m, "supported_generation_methods", None)
                        name = getattr(m, "name", "")
                        base = name.replace("models/", "")
                        if methods and "generateContent" in methods:
                            # Evitar modelos experimentais/preview/latest que podem causar 404/429
                            if any(suf in base for suf in ["-exp", "-preview"]) or base.endswith("-latest"):
                                continue
                            available.append(base)
                    for name in preferred:
                        if name in available:
                            model_name = name
                            break
                    if not model_name and available:
                        model_name = available[0]
                except Exception:
                    # Fallback para um nome estável
                    model_name = "gemini-1.5-pro"
            self.gemini_model = genai.GenerativeModel(model_name)
        else:
            self.gemini_model = None
        self.categories = {
            "INSUMOS AGRÍCOLAS": [
                "Sementes", "Fertilizantes", "Defensivos Agrícolas", "Corretivos"
            ],
            "MANUTENÇÃO E OPERAÇÃO": [
                "Combustíveis e Lubrificantes",
                "Peças, Parafusos, Componentes Mecânicos",
                "Manutenção de Máquinas e Equipamentos",
                "Pneus, Filtros, Correias",
                "Ferramentas e Utensílios"
            ],
            "RECURSOS HUMANOS": [
                "Mão de Obra Temporária",
                "Salários e Encargos"
            ],
            "SERVIÇOS OPERACIONAIS": [
                "Frete e Transporte",
                "Colheita Terceirizada",
                "Secagem e Armazenagem",
                "Pulverização e Aplicação"
            ],
            "INFRAESTRUTURA E UTILIDADES": [
                "Energia Elétrica",
                "Arrendamento de Terras",
                "Construções e Reformas",
                "Materiais de Construção"
            ],
            "ADMINISTRATIVAS": [
                "Honorários (Contábeis, Advocatícios, Agronômicos)",
                "Despesas Bancárias e Financeiras"
            ],
            "SEGUROS E PROTEÇÃO": [
                "Seguro Agrícola",
                "Seguro de Ativos (Máquinas/Veículos)",
                "Seguro Prestamista"
            ],
            "IMPOSTOS E TAXAS": [
                "ITR, IPTU, IPVA, INCRA-CCIR"
            ],
            "INVESTIMENTOS": [
                "Aquisição de Máquinas e Implementos",
                "Aquisição de Veículos",
                "Aquisição de Imóveis",
                "Infraestrutura Rural"
            ]
        }

    def _classify_with_rules(self, product_description: str) -> str:
        text = (product_description or "").lower()
        rules = [
            ("diesel", "MANUTENÇÃO E OPERAÇÃO"),
            ("combust", "MANUTENÇÃO E OPERAÇÃO"),
            ("manutenção", "MANUTENÇÃO E OPERAÇÃO"),
            ("pneu", "MANUTENÇÃO E OPERAÇÃO"),
            ("filtro", "MANUTENÇÃO E OPERAÇÃO"),
            ("correia", "MANUTENÇÃO E OPERAÇÃO"),
            ("semente", "INSUMOS AGRÍCOLAS"),
            ("fertiliz", "INSUMOS AGRÍCOLAS"),
            ("defensiv", "INSUMOS AGRÍCOLAS"),
            ("energia", "INFRAESTRUTURA E UTILIDADES"),
            ("arrendamento", "INFRAESTRUTURA E UTILIDADES"),
            ("constru", "INFRAESTRUTURA E UTILIDADES"),
            ("honorár", "ADMINISTRATIVAS"),
            ("contáb", "ADMINISTRATIVAS"),
            ("advog", "ADMINISTRATIVAS"),
            ("frete", "SERVIÇOS OPERACIONAIS"),
            ("transporte", "SERVIÇOS OPERACIONAIS"),
            ("colheita", "SERVIÇOS OPERACIONAIS"),
            ("secagem", "SERVIÇOS OPERACIONAIS"),
            ("pulveriza", "SERVIÇOS OPERACIONAIS"),
            ("mão de obra", "RECURSOS HUMANOS"),
            ("salár", "RECURSOS HUMANOS"),
            ("encargo", "RECURSOS HUMANOS"),
            ("seguro", "SEGUROS E PROTEÇÃO"),
            ("iptu", "IMPOSTOS E TAXAS"),
            ("ipva", "IMPOSTOS E TAXAS"),
            ("itr", "IMPOSTOS E TAXAS"),
            ("ccir", "IMPOSTOS E TAXAS"),
            ("máquina", "INVESTIMENTOS"),
            ("implemento", "INVESTIMENTOS"),
            ("veículo", "INVESTIMENTOS"),
            ("imóvel", "INVESTIMENTOS"),
        ]
        for kw, cat in rules:
            if kw in text:
                return cat
        return "ADMINISTRATIVAS"

    def classify_expense(self, product_description: str) -> str:
        """
        Classifica uma despesa baseada na descrição dos produtos usando OpenAI GPT
        """
        # Primeiro, regras locais rápidas
        rule_cat = self._classify_with_rules(product_description)
        if rule_cat:
            return rule_cat

        categories_text = "\n".join([
            f"{category}: {', '.join(items)}"
            for category, items in self.categories.items()
        ])
        
        prompt = f"""
        Você é um especialista em classificação de despesas agrícolas. 
        
        Baseado na descrição dos produtos abaixo, classifique a despesa em UMA das seguintes categorias:
        
        {categories_text}
        
        Descrição dos produtos: {product_description}
        
        Responda APENAS com o nome da categoria (ex: "MANUTENÇÃO E OPERAÇÃO").
        
        Exemplos:
        - "Óleo Diesel" → "MANUTENÇÃO E OPERAÇÃO"
        - "Material Hidráulico" → "INFRAESTRUTURA E UTILIDADES"
        - "Sementes de Soja" → "INSUMOS AGRÍCOLAS"
        """
        
        try:
            if not self.client:
                return self._classify_with_gemini(prompt)
            response = self.client.completions.create(
                model="gpt-3.5-turbo-instruct",
                prompt=prompt,
                max_tokens=100,
                temperature=0.1
            )
            
            classification = response.choices[0].text.strip()
            
            # Verificar se a classificação está nas categorias válidas
            if classification in self.categories:
                return classification
            else:
                # Tentar encontrar uma categoria similar
                for category in self.categories.keys():
                    if category.lower() in classification.lower() or classification.lower() in category.lower():
                        return category
                
                # Se não encontrar, retornar uma categoria padrão
                return "ADMINISTRATIVAS"
                
        except Exception as e:
            error_message = str(e)
            print(f"OpenAI error in classification: {error_message}")
            
            # Tratamento específico para erros de quota da OpenAI - tentar Gemini
            if "quota" in error_message.lower() or "exceeded" in error_message.lower():
                print("OpenAI quota exceeded, trying Gemini fallback...")
                return self._classify_with_gemini(prompt)
            elif "rate limit" in error_message.lower():
                print("OpenAI rate limit reached, trying Gemini fallback...")
                return self._classify_with_gemini(prompt)
            elif "authentication" in error_message.lower() or "api key" in error_message.lower():
                print("OpenAI authentication error, trying Gemini fallback...")
                return self._classify_with_gemini(prompt)
            else:
                # Para outros erros, tentar Gemini como fallback
                print("OpenAI error, trying Gemini fallback...")
                return self._classify_with_gemini(prompt)
    
    def _classify_with_gemini(self, prompt: str) -> str:
        """
        Classifica despesa usando Google Gemini como fallback
        """
        if not self.gemini_model:
            print("Gemini not configured, using default category.")
            return "ADMINISTRATIVAS"
        
        try:
            import google.generativeai as genai
            response = self.gemini_model.generate_content(prompt)
            classification = response.text.strip()
            
            # Verificar se a classificação está nas categorias válidas
            if classification in self.categories:
                return classification
            else:
                # Tentar encontrar uma categoria similar
                for category in self.categories.keys():
                    if category.lower() in classification.lower() or classification.lower() in category.lower():
                        return category
                
                # Se não encontrar, retornar uma categoria padrão
                return "ADMINISTRATIVAS"
                
        except Exception as gemini_error:
            print(f"Gemini classification error: {str(gemini_error)}")
            return "ADMINISTRATIVAS"  # Categoria padrão em caso de erro
    
    def get_all_categories(self) -> Dict[str, List[str]]:
        """
        Retorna todas as categorias disponíveis
        """
        return self.categories