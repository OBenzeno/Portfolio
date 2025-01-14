import json
import os

from livro import Livro
from usuario import Usuario

class Biblioteca:
    def __init__(self):
        self.livros = []
        self.usuarios = []
        self.emprestimos = {}

    def cadastrar_livro(self, livro):
        self.livros.append(livro)

    def cadastrar_usuario(self, usuario):
        self.usuarios.append(usuario)

    def emprestar_livro(self, id_livro, id_usuario):
        livro = next((livro for livro in self.livros if livro.id == id_livro), None)
        usuario = next((usuario for usuario in self.usuarios if usuario.id == id_usuario), None)
        if livro and usuario:
            if id_livro in [livro.id for livro in self.emprestimos.get(usuario.id, [])]:
                print("Usuário já possui este livro emprestado.")
                return False
            if livro.emprestar():
                if usuario.id in self.emprestimos:
                    self.emprestimos[usuario.id].append(livro)
                else:
                    self.emprestimos[usuario.id] = [livro]
                return True
        return False

    def devolver_livro(self, id_livro, id_usuario):
        usuario = next((usuario for usuario in self.usuarios if usuario.id == id_usuario), None)
        if usuario:
            livro = next((livro for livro in self.livros if livro.id == id_livro), None)
            if livro:
                if usuario.id in self.emprestimos:
                    livro_emprestado = next((l for l in self.emprestimos[usuario.id] if l.id == id_livro), None)
                    if livro_emprestado:
                        livro.devolver()
                        self.emprestimos[usuario.id].remove(livro_emprestado)
                        if not self.emprestimos[usuario.id]:
                            del self.emprestimos[usuario.id]
                        return True
        return False

    def consultar_livros(self, parametro):
        livros_encontrados = [
            livro for livro in self.livros
            if parametro.lower() in [livro.titulo.lower(), livro.autor.lower(), str(livro.ano)]
        ]
        return livros_encontrados

    def gerar_relatorio(self):
        relatorio = "Livros disponíveis:\n"
        for livro in self.livros:
            relatorio += f"ID: {livro.id}, Título: {livro.titulo}, Autor: {livro.autor}, Ano: {livro.ano}, Cópias Disponíveis: {livro.num_copias}\n"
        relatorio += "\nUsuários cadastrados:\n"
        for usuario in self.usuarios:
            relatorio += f"ID: {usuario.id}, Nome: {usuario.nome}, Contato: {usuario.contato}\n"
        relatorio += "\nEmpréstimos:\n"
        for usuario_id, livros in self.emprestimos.items():
            usuario = next((usuario for usuario in self.usuarios if usuario.id == usuario_id), None)
            if usuario:
                relatorio += f"Usuário: {usuario.nome}, Contato: {usuario.contato}, ID: {usuario.id}\n"
                for livro in livros:
                    relatorio += f"- Livro: {livro.titulo}, ID: {livro.id}\n"
        return relatorio

    def deletar_livro(self, id):
        for livro in self.livros:
            if livro.id == id:
                if any(id in [l.id for l in livros] for livros in self.emprestimos.values()):
                    return False
                self.livros.remove(livro)
                return True
        return False

    def deletar_usuario(self, id):
        for usuario in self.usuarios:
            if usuario.id == id:
                if id in self.emprestimos:
                    return False
                self.usuarios.remove(usuario)
                return True
        return False

    def salvar_dados(self, filename):
        data = {
            'livros': [livro.to_dict() for livro in self.livros],
            'usuarios': [usuario.to_dict() for usuario in self.usuarios],
            'emprestimos': {
                str(usuario_id): [livro.to_dict() for livro in livros]
                for usuario_id, livros in self.emprestimos.items()
            },
        }
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

    def carregar_dados(self, filename):
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as file:
                data = json.load(file)
                if 'livros' in data:
                    for livro_data in data['livros']:
                        livro = Livro.from_dict(livro_data)
                        self.livros.append(livro)
                if 'usuarios' in data:
                    for usuario_data in data['usuarios']:
                        usuario = Usuario.from_dict(usuario_data)
                        self.usuarios.append(usuario)
                if 'emprestimos' in data:
                    for usuario_id, livros_data in data['emprestimos'].items():
                        usuario_id = int(usuario_id)
                        livros = [Livro.from_dict(livro_data) for livro_data in livros_data]
                        self.emprestimos[usuario_id] = livros
