import logging
from app.utils.validators import validate_columns, validate_data
from app.utils.calculations import calculate_metrics
from app.repositories.consumo_repository import save_consumos, get_relatorios


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process_file(db, df):
    """
    Processa o arquivo:
    - valida dados
    - calcula métricas
    - salva no banco
    """
    logger.info("Iniciando processamento do arquivo")

    # 🔍 validações
    validate_columns(df)
    validate_data(df)

    # ⚙️ cálculos
    metrics = calculate_metrics(df)

    # 💾 persistência
    save_consumos(db, df)

    logger.info("Processamento concluído")
    return metrics


def get_relatorios_service(db):
    """
    Retorna relatórios agregados por cliente
    """
    logger.info("Buscando relatórios")
    return get_relatorios(db)
