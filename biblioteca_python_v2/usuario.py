class Usuario:
    proximo_id = 1  # Variável de classe para o próximo ID

    def __init__(self, nome, contato, _id=None):
        if _id is None:
            self.id = Usuario.proximo_id
            Usuario.proximo_id += 1
        else:
            self.id = _id  # Caso seja fornecido um ID (ex.: ao carregar do JSON)
        self.nome = nome
        self.contato = contato

    def to_dict(self):
        """
        Converte a instância do objeto para um dicionário, facilitando a serialização em JSON.
        """
        return {
            'id': self.id,
            'nome': self.nome,
            'contato': self.contato,
        }

    @classmethod
    def from_dict(cls, data):
        """
        Cria uma instância da classe a partir de um dicionário.
        """
        return cls(nome=data['nome'], contato=data['contato'], _id=data['id'])
