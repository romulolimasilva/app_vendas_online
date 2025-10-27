import flet as ft
from db import get_produto_by_id, update_produto, get_categorias_by_vendedor

def EditarProdutoView(page: ft.Page, produto_id: int):
    """
    Página para editar os detalhes de um produto.
    """
    # Busca os dados do produto para preencher o formulário
    produto = get_produto_by_id(produto_id)
    vendedor_id = page.session.get("user_id")

    # --- VERIFICAÇÃO DE SEGURANÇA ---
    if not produto or produto['vendedor_id'] != vendedor_id:
        page.go("/painel_adm")
        return ft.View(f"/editar_produto/{produto_id}", [ft.Text("Produto não encontrado ou acesso negado.")])

    # --- FUNÇÕES E COMPONENTES ---
    def show_snackbar(message, color):
        page.snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor=color)
        page.snack_bar.open = True
        page.update()

    def on_dialog_result(e: ft.FilePickerResultEvent):
        if e.files:
            path_imagem_produto.value = e.files[0].path
            nome_imagem_produto.value = f"Nova imagem: {e.files[0].name}"
            remover_imagem_chk.value = False # Desmarca a remoção se uma nova imagem for selecionada
            page.update()

    file_picker = ft.FilePicker(on_result=on_dialog_result)
    page.overlay.append(file_picker)

    # Campos de entrada preenchidos com os dados do produto
    nome_input = ft.TextField(label="Nome do Produto", value=produto['nome'])
    descricao_input = ft.TextField(label="Descrição", value=produto.get('descricao', ''), multiline=True, min_lines=3)
    categoria_input = ft.Dropdown(label="Categoria", value=str(produto['categoria_id']))
    preco_input = ft.TextField(label="Preço", value=f"{produto['preco']:.2f}", prefix="R$", keyboard_type=ft.KeyboardType.NUMBER)
    quantidade_input = ft.TextField(label="Quantidade em Estoque", value=str(produto['quantidade']), keyboard_type=ft.KeyboardType.NUMBER)
    
    path_imagem_produto = ft.Text(value="", visible=False)
    nome_imagem_produto = ft.Text(f"Imagem atual: {'Sim' if produto.get('img') else 'Nenhuma'}")
    remover_imagem_chk = ft.Checkbox(label="Remover imagem atual", value=False)

    def carregar_categorias():
        categorias_db = get_categorias_by_vendedor(vendedor_id)
        categoria_input.options.clear()
        for cat_id, cat_nome in categorias_db:
            categoria_input.options.append(ft.dropdown.Option(key=str(cat_id), text=cat_nome))
        page.update()

    carregar_categorias()

    def salvar_produto(e):
        try:
            preco_val = float(preco_input.value.replace(',', '.'))
            quantidade_val = int(quantidade_input.value)
        except (ValueError, TypeError):
            show_snackbar("Preço e Quantidade devem ser números válidos.", ft.Colors.RED)
            return

        success = update_produto(
            produto_id=produto_id,
            nome=nome_input.value,
            descricao=descricao_input.value,
            categoria_id=int(categoria_input.value) if categoria_input.value else None,
            preco=preco_val,
            quantidade=quantidade_val,
            img_path=path_imagem_produto.value,
            remover_img=remover_imagem_chk.value
        )

        if success:
            show_snackbar(f"Produto '{nome_input.value}' atualizado com sucesso!", ft.Colors.GREEN)
            page.go("/painel_adm")
        else:
            show_snackbar("Erro ao atualizar o produto.", ft.Colors.RED)

    return ft.View(
        f"/editar_produto/{produto_id}",
        [
            ft.Column(
                width=800,
                controls=[
                    ft.Text(f"Editar Produto: {produto['nome']}", size=32, weight="bold"),
                    ft.Divider(height=20),
                    nome_input,
                    descricao_input,
                    categoria_input,
                    ft.Row([
                        ft.Column([preco_input], expand=True),
                        ft.Column([quantidade_input], expand=True),
                    ]),
                    ft.Text("Imagem do Produto", weight="bold"),
                    ft.Row([
                        ft.ElevatedButton(
                            "Alterar Imagem",
                            icon=ft.Icons.UPLOAD_FILE,
                            on_click=lambda _: file_picker.pick_files(allow_multiple=False, allowed_extensions=["jpg", "jpeg", "png"])
                        ),
                        nome_imagem_produto,
                    ]),
                    remover_imagem_chk,
                    ft.Divider(height=20, color="transparent"),
                    ft.Row([
                        ft.FilledButton("Salvar Alterações", icon=ft.Icons.SAVE, on_click=salvar_produto),
                        ft.OutlinedButton("Cancelar", icon=ft.Icons.CANCEL, on_click=lambda e: page.go("/painel_adm")),
                    ], spacing=10),
                ],
                spacing=15,
            )
        ],
        padding=50,
        scroll=ft.ScrollMode.AUTO,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )