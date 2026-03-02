Markdown
# CRUD de Usuários com Perfil

API REST desenvolvida com FastAPI para gerenciamento de usuários e perfis, implementando relacionamento 1:1 e validações de integridade.

## 🚀 Tecnologias e Versões
- **Python:** 3.10+
- **FastAPI:** ^0.100.0
- **Uvicorn:** ^0.23.0
- **Pydantic:** ^2.4.0 (com suporte a `email`)
- **SQLite3:** Nativo do Python

## ⚙️ Funcionalidades
- CRUD completo de Usuários.
- Criação simultânea de Usuário e Perfil atrelado.
- Relacionamento 1:1 rigoroso no banco de dados.
- Validação de e-mail único.
- Listagem e busca trazendo os dados do perfil vinculados via JOIN.

## 🛠️ Como executar

1. Clone o repositório e acesse a pasta:
```bash
git clone [https://github.com/SanthiagoAbreu/Crud_user_with_perfil-PYTHON.git](https://github.com/SanthiagoAbreu/Crud_user_with_perfil-PYTHON.git)
cd Crud_user_with_perfil-PYTHON
Instale as dependências:

Bash
pip install -r requirements.txt
Crie o banco de dados SQLite:

Bash
python init_db.py
Inicie o servidor local:

Bash
uvicorn main:app --reload
Acesse a documentação interativa para testar as rotas (Swagger):
🔗 http://127.0.0.1:8000/docs
