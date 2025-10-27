import flet as ft
from db import get_connection

def TaxaEntregaView(page: ft.Page):
    """
    Página para gerenciar taxas de entrega.
    """

    taxa_list = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Cidade")),
            ft.DataColumn(ft.Text("Bairro")),
            ft.DataColumn(ft.Text("Estado")),
            ft.DataColumn(ft.Text("Valor")),
        ],
        rows=[],
        expand=True,
    )

    def load_taxas():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT cidade, bairro, estado, valor FROM taxa_entrega")
        taxas = cursor.fetchall()
        conn.close()

        taxa_list.rows.clear()
        for taxa in taxas:
            cidade, bairro, estado, valor = taxa
            taxa_list.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(cidade)),
                        ft.DataCell(ft.Text(bairro)),
                        ft.DataCell(ft.Text(estado)),
                        ft.DataCell(ft.Text(f"R$ {valor:.2f}")),
                    ]
                )
            )
        page.update()

    load_taxas()

    return ft.Column(
        [
            ft.Text("Taxas de Entrega", size=24, weight="bold"),
            taxa_list,
        ],
        expand=True,
    )