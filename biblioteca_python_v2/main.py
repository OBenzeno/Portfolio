import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from livro import Livro
from usuario import Usuario
from biblioteca import Biblioteca

def main():
    biblioteca = Biblioteca()
    filename = 'biblioteca_dados.json'
    biblioteca.carregar_dados(filename)

    # ========== CONFIGURAÇÃO DE ESTILO ==========
    root = tk.Tk()
    root.title("📚 Sistema de Gerenciamento de Biblioteca")
    root.geometry("1000x700")
    root.configure(bg='#f0f4f8')

    # Paleta de cores moderna
    cor_primaria = '#1e3c5c'       # azul escuro
    cor_secundaria = '#2c7da0'      # azul médio
    cor_destaque = '#61a5c2'        # azul claro
    cor_fundo = '#ffffff'           # branco
    cor_texto = '#2d3e50'
    cor_suave = '#e9ecef'

    # Configuração do ttk
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('.', background=cor_fundo, foreground=cor_texto, font=('Segoe UI', 10))
    style.configure('TLabel', background=cor_fundo, foreground=cor_texto)
    style.configure('TButton', background=cor_secundaria, foreground='white', borderwidth=0, padding=8)
    style.map('TButton', background=[('active', cor_destaque)])
    style.configure('Treeview', background=cor_fundo, foreground=cor_texto, fieldbackground=cor_fundo)
    style.configure('Treeview.Heading', background=cor_suave, foreground=cor_texto, font=('Segoe UI', 10, 'bold'))

    # ========== FUNÇÕES AUXILIARES ==========
    def centralizar_janela(janela, largura=500, altura=400):
        janela.update_idletasks()
        x = (janela.winfo_screenwidth() // 2) - (largura // 2)
        y = (janela.winfo_screenheight() // 2) - (altura // 2)
        janela.geometry(f'{largura}x{altura}+{x}+{y}')

    # ========== FUNÇÕES DE NEGÓCIO ==========
    def cadastrar_livro():
        def confirmar():
            try:
                titulo = titulo_entry.get().strip()
                autor = autor_entry.get().strip()
                ano = int(ano_entry.get())
                num_copias = int(copias_entry.get())
                if not titulo or not autor:
                    raise ValueError("Título e autor são obrigatórios.")
                livro = Livro(titulo, autor, ano, num_copias)
                biblioteca.cadastrar_livro(livro)
                messagebox.showinfo("Sucesso", "Livro cadastrado com sucesso!")
                janela.destroy()
                atualizar_estatisticas()
            except ValueError as e:
                messagebox.showerror("Erro", f"Valores inválidos: {e}")

        janela = tk.Toplevel(root)
        janela.title("Cadastrar Livro")
        janela.geometry("450x300")
        centralizar_janela(janela, 450, 300)
        janela.configure(bg='white')
        frame = ttk.Frame(janela, padding=20)
        frame.pack(fill='both', expand=True)

        ttk.Label(frame, text="Título:").grid(row=0, column=0, sticky='w', pady=5)
        titulo_entry = ttk.Entry(frame, width=30)
        titulo_entry.grid(row=0, column=1, pady=5)

        ttk.Label(frame, text="Autor:").grid(row=1, column=0, sticky='w', pady=5)
        autor_entry = ttk.Entry(frame, width=30)
        autor_entry.grid(row=1, column=1, pady=5)

        ttk.Label(frame, text="Ano de Publicação:").grid(row=2, column=0, sticky='w', pady=5)
        ano_entry = ttk.Entry(frame, width=30)
        ano_entry.grid(row=2, column=1, pady=5)

        ttk.Label(frame, text="Número de Cópias:").grid(row=3, column=0, sticky='w', pady=5)
        copias_entry = ttk.Entry(frame, width=30)
        copias_entry.grid(row=3, column=1, pady=5)

        ttk.Button(frame, text="Cadastrar", command=confirmar).grid(row=4, columnspan=2, pady=20)

    def cadastrar_usuario():
        def confirmar():
            nome = nome_entry.get().strip()
            contato = contato_entry.get().strip()
            if not nome or not contato:
                messagebox.showerror("Erro", "Nome e contato são obrigatórios.")
                return
            if not contato.isdigit():
                messagebox.showerror("Erro", "Contato deve conter apenas números.")
                return
            usuario = Usuario(nome, contato)
            biblioteca.cadastrar_usuario(usuario)
            messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!")
            janela.destroy()
            atualizar_estatisticas()

        janela = tk.Toplevel(root)
        janela.title("Cadastrar Usuário")
        janela.geometry("400x200")
        centralizar_janela(janela, 400, 200)
        janela.configure(bg='white')
        frame = ttk.Frame(janela, padding=20)
        frame.pack(fill='both', expand=True)

        ttk.Label(frame, text="Nome:").grid(row=0, column=0, sticky='w', pady=5)
        nome_entry = ttk.Entry(frame, width=30)
        nome_entry.grid(row=0, column=1, pady=5)

        ttk.Label(frame, text="Contato:").grid(row=1, column=0, sticky='w', pady=5)
        contato_entry = ttk.Entry(frame, width=30)
        contato_entry.grid(row=1, column=1, pady=5)

        ttk.Button(frame, text="Cadastrar", command=confirmar).grid(row=2, columnspan=2, pady=20)

    def emprestar_livro():
        def confirmar():
            try:
                id_livro = int(id_livro_entry.get())
                id_usuario = int(id_usuario_entry.get())
                if biblioteca.emprestar_livro(id_livro, id_usuario):
                    messagebox.showinfo("Sucesso", "Empréstimo realizado com sucesso!")
                else:
                    messagebox.showerror("Erro", "Não foi possível emprestar (livro indisponível ou IDs inválidos).")
                janela.destroy()
                atualizar_estatisticas()
            except ValueError:
                messagebox.showerror("Erro", "IDs devem ser números inteiros.")

        janela = tk.Toplevel(root)
        janela.title("Empréstimo de Livro")
        janela.geometry("400x180")
        centralizar_janela(janela, 400, 180)
        janela.configure(bg='white')
        frame = ttk.Frame(janela, padding=20)
        frame.pack(fill='both', expand=True)

        ttk.Label(frame, text="ID do Livro:").grid(row=0, column=0, sticky='w', pady=5)
        id_livro_entry = ttk.Entry(frame, width=30)
        id_livro_entry.grid(row=0, column=1, pady=5)

        ttk.Label(frame, text="ID do Usuário:").grid(row=1, column=0, sticky='w', pady=5)
        id_usuario_entry = ttk.Entry(frame, width=30)
        id_usuario_entry.grid(row=1, column=1, pady=5)

        ttk.Button(frame, text="Emprestar", command=confirmar).grid(row=2, columnspan=2, pady=20)

    def devolver_livro():
        def confirmar():
            try:
                id_livro = int(id_livro_entry.get())
                id_usuario = int(id_usuario_entry.get())
                if biblioteca.devolver_livro(id_livro, id_usuario):
                    messagebox.showinfo("Sucesso", "Devolução realizada com sucesso!")
                else:
                    messagebox.showerror("Erro", "Não foi possível devolver (verifique os IDs).")
                janela.destroy()
                atualizar_estatisticas()
            except ValueError:
                messagebox.showerror("Erro", "IDs devem ser números inteiros.")

        janela = tk.Toplevel(root)
        janela.title("Devolução de Livro")
        janela.geometry("400x180")
        centralizar_janela(janela, 400, 180)
        janela.configure(bg='white')
        frame = ttk.Frame(janela, padding=20)
        frame.pack(fill='both', expand=True)

        ttk.Label(frame, text="ID do Livro:").grid(row=0, column=0, sticky='w', pady=5)
        id_livro_entry = ttk.Entry(frame, width=30)
        id_livro_entry.grid(row=0, column=1, pady=5)

        ttk.Label(frame, text="ID do Usuário:").grid(row=1, column=0, sticky='w', pady=5)
        id_usuario_entry = ttk.Entry(frame, width=30)
        id_usuario_entry.grid(row=1, column=1, pady=5)

        ttk.Button(frame, text="Devolver", command=confirmar).grid(row=2, columnspan=2, pady=20)

    def consultar_livros():
        janela = tk.Toplevel(root)
        janela.title("Consulta de Livros")
        janela.geometry("800x500")
        centralizar_janela(janela, 800, 500)
        janela.configure(bg='white')
        janela.protocol("WM_DELETE_WINDOW", janela.destroy)

        notebook = ttk.Notebook(janela)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Aba por Título
        frame_titulo = ttk.Frame(notebook)
        notebook.add(frame_titulo, text="Por Título")
        ttk.Label(frame_titulo, text="Digite o título:").pack(anchor='w', padx=10, pady=5)
        entry_titulo = ttk.Entry(frame_titulo, width=50)
        entry_titulo.pack(padx=10, pady=5)
        ttk.Button(frame_titulo, text="Buscar",
                   command=lambda: buscar(biblioteca.consultar_livros_por_titulo, entry_titulo.get())).pack(pady=5)

        # Aba por Autor
        frame_autor = ttk.Frame(notebook)
        notebook.add(frame_autor, text="Por Autor")
        ttk.Label(frame_autor, text="Digite o autor:").pack(anchor='w', padx=10, pady=5)
        entry_autor = ttk.Entry(frame_autor, width=50)
        entry_autor.pack(padx=10, pady=5)
        ttk.Button(frame_autor, text="Buscar",
                   command=lambda: buscar(biblioteca.consultar_livros_por_autor, entry_autor.get())).pack(pady=5)

        # Aba por Ano
        frame_ano = ttk.Frame(notebook)
        notebook.add(frame_ano, text="Por Ano")
        ttk.Label(frame_ano, text="Digite o ano:").pack(anchor='w', padx=10, pady=5)
        entry_ano = ttk.Entry(frame_ano, width=50)
        entry_ano.pack(padx=10, pady=5)
        ttk.Button(frame_ano, text="Buscar",
                   command=lambda: buscar(biblioteca.consultar_livros_por_ano, entry_ano.get())).pack(pady=5)

        # Área de resultados
        result_frame = ttk.Frame(janela)
        result_frame.pack(fill='both', expand=True, padx=10, pady=10)

        colunas = ('ID', 'Título', 'Autor', 'Ano', 'Cópias')
        tree = ttk.Treeview(result_frame, columns=colunas, show='headings', height=10)
        for col in colunas:
            tree.heading(col, text=col)
            tree.column(col, width=150, anchor='center')

        scroll = ttk.Scrollbar(result_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        tree.pack(side='left', fill='both', expand=True)
        scroll.pack(side='right', fill='y')

        def buscar(metodo_busca, valor):
            """Executa a busca usando o método específico e exibe os resultados."""
            # Limpa resultados anteriores
            for item in tree.get_children():
                tree.delete(item)

            if not valor.strip():
                messagebox.showerror("Erro", "Digite um valor para busca.", parent=janela)
                janela.lift()
                return

            livros = metodo_busca(valor.strip())
            if not livros:
                messagebox.showinfo("Consulta", "Nenhum livro encontrado.", parent=janela)
                janela.lift()
                return

            for livro in livros:
                tree.insert('', 'end', values=(livro.id, livro.titulo, livro.autor, livro.ano, livro.num_copias))

    def gerar_relatorio():
        relatorio = biblioteca.gerar_relatorio()
        janela = tk.Toplevel(root)
        janela.title("Relatório Completo")
        janela.geometry("600x400")
        centralizar_janela(janela, 600, 400)
        janela.configure(bg='white')

        frame = ttk.Frame(janela, padding=10)
        frame.pack(fill='both', expand=True)

        text = tk.Text(frame, wrap='word', font=('Courier', 10))
        scroll = ttk.Scrollbar(frame, orient='vertical', command=text.yview)
        text.configure(yscrollcommand=scroll.set)
        text.pack(side='left', fill='both', expand=True)
        scroll.pack(side='right', fill='y')

        text.insert('1.0', relatorio)
        text.config(state='disabled')

    def deletar_livro():
        id_livro = simpledialog.askinteger("Deletar Livro", "ID do livro a ser deletado:")
        if id_livro is not None:
            if biblioteca.deletar_livro(id_livro):
                messagebox.showinfo("Sucesso", "Livro deletado.")
                atualizar_estatisticas()
            else:
                messagebox.showerror("Erro", "Livro não encontrado ou não pode ser deletado (pode estar emprestado).")

    def deletar_usuario():
        id_usuario = simpledialog.askinteger("Deletar Usuário", "ID do usuário a ser deletado:")
        if id_usuario is not None:
            if biblioteca.deletar_usuario(id_usuario):
                messagebox.showinfo("Sucesso", "Usuário deletado.")
                atualizar_estatisticas()
            else:
                messagebox.showerror("Erro", "Usuário não encontrado ou possui empréstimos pendentes.")

    def atualizar_estatisticas():
        total_livros = len(biblioteca.livros) if hasattr(biblioteca, 'livros') else 0
        total_usuarios = len(biblioteca.usuarios) if hasattr(biblioteca, 'usuarios') else 0
        label_livros.config(text=str(total_livros))
        label_usuarios.config(text=str(total_usuarios))

    # ========== INTERFACE PRINCIPAL ==========
    # Cabeçalho
    header = tk.Frame(root, bg=cor_primaria, height=80)
    header.pack(fill='x')
    header.pack_propagate(False)
    tk.Label(header, text="📚 Biblioteca Municipal", bg=cor_primaria, fg='white',
             font=('Segoe UI', 24, 'bold')).pack(side='left', padx=30, pady=20)
    tk.Label(header, text="v2.0", bg=cor_primaria, fg='#e0e0e0',
             font=('Segoe UI', 12)).pack(side='right', padx=30, pady=25)

    # Cards de estatísticas
    stats_frame = tk.Frame(root, bg='#f0f4f8')
    stats_frame.pack(fill='x', padx=30, pady=(20, 10))

    card1 = tk.Frame(stats_frame, bg='white', relief='solid', bd=1, padx=20, pady=15)
    card1.pack(side='left', padx=(0, 20))
    tk.Label(card1, text="📖 Livros", bg='white', font=('Segoe UI', 14, 'bold')).pack()
    label_livros = tk.Label(card1, text="0", bg='white', font=('Segoe UI', 32, 'bold'), fg=cor_primaria)
    label_livros.pack()

    card2 = tk.Frame(stats_frame, bg='white', relief='solid', bd=1, padx=20, pady=15)
    card2.pack(side='left')
    tk.Label(card2, text="👥 Usuários", bg='white', font=('Segoe UI', 14, 'bold')).pack()
    label_usuarios = tk.Label(card2, text="0", bg='white', font=('Segoe UI', 32, 'bold'), fg=cor_primaria)
    label_usuarios.pack()

    # Frame principal com os cards de ações
    main_frame = tk.Frame(root, bg='#f0f4f8')
    main_frame.pack(fill='both', expand=True, padx=30, pady=10)

    # Configurar grid para que as colunas tenham o mesmo peso e largura uniforme
    main_frame.columnconfigure(0, weight=1, uniform='card')
    main_frame.columnconfigure(1, weight=1, uniform='card')
    main_frame.columnconfigure(2, weight=1, uniform='card')
    main_frame.rowconfigure(0, weight=1)   # linha dos cards
    main_frame.rowconfigure(1, weight=0)   # linha dos botões longos (não expande verticalmente)

    # Card: Cadastros
    card_cadastro = tk.Frame(main_frame, bg='white', relief='solid', bd=1, padx=20, pady=20)
    card_cadastro.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
    tk.Label(card_cadastro, text="📋 Cadastros", bg='white', font=('Segoe UI', 16, 'bold'), fg=cor_primaria).pack(anchor='w')
    ttk.Button(card_cadastro, text="➕ Cadastrar Livro", command=cadastrar_livro).pack(fill='x', pady=5)
    ttk.Button(card_cadastro, text="👤 Cadastrar Usuário", command=cadastrar_usuario).pack(fill='x', pady=5)

    # Card: Movimentação
    card_mov = tk.Frame(main_frame, bg='white', relief='solid', bd=1, padx=20, pady=20)
    card_mov.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')
    tk.Label(card_mov, text="🔄 Movimentação", bg='white', font=('Segoe UI', 16, 'bold'), fg=cor_primaria).pack(anchor='w')
    ttk.Button(card_mov, text="↪️ Emprestar Livro", command=emprestar_livro).pack(fill='x', pady=5)
    ttk.Button(card_mov, text="↩️ Devolver Livro", command=devolver_livro).pack(fill='x', pady=5)

    # Card: Consulta e Relatórios
    card_consulta = tk.Frame(main_frame, bg='white', relief='solid', bd=1, padx=20, pady=20)
    card_consulta.grid(row=0, column=2, padx=10, pady=10, sticky='nsew')
    tk.Label(card_consulta, text="🔍 Consulta", bg='white', font=('Segoe UI', 16, 'bold'), fg=cor_primaria).pack(anchor='w')
    ttk.Button(card_consulta, text="📚 Consultar Livros", command=consultar_livros).pack(fill='x', pady=5)
    ttk.Button(card_consulta, text="📊 Gerar Relatório", command=gerar_relatorio).pack(fill='x', pady=5)

    # Linha de botões longos (exclusão e saída)
    long_buttons_frame = tk.Frame(main_frame, bg='#f0f4f8')
    long_buttons_frame.grid(row=1, column=0, columnspan=3, pady=(20, 10), sticky='ew')

    # Configurar o frame de botões para que os botões tenham tamanhos iguais
    long_buttons_frame.columnconfigure(0, weight=1)
    long_buttons_frame.columnconfigure(1, weight=1)
    long_buttons_frame.columnconfigure(2, weight=1)

    btn_excluir_livro = tk.Button(long_buttons_frame, text="❌ Deletar Livro", bg=cor_primaria, fg='white',
                                  font=('Segoe UI', 12), padx=20, pady=10, command=deletar_livro)
    btn_excluir_livro.grid(row=0, column=0, padx=5, pady=5, sticky='ew')

    btn_excluir_usuario = tk.Button(long_buttons_frame, text="🗑️ Deletar Usuário", bg=cor_primaria, fg='white',
                                    font=('Segoe UI', 12), padx=20, pady=10, command=deletar_usuario)
    btn_excluir_usuario.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

    btn_sair = tk.Button(long_buttons_frame, text="🚪 Sair", bg='#d9534f', fg='white',
                         font=('Segoe UI', 12), padx=20, pady=10, command=root.quit)
    btn_sair.grid(row=0, column=2, padx=5, pady=5, sticky='ew')

    # Rodapé
    footer = tk.Frame(root, bg=cor_primaria, height=30)
    footer.pack(fill='x', side='bottom')
    tk.Label(footer, text="© 2026 Biblioteca Municipal • Todos os direitos reservados",
             bg=cor_primaria, fg='white', font=('Segoe UI', 9)).pack(pady=5)

    # Inicializar estatísticas
    atualizar_estatisticas()

    root.mainloop()

    # Salvar dados ao sair
    biblioteca.salvar_dados(filename)

if __name__ == "__main__":
    main()