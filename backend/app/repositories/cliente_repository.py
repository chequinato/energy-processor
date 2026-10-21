from app.models.cliente import Cliente


def get_or_create_cliente(db, nome):
    cliente = db.query(Cliente).filter(Cliente.nome == nome).first()

    if cliente:
        return cliente

    novo = Cliente(nome=nome)
    db.add(novo)
    db.flush()  # gera o ID sem fechar a transação

    return novo


def get_or_create_clientes(db, nomes):
    """
    Versão em lote: resolve todos os clientes com uma consulta só,
    criando os que não existem. Retorna {nome: Cliente}.
    """
    nomes = set(nomes)
    existentes = db.query(Cliente).filter(Cliente.nome.in_(nomes)).all()
    por_nome = {c.nome: c for c in existentes}

    novos = [Cliente(nome=nome) for nome in nomes - por_nome.keys()]
    if novos:
        db.add_all(novos)
        db.flush()
        por_nome.update({c.nome: c for c in novos})

    return por_nome
