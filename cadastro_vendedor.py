import flet as ft
from db import create_vendedor


def CadastroVendedorView(page: ft.Page):
    page.title = "Cadastro de Vendedor"

    # --- CAMPOS DO FORMULÁRIO ---
    name = ft.TextField(label="Nome Completo / Razão Social", autofocus=True)
    email = ft.TextField(label="E-mail", keyboard_type=ft.KeyboardType.EMAIL)
    telefone = ft.TextField(label="Telefone / Celular", keyboard_type=ft.KeyboardType.PHONE)
    password = ft.TextField(label="Crie uma Senha", password=True, can_reveal_password=True)

    # Campos que mudam (CPF/CNPJ)
    cpf_field = ft.TextField(label="CPF", visible=True, keyboard_type=ft.KeyboardType.NUMBER)
    cnpj_field = ft.TextField(label="CNPJ", visible=False, keyboard_type=ft.KeyboardType.NUMBER)

    # Campos de endereço
    cep = ft.TextField(label="CEP", width=150, keyboard_type=ft.KeyboardType.NUMBER)
    rua = ft.TextField(label="Rua / Logradouro", expand=True)
    numero = ft.TextField(label="Número", width=100)
    bairro = ft.TextField(label="Bairro")
    cidade = ft.TextField(label="Cidade")
    estado = ft.TextField(label="Estado (UF)", width=100)

    def toggle_cpf_cnpj(e):
        """Alterna a visibilidade dos campos CPF e CNPJ."""
        if e.control.value == "Pessoa Física":
            cpf_field.visible = True
            cnpj_field.visible = False
        else:
            cpf_field.visible = False
            cnpj_field.visible = True
        page.update()

    tipo_pessoa = ft.RadioGroup(
        content=ft.Row([
            ft.Radio(value="Pessoa Física", label="Pessoa Física"),
            ft.Radio(value="Pessoa Jurídica", label="Pessoa Jurídica"),
        ]),
        value="Pessoa Física",  # Valor padrão
        on_change=toggle_cpf_cnpj
    )

    def show_snackbar(message, color):
        page.snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor=color)
        page.snack_bar.open = True
        page.update()

    def cadastrar_click(e):
        """Função chamada ao clicar no botão de cadastrar."""
        # Validação simples para campos obrigatórios
        required_fields = [name, email, telefone, password, cep, rua, numero, bairro, cidade, estado]
        if tipo_pessoa.value == "Pessoa Física":
            required_fields.append(cpf_field)
        else:
            required_fields.append(cnpj_field)

        for field in required_fields:
            if not field.value:
                show_snackbar(f"O campo '{field.label}' é obrigatório.", ft.Colors.RED_400)
                field.focus()
                return

        # Coleta os dados e chama a função do banco
        success = create_vendedor(
            tipo_pessoa=tipo_pessoa.value,
            name=name.value,
            email=email.value,
            cnpj=cnpj_field.value if tipo_pessoa.value == "Pessoa Jurídica" else None,
            cpf=cpf_field.value if tipo_pessoa.value == "Pessoa Física" else None,
            telefone=telefone.value,
            rua=rua.value,
            numero=numero.value,
            bairro=bairro.value,
            cidade=cidade.value,
            estado=estado.value,
            cep=cep.value,
            password=password.value  # Futuramente, usar hash para a senha
        )

        if success:
            show_snackbar("Vendedor cadastrado com sucesso!", ft.Colors.GREEN_400)
            page.go("/login")  # Redireciona para o login após o sucesso
        else:
            show_snackbar("Erro ao cadastrar. Verifique se o e-mail, CPF ou CNPJ já existem.", ft.Colors.RED_400)

    # --- LAYOUT DA VIEW ---
    return ft.View(
        '/cadastro_vendedor',
        [
            ft.Column(
                [
                    ft.Text("Crie sua Conta de Vendedor", size=32, weight="bold", text_align="center"),
                    ft.Text("Preencha os campos abaixo para começar a vender.", size=16, color=ft.Colors.GREY_600, text_align="center"),
                    ft.Divider(height=20, color="transparent"),

                    ft.Text("Tipo de Conta", weight="bold"),
                    tipo_pessoa,

                    ft.ResponsiveRow(
                        [
                            ft.Column([ft.Text("Informações Pessoais", weight="bold"), name, email, telefone, password], col={"md": 6}),
                            ft.Column([ft.Text("Documento", weight="bold"), cpf_field, cnpj_field], col={"md": 6}),
                        ],
                        spacing=20,
                        run_spacing=20,
                    ),

                    ft.Divider(height=20),
                    ft.Text("Endereço", size=20, weight="bold"),

                    ft.ResponsiveRow(
                        [
                            ft.Column([cep], col={"sm": 4, "md": 2}),
                            ft.Column([rua], col={"sm": 8, "md": 8}),
                            ft.Column([numero], col={"sm": 4, "md": 2}),
                        ],
                        spacing=10,
                        run_spacing=10,
                    ),
                    ft.ResponsiveRow(
                        [
                            ft.Column([bairro], col={"sm": 12, "md": 5}),
                            ft.Column([cidade], col={"sm": 8, "md": 5}),
                            ft.Column([estado], col={"sm": 4, "md": 2}),
                        ],
                        spacing=10,
                        run_spacing=10,
                    ),

                    ft.Divider(height=30, color="transparent"),
                    ft.FilledButton("Cadastrar", on_click=cadastrar_click, width=200, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))),
                    ft.Button ("Home", on_click=lambda e: page.go("/"), width=200, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))),
                    ft.TextButton("Já tenho uma conta", on_click=lambda e: page.go("/login")),
                ],
                spacing=15,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        ],
        padding=ft.padding.symmetric(horizontal=50, vertical=20),
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        scroll=ft.ScrollMode.AUTO,  # <-- CORREÇÃO: Mover a propriedade de scroll para a View
    )