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
