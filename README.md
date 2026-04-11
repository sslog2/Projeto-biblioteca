# 📚 Projeto Biblioteca

Sistema de gerenciamento de biblioteca desenvolvido com **Django 6.0** e **Django REST Framework 3.17**, oferecendo uma API RESTful completa e um front-end com templates em CSS puro.

## Índice

- [Tecnologias](#tecnologias)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Pré-requisitos](#pré-requisitos)
- [Instalação Local](#instalação-local)
- [Rodando com Docker](#rodando-com-docker)
- [Variáveis de Ambiente](#variáveis-de-ambiente)
- [Populando o Banco de Dados](#populando-o-banco-de-dados)
- [Endpoints da API](#endpoints-da-api)
- [Páginas do Front-End](#páginas-do-front-end)
- [Diagrama ER](#diagrama-er)
- [Licença](#licença)

## Tecnologias

| Camada       | Tecnologia                          |
|--------------|-------------------------------------|
| Linguagem    | Python 3.12                         |
| Framework    | Django 6.0.3                        |
| API          | Django REST Framework 3.17.1        |
| Docs da API  | drf-yasg (Swagger UI)               |
| Banco (dev)  | SQLite                              |
| Banco (prod) | PostgreSQL 16                       |
| Container    | Docker + Docker Compose             |
| CI           | GitHub Actions                      |

## Estrutura do Projeto

```
├── project/           # Configurações do Django (settings, urls, wsgi)
├── app/
│   ├── api/           # Models, Views (CRUD), Serializers, URLs
│   │   └── management/commands/  # Comando popular_db
│   └── utils/         # Views utilitárias (Dashboard, Ranking, Multas)
├── templates/         # Templates HTML (Dashboard, Feed, Livros, etc.)
├── static/            # CSS e JavaScript
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── manage.py
```

## Pré-requisitos

- **Python 3.12+**
- **pip**
- **Docker e Docker Compose** (opcional, para rodar via contêiner)

## Instalação Local

### 1. Clonar o repositório

```bash
git clone https://github.com/sslog2/Projeto-biblioteca.git
cd Projeto-biblioteca
```

### 2. Criar e ativar o ambiente virtual

```bash
# Windows
python -m venv env
env\Scripts\activate

# Linux / macOS
python3 -m venv env
source env/bin/activate
```

### 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente (opcional)

Por padrão o projeto usa **SQLite** sem necessidade de configuração. Para usar PostgreSQL, crie um arquivo `.env` na raiz:

```bash
cp .env_example .env
```

Para usar SQLite (padrão), basta não criar o `.env` ou definir:

```
USE_POSTGRESQL=False
```

### 5. Aplicar as migrações

```bash
python manage.py migrate
```

### 6. Popular o banco com dados de demonstração (opcional)

```bash
python manage.py popular_db
```

### 7. Iniciar o servidor

```bash
python manage.py runserver
```

Acesse em: **http://127.0.0.1:8000/**

## Rodando com Docker

### 1. Criar o arquivo `.env`

```bash
cp .env_example .env
```

### 2. Descomentar o serviço do banco no `docker-compose.yml`

Abra o `docker-compose.yml` e descomente o bloco do serviço `db`.

### 3. Subir os contêineres

```bash
docker compose up --build
```

As migrações são executadas automaticamente na inicialização do contêiner.

Acesse em: **http://localhost:8000/**

## Variáveis de Ambiente

| Variável            | Padrão       | Descrição                                     |
|---------------------|--------------|------------------------------------------------|
| `USE_POSTGRESQL`    | `False`      | `True` para usar PostgreSQL, `False` para SQLite |
| `POSTGRES_DB`       | `biblioteca` | Nome do banco PostgreSQL                       |
| `POSTGRES_USER`     | `postgres`   | Usuário do PostgreSQL                          |
| `POSTGRES_PASSWORD` | `postgres`   | Senha do PostgreSQL                            |
| `POSTGRES_HOST`     | `db`         | Host do PostgreSQL (nome do serviço no Docker) |
| `POSTGRES_PORT`     | `5432`       | Porta do PostgreSQL                            |

## Populando o Banco de Dados

O comando `popular_db` insere dados de demonstração incluindo editoras, livros, estantes, membros, empréstimos e multas:

```bash
python manage.py popular_db
```

> **Atenção:** esse comando apaga todos os dados existentes antes de inserir os novos.

## Endpoints da API

### Documentação Interativa

| Rota         | Descrição      |
|--------------|----------------|
| `/swagger/`  | Swagger UI     |
| `/admin/`    | Django Admin   |

### CRUD — `/api/`

Cada recurso possui 5 endpoints:

| Método      | Rota                                 | Ação      |
|-------------|--------------------------------------|-----------|
| `GET`       | `/api/{recurso}/`                    | Listar    |
| `POST`      | `/api/{recurso}/criar/`              | Criar     |
| `GET`       | `/api/{recurso}/<id>/`               | Detalhar  |
| `PUT/PATCH` | `/api/{recurso}/<id>/atualizar/`     | Atualizar |
| `DELETE`    | `/api/{recurso}/<id>/deletar/`       | Deletar   |

**Recursos disponíveis:** `livros`, `estantes`, `editoras`, `membros`, `emprestimos`, `multas`

### Utilitários — `/api/utils/`

| Método     | Rota                              | Descrição                             |
|------------|-----------------------------------|---------------------------------------|
| `GET`      | `/api/utils/dashboard/`           | Métricas consolidadas do sistema      |
| `GET`      | `/api/utils/novos-livros/`        | Livros recém-cadastrados              |
| `GET`      | `/api/utils/ranking/`             | Ranking dos livros mais emprestados   |
| `GET/POST` | `/api/utils/calculo-multa/`       | Simulação e criação de multas         |
| `GET`      | `/api/utils/atrasados/`           | Empréstimos com devolução vencida     |
| `GET`      | `/api/utils/membro/<id>/stats/`   | Estatísticas individuais de um membro |

## Páginas do Front-End

| Rota         | Página                     |
|--------------|----------------------------|
| `/`          | Dashboard                  |
| `/feed/`     | Feed de Novidades          |
| `/ranking/`  | Ranking Semanal            |
| `/livros/`   | Cadastro de Livros         |
| `/editoras/` | Gestão de Editoras         |
| `/membros/`  | Administração de Membros   |
| `/multa/`    | Calculador de Multas       |

## Diagrama ER

O diagrama entidade-relacionamento é gerado automaticamente via GitHub Actions a cada push na branch `main`. O arquivo `erd.png` na raiz do repositório é sempre atualizado com o estado atual do banco.

## Licença

Este projeto está licenciado sob a licença **MIT**. Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.