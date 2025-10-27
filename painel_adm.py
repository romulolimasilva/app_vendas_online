import flet as ft
from db import (create_produto, create_categoria, get_categorias_by_vendedor, get_produtos_by_vendedor, 
                update_categoria, delete_categoria, cadastrar_taxa_entrega, get_taxas_by_vendedor, 
                delete_taxa_entrega, get_pedidos_by_vendedor)
from datetime import datetime

def PainelAdmView(page: ft.Page):
    # --- VERIFICAÇÃO DE SEGURANÇA ---
    # Redireciona para o login se não for um vendedor logado
    if page.session.get("user_type") != "vendedor":
        page.go("/login")
        # Retorna uma View vazia para evitar que o resto do código seja renderizado
        return ft.View(
            "/painel_adm",
            [ft.Text("Acesso negado. Redirecionando...", weight="bold")],
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    # --- FUNÇÕES GERAIS ---
    def show_snackbar(message, color):
        page.snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor=color)
        page.snack_bar.open = True
        page.update()

    # --- LÓGICA DO FILE PICKER (UPLOAD DE IMAGEM) ---
    def on_dialog_result(e: ft.FilePickerResultEvent):
        if e.files:
            # Pega o caminho do primeiro arquivo selecionado
            path_imagem_produto.value = e.files[0].path
            nome_imagem_produto.value = e.files[0].name
            page.update()

    file_picker = ft.FilePicker(on_result=on_dialog_result)
    page.overlay.append(file_picker)  # Adiciona o file picker à página

    # --- COMPONENTES DA ABA "CADASTRAR PRODUTO" ---
    nome_produto = ft.TextField(label="Nome do Produto", autofocus=True)
    descricao_produto = ft.TextField(
        label="Descrição", multiline=True, min_lines=3)
    categoria_produto = ft.Dropdown(label="Categoria")
    preco_produto = ft.TextField(
        label="Preço (ex: 99.90)", prefix="R$", keyboard_type=ft.KeyboardType.NUMBER)
    quantidade_produto = ft.TextField(
        label="Quantidade em Estoque", keyboard_type=ft.KeyboardType.NUMBER)
    # Armazena o caminho do arquivo
    path_imagem_produto = ft.Text(value="", visible=False)
    nome_imagem_produto = ft.Text("Nenhuma imagem selecionada.")

    def cadastrar_produto_click(e):
        vendedor_id = page.session.get("user_id")

        # Validações
        if not all([nome_produto.value, categoria_produto.value, preco_produto.value, quantidade_produto.value]):
            show_snackbar(
                "Todos os campos, exceto descrição e imagem, são obrigatórios.", ft.Colors.ORANGE)
            return
        try:
            # Valida se preço e quantidade são números válidos
            float(preco_produto.value)
            int(quantidade_produto.value)
        except ValueError:
            show_snackbar(
                "Preço e Quantidade devem ser números válidos.", ft.Colors.RED)
            return

        success = create_produto(
            vendedor_id=vendedor_id,
            nome=nome_produto.value,
            descricao=descricao_produto.value,
            categoria_id=int(categoria_produto.value),
            preco=float(preco_produto.value),
            quantidade=int(quantidade_produto.value),
            img_path=path_imagem_produto.value
        )

        if success:
            show_snackbar("Produto cadastrado com sucesso!", ft.Colors.GREEN)
            # Limpar campos após o cadastro
            for field in [nome_produto, descricao_produto, categoria_produto, preco_produto, quantidade_produto, path_imagem_produto, nome_imagem_produto]:
                field.value = ""
            nome_imagem_produto.value = "Nenhuma imagem selecionada."
            page.update()
        else:
            show_snackbar(
                "Erro ao cadastrar o produto. Tente novamente.", ft.Colors.RED)

    # --- COMPONENTES DA ABA "GERENCIAR PRODUTOS" ---
    lista_produtos = ft.ListView(expand=True, spacing=10)

    def editar_produto_click(e):
        produto_id = e.control.data
        page.go(f"/editar_produto/{produto_id}")

    def carregar_produtos():
        """Busca produtos no DB e atualiza a ListView."""
        vendedor_id = page.session.get("user_id")
        produtos_db = get_produtos_by_vendedor(vendedor_id)

        lista_produtos.controls.clear()
        if not produtos_db:
            lista_produtos.controls.append(
                ft.Text("Você ainda não cadastrou nenhum produto."))
        else:
            for produto in produtos_db:
                lista_produtos.controls.append(
                    ft.Card(
                        content=ft.ListTile(
                            title=ft.Text(produto['nome']),
                            subtitle=ft.Text(
                                f"R$ {produto['preco']:.2f} - Estoque: {produto['quantidade']}"),
                            trailing=ft.IconButton(
                                icon=ft.Icons.EDIT, tooltip="Editar Produto", data=produto['id'], on_click=editar_produto_click
                            ),
                        )
                    )
                )
        page.update()

    # --- COMPONENTES DA ABA "GERENCIAR CATEGORIAS" ---
    nome_nova_categoria = ft.TextField(label="Nome da Nova Categoria")
    lista_categorias = ft.Row(wrap=True, spacing=10, run_spacing=10)

    def open_edit_dialog(cat_id, cat_nome):
        """Abre um diálogo para editar o nome da categoria."""
        edit_field = ft.TextField(
            label="Novo nome da categoria", value=cat_nome)

        def save_edit(e):
            novo_nome = edit_field.value
            if not novo_nome:
                show_snackbar("O nome não pode ser vazio.", ft.Colors.ORANGE)
                return

            vendedor_id = page.session.get("user_id")
            if update_categoria(cat_id, vendedor_id, novo_nome):
                show_snackbar(
                    "Categoria atualizada com sucesso!", ft.Colors.GREEN)
                dialog.open = False
                carregar_categorias()
            else:
                show_snackbar(
                    "Erro ao atualizar. O nome pode já existir.", ft.Colors.RED)
            page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Editar Categoria"),
            content=edit_field,
            actions=[
                ft.TextButton(
                    "Cancelar", on_click=lambda e: close_dialog(dialog)),
                ft.FilledButton("Salvar", on_click=save_edit),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.dialog = dialog
        dialog.open = True
        page.update()

    def open_delete_dialog(cat_id, cat_nome):
        """Abre um diálogo de confirmação para deletar a categoria."""
        def delete_confirmed(e):
            vendedor_id = page.session.get("user_id")
            if delete_categoria(cat_id, vendedor_id):
                show_snackbar(
                    f"Categoria '{cat_nome}' deletada com sucesso.", ft.Colors.GREEN)
                dialog.open = False
                carregar_categorias()
            else:
                show_snackbar("Erro ao deletar a categoria.", ft.Colors.RED)
            page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar Exclusão"),
            content=ft.Text(
                f"Tem certeza que deseja excluir a categoria '{cat_nome}'?\nOs produtos nesta categoria não serão excluídos, mas ficarão sem categoria."),
            actions=[
                ft.TextButton(
                    "Cancelar", on_click=lambda e: close_dialog(dialog)),
                ft.FilledButton(
                    "Excluir", on_click=delete_confirmed, bgcolor=ft.Colors.RED),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.dialog = dialog
        dialog.open = True
        page.update()

    def close_dialog(dialog):
        dialog.open = False
        page.update()

    def carregar_categorias():
        """Busca categorias no DB e atualiza o Dropdown e a Lista."""
        vendedor_id = page.session.get("user_id")
        categorias_db = get_categorias_by_vendedor(vendedor_id)

        # Atualiza o Dropdown de produtos
        categoria_produto.options.clear()
        for cat_id, cat_nome in categorias_db:
            categoria_produto.options.append(
                ft.dropdown.Option(key=str(cat_id), text=cat_nome))
        if categoria_produto.page is not None:
            categoria_produto.update()

        # Atualiza a lista de gerenciamento
        lista_categorias.controls.clear()
        if not categorias_db:
            lista_categorias.controls.append(
                ft.Text("Nenhuma categoria cadastrada."))
        else:
            for cat_id, cat_nome in categorias_db:
                lista_categorias.controls.append(
                    ft.Chip(
                        label=ft.Text(cat_nome),
                        bgcolor=ft.Colors.BLUE_GREY_100,
                        on_delete=lambda e, cat_id=cat_id, cat_nome=cat_nome: open_delete_dialog(cat_id, cat_nome),
                        delete_icon_tooltip="Excluir Categoria",
                        data=cat_id,
                        # Adicionando a funcionalidade de edição ao clicar no Chip
                        on_click=lambda e, cat_id=cat_id, cat_nome=cat_nome: open_edit_dialog(cat_id, cat_nome),
                        tooltip="Clique para editar"
                    )
                )

        page.update()

    def cadastrar_categoria_click(e):
        if not nome_nova_categoria.value:
            show_snackbar("Digite o nome da categoria.", ft.Colors.RED)
            return

        vendedor_id = page.session.get("user_id")
        if create_categoria(vendedor_id, nome_nova_categoria.value):
            show_snackbar("Categoria cadastrada com sucesso!", ft.Colors.GREEN)
            nome_nova_categoria.value = ""
            carregar_categorias()  # Recarrega a lista e o dropdown
        else:
            show_snackbar(
                "Você já possui uma categoria com este nome.", ft.Colors.RED)
        page.update()

    # --- COMPONENTES DA ABA "TAXAS DE ENTREGA" ---
    cidade_taxa = ft.TextField(label="Cidade")
    bairro_taxa = ft.TextField(label="Bairro")
    estado_taxa = ft.TextField(label="Estado (UF)", width=100)
    valor_taxa = ft.TextField(label="Valor da Entrega", prefix="R$", keyboard_type=ft.KeyboardType.NUMBER)

    tabela_taxas = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Cidade")),
            ft.DataColumn(ft.Text("Bairro")),
            ft.DataColumn(ft.Text("Valor")),
            ft.DataColumn(ft.Text("Ações")),
        ],
        rows=[],
    )

    def carregar_taxas():
        vendedor_id = page.session.get("user_id")
        taxas_db = get_taxas_by_vendedor(vendedor_id)
        tabela_taxas.rows.clear()
        if not taxas_db:
            tabela_taxas.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text("Nenhuma taxa cadastrada.", colspan=4, text_align="center"))]))
        else:
            for taxa in taxas_db:
                tabela_taxas.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(taxa['cidade'])),
                        ft.DataCell(ft.Text(taxa['bairro'])),
                        ft.DataCell(ft.Text(f"R$ {taxa['valor']:.2f}")),
                        ft.DataCell(ft.IconButton(
                            icon=ft.Icons.DELETE,
                            icon_color=ft.Colors.RED,
                            tooltip="Excluir Taxa",
                            data=taxa['id'],
                            on_click=excluir_taxa_click
                        )),
                    ])
                )
        page.update()

    def cadastrar_taxa_click(e):
        vendedor_id = page.session.get("user_id")
        if not all([cidade_taxa.value, bairro_taxa.value, estado_taxa.value, valor_taxa.value]):
            show_snackbar("Todos os campos da taxa de entrega são obrigatórios.", ft.Colors.ORANGE)
            return
        try:
            valor = float(valor_taxa.value.replace(',', '.'))
        except ValueError:
            show_snackbar("O valor da taxa deve ser um número válido.", ft.Colors.RED)
            return

        cadastrar_taxa_entrega(
            vendedor_id=vendedor_id,
            cidade=cidade_taxa.value,
            bairro=bairro_taxa.value,
            estado=estado_taxa.value,
            valor=valor
        )
        show_snackbar("Taxa de entrega cadastrada com sucesso!", ft.Colors.GREEN)
        # Limpar campos e recarregar a lista
        cidade_taxa.value = ""
        bairro_taxa.value = ""
        estado_taxa.value = ""
        valor_taxa.value = ""
        carregar_taxas()

    def excluir_taxa_click(e):
        taxa_id = e.control.data
        vendedor_id = page.session.get("user_id")
        if delete_taxa_entrega(taxa_id, vendedor_id):
            show_snackbar("Taxa de entrega excluída com sucesso!", ft.Colors.GREEN)
            carregar_taxas()
        else:
            show_snackbar("Erro ao excluir a taxa.", ft.Colors.RED)

    # --- COMPONENTES DA ABA "PEDIDOS RECEBIDOS" ---
    lista_pedidos = ft.ListView(expand=True, spacing=10)

    def carregar_pedidos():
        vendedor_id = page.session.get("user_id")
        pedidos_db = get_pedidos_by_vendedor(vendedor_id)
        lista_pedidos.controls.clear()

        if not pedidos_db:
            lista_pedidos.controls.append(ft.Text("Você ainda não recebeu nenhum pedido."))
        else:
            for pedido in pedidos_db:
                # Formata a data para um formato mais legível
                # O formato do timestamp do SQLite é 'YYYY-MM-DD HH:MM:SS'
                try:
                    data_obj = datetime.strptime(pedido['data_pedido'], '%Y-%m-%d %H:%M:%S')
                    data_formatada = data_obj.strftime('%d/%m/%Y %H:%M')
                except (ValueError, TypeError):
                    data_formatada = pedido['data_pedido'] # Mostra a data original se a conversão falhar
                
                lista_pedidos.controls.append(
                    ft.Card(
                        ft.Container(
                            padding=15,
                            content=ft.Column([
                                ft.Text(f"Pedido #{pedido['id']} - {data_formatada}", weight="bold"),
                                ft.Text(f"Comprador: {pedido['comprador_nome']}"),
                                ft.Text(f"Total: R$ {pedido['total']:.2f}", color=ft.Colors.GREEN_700, weight="bold"),
                                ft.Text(f"Status: {pedido['status']}"),
                                ft.Container(
                                    content=ft.Text("Endereço de Entrega:", weight="bold"),
                                    margin=ft.margin.only(top=10)
                                ),
                                ft.Text(f"{pedido['rua']}, {pedido['numero']} - {pedido['bairro']}"),
                                ft.Text(f"{pedido['cidade']} - {pedido['estado']}, CEP: {pedido['cep']}"),
                            ])
                        )
                    )
                )
        page.update()


    # Carrega as categorias ao iniciar a view
    def on_tab_change(e):
        selected_tab = e.control.selected_index
        if selected_tab == 0:  # Aba "Cadastrar Produto"
            carregar_categorias()
        elif selected_tab == 1:  # Aba "Gerenciar Produtos"
            carregar_produtos()
        elif selected_tab == 2:  # Aba "Gerenciar Categorias"
            carregar_categorias()
        elif selected_tab == 3: # Aba "Taxas de Entrega"
            carregar_taxas()
        elif selected_tab == 4: # Aba "Pedidos Recebidos"
            carregar_pedidos()

    # Carrega as categorias para o dropdown de cadastro assim que a view é criada
    carregar_categorias()

    # --- LAYOUT DA VIEW ---
    return ft.View(
        "/painel_adm",
        [
            ft.Column(  # <-- Adicionado um Column para envolver o conteúdo
                width=800,
                controls=[
                    ft.Text("Painel do Vendedor", size=32, weight="bold"),
                    ft.Text(
                        f"Bem-vindo, {page.session.get('user_name')}!", size=16, color=ft.Colors.GREY_600),
                    ft.Tabs(
                        selected_index=0,
                        animation_duration=300,
                        on_change=on_tab_change,
                        tabs=[
                            ft.Tab(
                                text="Cadastrar Produto",
                                icon=ft.Icons.ADD_SHOPPING_CART,
                                content=ft.Container(
                                    ft.Column([
                                        nome_produto,
                                        descricao_produto,
                                        categoria_produto,
                                        ft.Row([
                                            ft.Column(
                                                [preco_produto], expand=True),
                                            ft.Column(
                                                [quantidade_produto], expand=True),
                                        ]),
                                        ft.Text("Imagem do Produto",
                                                weight="bold"),
                                        ft.Row([
                                            ft.ElevatedButton(
                                                "Selecionar Imagem",
                                                icon=ft.Icons.UPLOAD_FILE,
                                                on_click=lambda _: file_picker.pick_files(
                                                    allow_multiple=False, allowed_extensions=["jpg", "jpeg", "png"])
                                            ),
                                            nome_imagem_produto,
                                        ]),
                                        ft.Divider(
                                            height=20, color="transparent"),
                                        ft.FilledButton(
                                            "Cadastrar Produto", on_click=cadastrar_produto_click, icon=ft.Icons.ADD),
                                    ], spacing=15),
                                    padding=ft.padding.symmetric(vertical=20)
                                )
                            ),
                            ft.Tab(
                                text="Gerenciar Produtos",
                                icon=ft.Icons.EDIT_SQUARE,
                                content=ft.Container(
                                    content=lista_produtos,
                                    padding=ft.padding.symmetric(vertical=20),
                                )
                            ),
                            ft.Tab(
                                text="Gerenciar Categorias",
                                icon=ft.Icons.CATEGORY,
                                content=ft.Container(
                                    ft.Column([
                                        ft.Text(
                                            "Adicionar Nova Categoria", weight="bold"),
                                        ft.Row([
                                            ft.Column(
                                                [nome_nova_categoria], expand=True),
                                            ft.FilledButton(
                                                "Adicionar",
                                                on_click=cadastrar_categoria_click,
                                                icon=ft.Icons.ADD,
                                            ),
                                        ]),
                                        ft.Divider(),
                                        ft.Text("Categorias Existentes",
                                                weight="bold"),
                                        ft.Container(
                                            content=ft.Column([lista_categorias], scroll=ft.ScrollMode.AUTO),
                                            border=ft.border.all(
                                                1, ft.Colors.GREY_300),
                                            border_radius=ft.border_radius.all(
                                                5),
                                            padding=10,
                                            height=200,
                                            # Garante que o conteúdo se expanda para preencher o container
                                            expand=True,
                                        )
                                    ], spacing=15),
                                    padding=ft.padding.symmetric(horizontal=20)
                                )

                            ),
                            ft.Tab(
                                text="Taxas de Entrega",
                                icon=ft.Icons.LOCAL_SHIPPING,
                                content=ft.Container(
                                    ft.Column([
                                        ft.Text("Cadastrar Nova Taxa de Entrega", weight="bold"),
                                        ft.Row([
                                            ft.Column([cidade_taxa], expand=True),
                                            ft.Column([bairro_taxa], expand=True),
                                        ]),
                                        ft.Row([
                                            ft.Column([estado_taxa], expand=True),
                                            ft.Column([valor_taxa], expand=True),
                                        ]),
                                        ft.FilledButton(
                                            "Cadastrar Taxa",
                                            on_click=cadastrar_taxa_click,
                                            icon=ft.Icons.ADD
                                        ),
                                        ft.Divider(),
                                        ft.Text("Taxas Cadastradas", weight="bold"),
                                        tabela_taxas,
                                    ], spacing=15),
                                    padding=ft.padding.symmetric(vertical=20))
                            ),
                            ft.Tab(
                                text="Pedidos Recebidos",
                                icon=ft.Icons.INVENTORY,
                                content=ft.Container(
                                    content=lista_pedidos,
                                    padding=ft.padding.symmetric(vertical=20),
                                )
                            ),
                        ],
                        expand=1,
                    ),
                ]
            )
        ],
        scroll=ft.ScrollMode.AUTO,
        vertical_alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        padding=50,
    )
