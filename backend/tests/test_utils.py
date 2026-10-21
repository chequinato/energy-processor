import pandas as pd
import pytest

from app.utils.calculations import calculate_metrics
from app.utils.file_reader import read_file
from app.utils.validators import validate_data


def test_calculate_metrics_adiciona_custo():
    df = pd.DataFrame({"consumo_kwh": [1000, 500], "preco_mwh": [200, 300]})

    metrics = calculate_metrics(df)

    assert list(df["custo"]) == [200.0, 150.0]
    assert metrics == {"total_consumo": 1500.0, "total_custo": 350.0}


def test_validate_data_colunas_faltando():
    df = pd.DataFrame({"cliente": ["A"], "consumo_kwh": [1]})

    with pytest.raises(ValueError, match="preco_mwh"):
        validate_data(df)


def test_validate_data_negativo():
    df = pd.DataFrame({"cliente": ["A"], "consumo_kwh": [-1], "preco_mwh": [10]})

    with pytest.raises(ValueError, match="negativo"):
        validate_data(df)


def test_validate_data_nao_numerico():
    df = pd.DataFrame({"cliente": ["A"], "consumo_kwh": ["abc"], "preco_mwh": [10]})

    with pytest.raises(ValueError, match="não numéricos"):
        validate_data(df)


def test_validate_data_ignora_nulos_em_colunas_extras():
    df = pd.DataFrame({
        "cliente": ["A"], "consumo_kwh": [1], "preco_mwh": [10], "observacao": [None]
    })

    validate_data(df)


def test_read_file_bytes_csv_com_datas_dayfirst():
    content = b"cliente,consumo_kwh,preco_mwh,data\nA,1,10,15/03/2026\nB,2,20,\n"

    df = read_file(content, "dados.csv")

    assert df.loc[0, "data"] == pd.Timestamp(2026, 3, 15)
    assert df["data"].notnull().all()


def test_read_file_formato_invalido():
    with pytest.raises(ValueError, match="Formato não suportado"):
        read_file(b"x", "dados.txt")
