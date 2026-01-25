import pandas as pd
from src.core.main import ClienteCSVViewer, formatar_telefone


def test_formatar_telefone_varios_casos():
    assert formatar_telefone("5511988887777") == "(11) 98888-7777"
    assert formatar_telefone("11988887777") == "(11) 98888-7777"
    assert formatar_telefone("1198887777") == "(11) 9888-7777"
    assert formatar_telefone("abc") == ""


def test_indice_coluna_telefone(qapp):
    viewer = ClienteCSVViewer()
    viewer.table.setColumnCount(3)
    viewer.table.setHorizontalHeaderLabels(["Nome", "Telefone1", "Email"])
    assert viewer._indice_coluna_telefone() == 1


def test_aplicar_filtro_atualiza_tabela(qapp):
    viewer = ClienteCSVViewer()
    df = pd.DataFrame(
        {
            "nome": ["Ana", "Bruno"],
            "telefone": ["11988887777", "21999990000"],
        }
    )
    viewer.df = df
    viewer.df_filtrado = df
    viewer._preencher_tabela(df)

    viewer.aplicar_filtro("ana")

    assert viewer.df_filtrado.shape[0] == 1
    assert viewer.table.rowCount() == 1
    # valor filtrado permanece na tabela
    assert viewer.table.item(0, 0).text() == "Ana"
