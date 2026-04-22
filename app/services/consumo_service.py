from app.utils.validators import validate_columns, validate_data
from app.utils.calculations import calculate_metrics
from app.repositories.consumo_repository import save_consumos


def process_file(db, df):
    """
    Processa o arquivo:
    - valida dados
    - calcula métricas
    - salva no banco
    """

    # 🔍 validações
    validate_columns(df)
    validate_data(df)

    # ⚙️ cálculos
    metrics = calculate_metrics(df)

    # 💾 persistência
    save_consumos(db, df)

    return metrics