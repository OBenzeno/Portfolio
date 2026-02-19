# 📚 Sistema de Gerenciamento de Biblioteca

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-green)
![JSON](https://img.shields.io/badge/storage-JSON-lightgrey)
![Status](https://img.shields.io/badge/status-concluído-brightgreen)

> Um sistema completo para gerenciamento de bibliotecas desenvolvido em Python com interface gráfica moderna usando Tkinter. Este projeto representa meus primeiros passos na área de dados (2024) e, dois anos depois, revisito-o para enxergar os fundamentos que uso até hoje como Cientista de Dados.

---

## 📖 Sobre o Projeto

**Relembrando o 1º semestre de 2024…**  
Parece que foi ontem. Eu estava dando os primeiros passos na área, ainda descobrindo o que significava transformar problemas em código. O desafio do semestre chegou: desenvolver um Sistema de Gerenciamento de Biblioteca. Na época, parecia apenas "entregar o projeto para passar". Hoje, dois anos depois, olho para aquele código e enxergo algo completamente diferente.

O que eu não sabia naquele 1º semestre é que, sem perceber, eu já estava praticando os fundamentos mais essenciais da Ciência de Dados:

- **Modelagem de entidades** com classes (`Livro`, `Usuario`, `Biblioteca`)
- **Serialização** de objetos para JSON (preparação de dados para persistência)
- **Consultas e filtros** (lógica de busca que hoje uso em SQL/Pandas)
- **Relatórios** como análise descritiva dos dados
- **Regras de negócio** garantindo a integridade e qualidade dos dados

Agora, em 2026, transformei a antiga interface de console em uma aplicação visual atraente com **Tkinter**, mantendo a mesma essência de aprendizado.

---

## ✨ Funcionalidades

- ✅ **Cadastro de Livros** – Título, autor, ano, número de cópias.
- ✅ **Cadastro de Usuários** – Nome e contato (apenas números).
- ✅ **Empréstimo de Livros** – Verifica disponibilidade e impede duplicidade.
- ✅ **Devolução de Livros** – Atualiza estoque e remove vínculo.
- ✅ **Consulta de Livros** – Por título, autor ou ano (com abas separadas).
- ✅ **Relatório Completo** – Lista livros, usuários e empréstimos ativos.
- ✅ **Exclusão Segura** – Impede remoção de itens com vínculos ativos.
- ✅ **Persistência em JSON** – Dados salvos automaticamente ao sair.
- ✅ **Interface Moderna** – Desenvolvida com Tkinter, cores suaves e cards.

---

## 📸 Captura de Tela

![Interface principal do sistema](screenshots/interface_principal.png)

> *Menu principal com cards para cada grupo de ações e estatísticas em destaque.*

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.8+** – Linguagem principal
- **Tkinter** – Interface gráfica nativa
- **JSON** – Armazenamento de dados
- **POO** – Programação Orientada a Objetos (classes, herança, encapsulamento)

---

## 📁 Estrutura do Projeto

sistema-biblioteca/
│
├── main.py # Interface gráfica e lógica de apresentação
├── biblioteca.py # Classe Biblioteca (regras de negócio e persistência)
├── livro.py # Classe Livro (modelo)
├── usuario.py # Classe Usuario (modelo)
├── biblioteca_dados.json # Arquivo de dados gerado automaticamente
├── screenshots/ # Pasta com imagens para o README
│ └── interface_principal.png
└── README.md # Documentação


---

## 🚀 Como Executar

### Pré-requisitos
- Python 3.8 ou superior instalado
- Tkinter já incluso na instalação padrão do Python (não requer instalação adicional)

### Passo a passo

1. **Clone o repositório**
   ```bash
   git clone https://github.com/seu-usuario/sistema-biblioteca.git
   cd sistema-biblioteca

2. (Opcional) Crie e ative um ambiente virtual
    python -m venv venv
    source venv/bin/activate  # Linux/macOS
    venv\Scripts\activate     # Windows
3. Execute o programa
    python main.py

---

💡 Dica: O arquivo biblioteca_dados.json é criado automaticamente na primeira execução. Para começar do zero, basta deletá-lo.

📚 Documentação das Classes

Livro
* Atributos: id, titulo, autor, ano, num_copias
* Métodos principais:
  - emprestar() – reduz o número de cópias se disponível.
  - devolver() – aumenta o número de cópias.
  - to_dict() – converte para dicionário (serialização).
  - from_dict() – cria objeto a partir de dicionário (desserialização).

Usuario
* Atributos: id, nome, contato
* Métodos principais:
  - to_dict() – serialização.
  - from_dict() – desserialização.

Biblioteca
* Atributos: livros (lista), usuarios (lista), emprestimos (dicionário)
* Métodos principais:
  - cadastrar_livro(), cadastrar_usuario()
  - emprestar_livro(), devolver_livro()
  - consultar_livros_por_titulo(), por_autor(), por_ano()
  - gerar_relatorio()
  - deletar_livro(), deletar_usuario() (com validações)
  - salvar_dados() e carregar_dados() (JSON)

🔍 Conexão com Ciência de Dados

| Conceito no Projeto                 | Aplicação em Dados                           |
|-------------------------------------|---------------------------------------------|
| Classes Livro, Usuario             | Modelagem de entidades do mundo real        |
| Serialização JSON (to_dict/from_dict) | Preparação de dados para APIs/pipelines     |
| Consultas com filtros              | Lógica de busca em DataFrames/SQL           |
| Relatórios consolidados            | Análise descritiva e dashboards             |
| Validações de regras de negócio    | Qualidade e governança de dados             |

"Ciência de Dados não começa com algoritmos complexos, mas com a capacidade de estruturar, armazenar, consultar e interpretar dados de forma consistente."

🔮 Melhorias Futuras
- Integração com banco de dados (SQLite/PostgreSQL)
- Geração de relatórios em PDF/Excel
- Dashboard com gráficos de livros mais emprestados
- Sistema de multas por atraso
- API REST para acesso remoto
- Testes unitários automatizados

🤝 Como Contribuir
Contribuições são sempre bem-vindas!
  1. Faça um fork do projeto
  2. Crie uma branch para sua feature (git checkout -b feature/AmazingFeature)
  3. Commit suas mudanças (git commit -m 'Add some AmazingFeature')
  4. Push para a branch (git push origin feature/AmazingFeature)
  5. Abra um Pull Request

📝 Licença
Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

✉️ Contato
Weslley B. de Andrade – @in/weslley-bitencourt – weslleybitencourt03@gmail.com
Link do projeto: https://github.com/OBenzeno/Portfolio/tree/main/biblioteca_python_v2
