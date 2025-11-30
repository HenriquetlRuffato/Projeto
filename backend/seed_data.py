from app import app, db
from models import TipoDespesa
from expense_classifier import ExpenseClassifier

def seed_expense_categories():
    """
    Popula o banco de dados com as categorias de despesas predefinidas
    """
    with app.app_context():
        classifier = ExpenseClassifier()
        categories = classifier.get_all_categories()
        
        for category_name, subcategories in categories.items():
            # Verificar se a categoria já existe
            existing = TipoDespesa.query.filter_by(nome=category_name).first()
            
            if not existing:
                tipo_despesa = TipoDespesa(
                    nome=category_name,
                    descricao=f"Categoria: {category_name}. Inclui: {', '.join(subcategories)}"
                )
                db.session.add(tipo_despesa)
                print(f"Categoria criada: {category_name}")
            else:
                print(f"Categoria já existe: {category_name}")
        
        try:
            db.session.commit()
            print("Todas as categorias de despesas foram criadas com sucesso!")
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao criar categorias: {e}")

if __name__ == '__main__':
    seed_expense_categories()