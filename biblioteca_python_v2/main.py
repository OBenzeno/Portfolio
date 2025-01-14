import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import ttk
from livro import Livro
from usuario import Usuario
from biblioteca import Biblioteca

def main():
    biblioteca = Biblioteca()

    # Carregar dados se o arquivo existir
    filename = 'biblioteca_dados.json'
    biblioteca.carregar_dados(filename)

    def cadastrar_livro():
        def confirmar_cadastro():
            try:
                titulo = titulo_entry.get()
                autor = autor_entry.get()
                ano = int(ano_entry.get())
                num_copias = int(copias_entry.get())
                livro = Livro(titulo, autor, ano, num_copias)
                biblioteca.cadastrar_livro(livro)
                messagebox.showinfo("Sucesso", "Livro cadastrado com sucesso!")
                cadastro_window.destroy()
            except ValueError:
                messagebox.showerror("Erro", "Por favor, insira valores válidos para o ano e o número de cópias.")

        cadastro_window = tk.Toplevel(root)
        cadastro_window.title("Cadastrar Livro")

        tk.Label(cadastro_window, text="Título").grid(row=0, column=0)
        titulo_entry = tk.Entry(cadastro_window)
        titulo_entry.grid(row=0, column=1)

        tk.Label(cadastro_window, text="Autor").grid(row=1, column=0)
        autor_entry = tk.Entry(cadastro_window)
        autor_entry.grid(row=1, column=1)

        tk.Label(cadastro_window, text="Ano").grid(row=2, column=0)
        ano_entry = tk.Entry(cadastro_window)
        ano_entry.grid(row=2, column=1)

        tk.Label(cadastro_window, text="Número de Cópias").grid(row=3, column=0)
        copias_entry = tk.Entry(cadastro_window)
        copias_entry.grid(row=3, column=1)

        tk.Button(cadastro_window, text="Cadastrar", command=confirmar_cadastro).grid(row=4, columnspan=2)

    def cadastrar_usuario():
        def confirmar_cadastro():
            nome = nome_entry.get()
            contato = contato_entry.get()
            if not contato.isdigit():
                messagebox.showerror("Erro", "Por favor, insira apenas números para o contato.")
                return
            usuario = Usuario(nome, contato)
            biblioteca.cadastrar_usuario(usuario)
            messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!")
            cadastro_window.destroy()

        cadastro_window = tk.Toplevel(root)
        cadastro_window.title("Cadastrar Usuário")

        tk.Label(cadastro_window, text="Nome").grid(row=0, column=0)
        nome_entry = tk.Entry(cadastro_window)
        nome_entry.grid(row=0, column=1)

        tk.Label(cadastro_window, text="Contato").grid(row=1, column=0)
        contato_entry = tk.Entry(cadastro_window)
        contato_entry.grid(row=1, column=1)

        tk.Button(cadastro_window, text="Cadastrar", command=confirmar_cadastro).grid(row=2, columnspan=2)

    def emprestar_livro():
        def confirmar_emprestimo():
            try:
                id_livro = int(id_livro_entry.get())
                id_usuario = int(id_usuario_entry.get())
                if biblioteca.emprestar_livro(id_livro, id_usuario):
                    messagebox.showinfo("Sucesso", "Livro emprestado com sucesso!")
                else:
                    messagebox.showerror("Erro", "Não foi possível emprestar o livro.")
                emprestimo_window.destroy()
            except ValueError:
                messagebox.showerror("Erro", "Por favor, insira valores válidos para o ID do livro e do usuário.")

        emprestimo_window = tk.Toplevel(root)
        emprestimo_window.title("Empréstimo de Livro")

        tk.Label(emprestimo_window, text="ID do Livro").grid(row=0, column=0)
        id_livro_entry = tk.Entry(emprestimo_window)
        id_livro_entry.grid(row=0, column=1)

        tk.Label(emprestimo_window, text="ID do Usuário").grid(row=1, column=0)
        id_usuario_entry = tk.Entry(emprestimo_window)
        id_usuario_entry.grid(row=1, column=1)

        tk.Button(emprestimo_window, text="Emprestar", command=confirmar_emprestimo).grid(row=2, columnspan=2)

    def devolver_livro():
        def confirmar_devolucao():
            try:
                id_livro = int(id_livro_entry.get())
                id_usuario = int(id_usuario_entry.get())
                if biblioteca.devolver_livro(id_livro, id_usuario):
                    messagebox.showinfo("Sucesso", "Livro devolvido com sucesso!")
                else:
                    messagebox.showerror("Erro", "Não foi possível devolver o livro.")
                devolucao_window.destroy()
            except ValueError:
                messagebox.showerror("Erro", "Por favor, insira valores válidos para o ID do livro e do usuário.")

        devolucao_window = tk.Toplevel(root)
        devolucao_window.title("Devolução de Livro")

        tk.Label(devolucao_window, text="ID do Livro").grid(row=0, column=0)
        id_livro_entry = tk.Entry(devolucao_window)
        id_livro_entry.grid(row=0, column=1)

        tk.Label(devolucao_window, text="ID do Usuário").grid(row=1, column=0)
        id_usuario_entry = tk.Entry(devolucao_window)
        id_usuario_entry.grid(row=1, column=1)

        tk.Button(devolucao_window, text="Devolver", command=confirmar_devolucao).grid(row=2, columnspan=2)

    def consultar_livros():
        parametro = simpledialog.askstring("Consulta de Livros", "Digite o Título, Autor ou Ano de Publicação:")
        if parametro:
            livros_encontrados = biblioteca.consultar_livros(parametro)
            if livros_encontrados:
                resultado = "Livros encontrados:\n"
                for livro in livros_encontrados:
                    resultado += (f"ID: {livro.id}, Título: {livro.titulo}, Autor: {livro.autor}, Ano: {livro.ano}, "
                                 f"Cópias Disponíveis: {livro.num_copias}\n")
                show_resultado(resultado)
            else:
                messagebox.showinfo("Consulta de Livros", "Nenhum livro encontrado com esse parâmetro.")

    def gerar_relatorio():
        relatorio = biblioteca.gerar_relatorio()
        show_resultado(relatorio)

    def show_resultado(result):
        # Tela de resultados
        resultado_window = tk.Toplevel(root)
        resultado_window.title("Relatório Completo")

        # Tela com rolagem
        result_frame = tk.Frame(resultado_window)
        result_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Create a canvas for the scrollable area
        canvas = tk.Canvas(result_frame)
        scrollbar = tk.Scrollbar(result_frame, orient="vertical", command=canvas.yview)
        canvas.config(yscrollcommand=scrollbar.set)

        # Create a frame inside the canvas that holds the results
        result_canvas_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=result_canvas_frame, anchor="nw")

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # Split the result into lines and add them to the frame
        result_lines = result.split('\n')
        for line in result_lines:
            tk.Label(result_canvas_frame, text=line, anchor="w", justify="left").pack(fill="x")

        # Update the scroll region
        result_canvas_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    def deletar_livro():
        try:
            id_livro = simpledialog.askinteger("Deletar Livro", "Digite o ID do Livro a ser deletado:")
            if id_livro is not None:
                if biblioteca.deletar_livro(id_livro):
                    messagebox.showinfo("Sucesso", "Livro deletado com sucesso!")
                else:
                    messagebox.showerror("Erro", "Livro não encontrado ou já foi emprestado.")
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira um ID válido.")

    def deletar_usuario():
        try:
            id_usuario = simpledialog.askinteger("Deletar Usuário", "Digite o ID do Usuário a ser deletado:")
            if id_usuario is not None:
                if biblioteca.deletar_usuario(id_usuario):
                    messagebox.showinfo("Sucesso", "Usuário deletado com sucesso!")
                else:
                    messagebox.showerror("Erro", "Usuário não encontrado ou possui empréstimos pendentes.")
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira um ID válido.")

    # Interface principal
    global root
    root = tk.Tk()
    root.title("Sistema de Gerenciamento de Biblioteca")

    # Adicionar um estilo de botão
    button_style = {'padx': 10, 'pady': 5, 'font': ("Arial", 12)}

    tk.Button(root, text="Cadastrar Livro", command=cadastrar_livro, **button_style).pack(fill="x")
    tk.Button(root, text="Cadastrar Usuário", command=cadastrar_usuario, **button_style).pack(fill="x")
    tk.Button(root, text="Empréstimo de Livro", command=emprestar_livro, **button_style).pack(fill="x")
    tk.Button(root, text="Devolução de Livro", command=devolver_livro, **button_style).pack(fill="x")
    tk.Button(root, text="Consulta de Livros", command=consultar_livros, **button_style).pack(fill="x")
    tk.Button(root, text="Gerar Relatório", command=gerar_relatorio, **button_style).pack(fill="x")
    tk.Button(root, text="Deletar Livro", command=deletar_livro, **button_style).pack(fill="x")
    tk.Button(root, text="Deletar Usuário", command=deletar_usuario, **button_style).pack(fill="x")
    tk.Button(root, text="Sair", command=root.quit, **button_style).pack(fill="x")

    root.mainloop()

    # Salvar dados antes de sair
    biblioteca.salvar_dados(filename)

if __name__ == "__main__":
    main()
