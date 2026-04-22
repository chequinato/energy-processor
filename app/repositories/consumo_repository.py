
from sqlalchemy.orm import Session
from app.models.consumo import Consumo

def save_consumos(db: Session, df):
    objetos = []

    for _, row in df.iterrows():
        consumo = Consumo(
            cliente=row["cliente"],
            consumo_kwh=row["consumo_kwh"],
            preco_mwh=row["preco_mwh"],
            custo=row["custo"]
        )
        objetos.append(consumo)

    db.add_all(objetos)
    db.commit()