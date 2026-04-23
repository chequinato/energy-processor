
from app.models.cliente import Cliente

def get_or_create_cliente(db, nome):
    cliente = db.query(Cliente).filter(Cliente.nome == nome).first()

    if cliente:
        return cliente

    novo = Cliente(nome=nome)
    db.add(novo)
    db.flush()  # gera o ID sem fechar a transação

    return novo