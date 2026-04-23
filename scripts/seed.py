import pandas as pd
from app.core.database import SessionLocal
from app.services.consumo_service import process_file


samples = [
    "data/uploads/planilha_clientes.xlsx",
    "data/uploads/planilha_consumos.xlsx",
    "data/uploads/teste.xlsx"
]

db = SessionLocal()

try:
    for sample in samples:

        try:
            df = pd.read_excel(sample)
        except Exception:
            print(f"Erro ao ler {sample}")
            continue

        if df.empty:
            continue

        print(f"Seeding {sample}...")

        process_file(db, df)

finally:
    db.close()

print("Seed complete 🔥")