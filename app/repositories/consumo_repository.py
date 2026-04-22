from app.models.consumo import Consumo
from app.repositories.cliente_repository import get_or_create_cliente

def save_consumos(db, df):
    try:
        objetos = []

        for _, row in df.iterrows():
            cliente = get_or_create_cliente(db, row["cliente"])

            consumo = Consumo(
                cliente_id=cliente.id,
                consumo_kwh=row["consumo_kwh"],
                preco_mwh=row["preco_mwh"],
                custo=row["custo"]
            )

            objetos.append(consumo)

        db.add_all(objetos)
        db.commit()

    except Exception as e:
        db.rollback()
        raise e