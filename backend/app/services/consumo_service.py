import logging

from app.repositories.consumo_repository import get_relatorios, save_consumos
from app.utils.calculations import calculate_metrics
from app.utils.validators import validate_data

logger = logging.getLogger(__name__)


def process_file(db, df, upload_id=None, commit=True):
    """
    Processa o arquivo:
    - valida dados
    - calcula métricas
    - salva no banco
    """
    logger.info("Iniciando processamento do arquivo")

    # 🔍 validações
    validate_data(df)

    # ⚙️ cálculos
    metrics = calculate_metrics(df)

    # 💾 persistência
    save_consumos(db, df, upload_id=upload_id, commit=commit)

    logger.info("Processamento concluído")
    return metrics


def get_relatorios_service(db):
    """
    Retorna relatórios agregados por cliente
    """
    logger.info("Buscando relatórios")
    return get_relatorios(db)


def get_resumo_service(db):
    relatorios = get_relatorios(db)

    return {
        "total_clientes": len(relatorios),
        "total_geral_consumo": sum(r["total_consumo"] for r in relatorios),
        "total_geral_custo": sum(r["total_custo"] for r in relatorios)
    }
