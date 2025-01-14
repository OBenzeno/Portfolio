class Livro:
    proximo_id = 1  # Variável de classe para o próximo ID
    
    def __init__(self, titulo, autor, ano, num_copias, _id=None):
        if _id is None:
            self.id = Livro.proximo_id
            Livro.proximo_id += 1
        else:
            self.id = _id
        self.titulo = titulo
        self.autor = autor
        self.ano = ano
        self.num_copias = num_copias

    def emprestar(self):
        """Realiza o empréstimo do livro, caso haja cópias disponíveis."""
        if self.num_copias > 0:
            self.num_copias -= 1
            return True
        else:
            return False

    def devolver(self):
        """Devolve uma cópia do livro."""
        self.num_copias += 1

    def to_dict(self):
        """Converte o objeto Livro para um dicionário."""
        return {
            'id': self.id,
            'titulo': self.titulo,
            'autor': self.autor,
            'ano': self.ano,
            'num_copias': self.num_copias
        }
    
    @classmethod
    def from_dict(cls, livro_dict):
        """Cria um objeto Livro a partir de um dicionário."""
        return cls(
            titulo=livro_dict['titulo'],
            autor=livro_dict['autor'],
            ano=livro_dict['ano'],
            num_copias=livro_dict['num_copias'],
            _id=livro_dict.get('id')
        )
