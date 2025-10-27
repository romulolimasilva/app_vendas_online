import flet as ft
import base64
from db import create_pedido

def CarrinhoComprasView(page: ft.Page):
    """
    Página do carrinho de compras (modo carrossel horizontal).
    """

    # Container horizontal com scroll
    lista_itens_carrinho = ft.Container(
        content=ft.Row(
            controls=[],
            spacing=10,
            alignment=ft.MainAxisAlignment.START,
            scroll=ft.ScrollMode.ALWAYS,  # habilita rolagem horizontal
        ),
        expand=True,
    )

    total_carrinho_text = ft.Text(weight="bold", size=20)
    checkout_button = ft.FilledButton(
        "Finalizar Compra",
        icon=ft.Icons.PAYMENT,
        height=50,
        expand=True,
        on_click=lambda e: go_to_checkout(e),
    )

    progress_bar = ft.ProgressBar(visible=True)

    # --- COMPONENTES DO FORMULÁRIO DE ENDEREÇO ---
    rua_entrega = ft.TextField(label="Rua / Logradouro", expand=True)
    numero_entrega = ft.TextField(label="Número", width=150)
    bairro_entrega = ft.TextField(label="Bairro", expand=True)
    cidade_entrega = ft.TextField(label="Cidade", expand=True)
    estado_entrega = ft.TextField(label="Estado (UF)", width=100)
    cep_entrega = ft.TextField(label="CEP", width=150, keyboard_type=ft.KeyboardType.NUMBER)

    form_endereco = ft.Container(
        visible=False,  # Começa invisível
        padding=ft.padding.symmetric(vertical=20),
        content=ft.Column(
            [
                ft.Text("Endereço de Entrega", size=24, weight="bold"),
                ft.Row([rua_entrega, numero_entrega]),
                ft.Row([bairro_entrega, cidade_entrega, estado_entrega]),
                cep_entrega,
                ft.Divider(height=20, color="transparent"),
                ft.FilledButton("Confirmar Pedido", icon=ft.Icons.CHECK_CIRCLE_OUTLINE, height=50, on_click=lambda e: confirmar_pedido_click(e), expand=True)
            ],
            spacing=15
        )
    )

    # --- Funções ---
    def update_cart_item(e, produto_id, change):
        carrinho_atual = page.session.get("cart")
        if str(produto_id) in carrinho_atual:
            carrinho_atual[str(produto_id)]["quantity"] += change
            if carrinho_atual[str(produto_id)]["quantity"] <= 0:
                del carrinho_atual[str(produto_id)]
        page.session.set("cart", carrinho_atual)
        build_cart_view()

    def remove_cart_item(e, produto_id):
        carrinho_atual = page.session.get("cart")
        if str(produto_id) in carrinho_atual:
            del carrinho_atual[str(produto_id)]
        page.session.set("cart", carrinho_atual)
        build_cart_view()

    def build_cart_view():
        progress_bar.visible = True
        page.update()

        carrinho_atual = page.session.get("cart") or {}
        lista_itens_carrinho.content.controls.clear()
        total_carrinho = 0

        if not carrinho_atual:
            lista_itens_carrinho.content.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(ft.Icons.SHOPPING_CART_OUTLINED, size=80, color=ft.Colors.GREY_400),
                            ft.Text("Seu carrinho está vazio.", size=20, color=ft.Colors.GREY_600),
                            ft.Text("Adicione produtos para vê-los aqui.", color=ft.Colors.GREY_500),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    alignment=ft.alignment.center,
                    expand=True,
                )
            )
        else:
            for produto_id, detalhes in carrinho_atual.items():
                subtotal = detalhes["price"] * detalhes["quantity"]
                total_carrinho += subtotal

                lista_itens_carrinho.content.controls.append(
                    ft.Card(
                        elevation=2,
                        content=ft.Container(
                            width=220,
                            padding=10,
                            content=ft.Column(
                                [
                                    ft.Image(
                                        src_base64=detalhes["img"] if detalhes["img"] else None,
                                        src="/icons/no-image.png" if not detalhes["img"] else None,
                                        width=200,
                                        height=130,
                                        fit=ft.ImageFit.COVER,
                                        border_radius=ft.border_radius.all(8),
                                    ),
                                    ft.Text(detalhes["name"], weight="bold", size=14, text_align=ft.TextAlign.CENTER),
                                    ft.Text(f"R$ {detalhes['price']:.2f}", color=ft.Colors.GREEN, size=12),
                                    ft.Row(
                                        [
                                            ft.IconButton(ft.Icons.REMOVE, icon_size=16, on_click=lambda e, pid=produto_id: update_cart_item(e, pid, -1)),
                                            ft.Text(str(detalhes["quantity"]), size=14),
                                            ft.IconButton(ft.Icons.ADD, icon_size=16, on_click=lambda e, pid=produto_id: update_cart_item(e, pid, 1)),
                                        ],
                                        alignment=ft.MainAxisAlignment.CENTER,
                                    ),
                                    ft.Row(
                                        [
                                            ft.Text(f"Subtotal: R$ {subtotal:.2f}", size=12, weight="bold"),
                                            ft.IconButton(ft.Icons.DELETE_FOREVER, icon_color=ft.Colors.RED_400, icon_size=18, on_click=lambda e, pid=produto_id: remove_cart_item(e, pid))
                                        ],
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    ),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=5,
                            ),
                        ),
                    )
                )

        total_carrinho_text.value = f"Total: R$ {total_carrinho:.2f}"
        checkout_button.disabled = not carrinho_atual
        progress_bar.visible = False
        page.update()

    def go_to_checkout(e):
        # Mostra o formulário de endereço e esconde o botão de finalizar compra
        form_endereco.visible = True
        checkout_button.visible = False
        page.update()

    def show_snackbar(message, color):
        page.snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor=color)
        page.snack_bar.open = True
        page.update()

    def confirmar_pedido_click(e):
        # Validação simples
        if not all([rua_entrega.value, numero_entrega.value, bairro_entrega.value, cidade_entrega.value, estado_entrega.value, cep_entrega.value]):
            page.snack_bar = ft.SnackBar(content=ft.Text("Por favor, preencha todos os campos do endereço."), bgcolor=ft.Colors.ORANGE)
            page.snack_bar.open = True
            page.update()
            return

        carrinho_atual = page.session.get("cart") or {}
        if not carrinho_atual:
            show_snackbar("Seu carrinho está vazio.", ft.Colors.RED)
            return

        # Assume que todos os produtos no carrinho são do mesmo vendedor
        # Em um cenário real, o carrinho poderia ser agrupado por vendedor
        primeiro_produto_id = next(iter(carrinho_atual))
        vendedor_id = carrinho_atual[primeiro_produto_id].get("vendedor_id")

        total_pedido = sum(item['price'] * item['quantity'] for item in carrinho_atual.values())
        
        endereco = {
            "rua": rua_entrega.value, "numero": numero_entrega.value, "bairro": bairro_entrega.value,
            "cidade": cidade_entrega.value, "estado": estado_entrega.value, "cep": cep_entrega.value
        }
        
        # Prepara a lista de itens para a função do DB
        itens_pedido = [{"id": prod_id, **detalhes} for prod_id, detalhes in carrinho_atual.items()]

        pedido_id = create_pedido(
            comprador_id=page.session.get("user_id"),
            vendedor_id=vendedor_id,
            total=total_pedido,
            endereco=endereco,
            itens=itens_pedido
        )

        if pedido_id:
            page.session.set("cart", {}) # Limpa o carrinho
            show_snackbar(f"Pedido #{pedido_id} realizado com sucesso!", ft.Colors.GREEN)
            page.go("/lojas") # Redireciona para a lista de lojas
        else:
            show_snackbar("Ocorreu um erro ao processar seu pedido. Tente novamente.", ft.Colors.RED)

    build_cart_view()

    return ft.View(
        "/carrinho",
        [
            ft.Text("Carrinho de Compras", size=32, weight="bold"),
            progress_bar,
            ft.Divider(),
            lista_itens_carrinho,  # agora com scroll horizontal
            ft.Divider(),
            ft.Row([total_carrinho_text], alignment=ft.MainAxisAlignment.END),
            ft.Container(height=10),
            # Linha que contém o botão de checkout ou o formulário de endereço
            ft.Row([checkout_button]),
            form_endereco,
        ],
        padding=ft.padding.symmetric(horizontal=50, vertical=20),
        scroll=ft.ScrollMode.AUTO,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
