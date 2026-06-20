# Encurtador URL API

API em FastAPI para encurtamento de URLs com suporte a:

- criação de URLs curtas públicas
- criação de URLs curtas vinculadas a usuários autenticados
- expiração por tipo de usuário
- coleta de métricas de acesso
- geração de QR Code
- autenticação com JWT
- versionamento de schema com Alembic

## Visão Geral

O projeto implementa um micro SaaS de encurtamento de URLs com duas regras principais de negócio:

- usuários não cadastrados podem gerar URLs curtas
- usuários não cadastrados não podem acessar métricas e suas URLs expiram antes

Hoje a aplicação já está organizada em camadas de rota, service, schema, auth e model.

## Stack

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Alembic
- Pydantic
- SlowAPI
- Passlib + bcrypt
- PyJWT
- qrcode

## Estrutura Do Projeto

```text
src/
  alembic/
    versions/
  auth/
    acess.py
    auth.py
  core/
    rate_limiter.py
  dependencies/
    dependencies.py
  models/
    models.py
  routes/
    metrics_routes.py
    shortener_routes.py
    user_routes.py
  schemas/
    metric_schema.py
    shortener_schema.py
    token_schema.py
    user_schema.py
  services/
    metric_service.py
    short_url_service.py
    user_service.py
  utils/
    short_code.py
    url_utils.py
  alembic.ini
  banco.db
  main.py
requirements.txt
```

## Arquitetura

### Rotas

As rotas recebem a requisição HTTP, resolvem dependências do FastAPI e delegam a regra de negócio para os services.

- `src/routes/shortener_routes.py`
- `src/routes/user_routes.py`
- `src/routes/metrics_routes.py`

### Services

Os services concentram a regra de negócio da aplicação.

- `short_url_service.py`
  - valida URL
  - gera hash curto
  - define expiração
  - persiste URL encurtada
  - valida expiração no redirecionamento
  - registra métricas de acesso
- `metric_service.py`
  - consulta métricas por dia, mês e ano
  - restringe acesso a URLs anônimas
  - restringe acesso a usuários que não são donos da URL
- `user_service.py`
  - cria usuário
  - busca usuário por e-mail
  - autentica usuário
  - emite tokens JWT

### Models

Os models SQLAlchemy estão em `src/models/models.py`.

- `User`
- `ShortUrl`
- `UrlMetric`

### Schemas

Os schemas Pydantic definem payloads de entrada e saída da API.

### Auth

O módulo `src/auth` centraliza autenticação JWT e recuperação do usuário autenticado.

### Utils

Os utilitários concentram helpers puros reutilizáveis.

- `validate_url()`
- `generate_short_id()`

## Regras De Negócio

### URLs anônimas

- podem ser criadas sem autenticação
- ficam com `user_id = null`
- expiram em `7` dias
- não podem ter métricas consultadas

### URLs de usuários autenticados

- exigem token Bearer válido
- ficam associadas ao `user_id`
- expiram em `30` dias
- métricas só podem ser acessadas pelo dono da URL

### Expiração

A expiração é armazenada em `ShortUrl.expires_at`.

Durante o redirecionamento:

- se a URL não existir, retorna `404`
- se estiver expirada, retorna `410`
- se estiver válida, registra métrica e redireciona

### Métricas

As métricas são agregadas por dia em `UrlMetric`:

- `day`
- `month`
- `year`
- `amount`

As consultas mensal e anual somam os registros diários armazenados.

## Banco De Dados

O projeto usa SQLite com arquivo local em:

- `src/banco.db`

O engine SQLAlchemy é definido em `src/models/models.py` com:

```python
db = create_engine("sqlite:///banco.db")
```

As sessões são abertas via `get_session()` em `src/dependencies/dependencies.py`.

## Models

### User

Campos:

- `id`
- `name`
- `email`
- `password`
- `access`

Relacionamentos:

- `short_urls`

### ShortUrl

Campos:

- `id`
- `origin_url`
- `hash_url`
- `user_id`
- `expires_at`

Relacionamentos:

- `user`
- `metrics`

### UrlMetric

Campos:

- `id`
- `day`
- `month`
- `year`
- `amount`
- `short_url_id`

## Endpoints

### Público

#### `POST /short`

Cria uma URL curta anônima.

Request:

```json
{
  "url": "https://exemplo.com"
}
```

Response:

```json
{
  "url": "https://exemplo.com",
  "short_url": "http://localhost:8000/abc123X"
}
```

#### `GET /{short_id}`

Redireciona para a URL original.

Observações:

- possui rate limit de `5/minute`
- registra métrica diária
- retorna `410` se a URL estiver expirada

#### `GET /{short_id}/qrcode`

Gera um QR Code PNG apontando para a URL curta.

### Usuário

Prefixo base: `/user`

#### `POST /user/create`

Cria usuário.

Request:

```json
{
  "name": "Victor",
  "email": "victor@email.com",
  "password": "123456"
}
```

#### `POST /user/login`

Autentica usuário e retorna tokens.

Request:

```json
{
  "email": "victor@email.com",
  "password": "123456"
}
```

Response:

```json
{
  "access_token": "...",
  "refresh_token": "..."
}
```

#### `POST /user/createUrl`

Cria uma URL curta vinculada ao usuário autenticado.

Headers:

```text
Authorization: Bearer <access_token>
```

Request:

```json
{
  "url": "https://exemplo.com"
}
```

### Métricas

As rotas de métricas exigem autenticação e validam ownership.

#### `GET /metrics/day/{short_id}`

Retorna métricas do dia da URL do usuário.

#### `GET /metrics/month/{short_id}`

Retorna soma das métricas do mês atual.

#### `GET /metrics/year/{short_id}`

Retorna soma das métricas do ano atual.

## Autenticação

A autenticação usa JWT.

Arquivo principal:

- `src/auth/auth.py`

Funções principais:

- `create_access_token()`
- `create_refresh_token()`
- `decode_token()`

O usuário autenticado é resolvido em:

- `src/auth/acess.py`

O token deve conter:

- `sub`: e-mail do usuário
- `type`: `access` ou `refresh`

## Configuração De Ambiente

O projeto lê variáveis do `.env` para autenticação:

- `SECRET_KEY`
- `HASH`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `REFRESH_TOKEN_EXPIRE_MINUTES`

## Migrations Com Alembic

Configuração principal:

- `src/alembic.ini`
- `src/alembic/env.py`

Revisões atuais:

- `ffaeb92272a5_create_initial_tables.py`
- `6f8e9b0a1c2d_add_expires_at_to_short_urls.py`

### Comandos úteis

Rodando a partir de `src/`:

```bash
alembic current
alembic heads
alembic history
alembic upgrade head
alembic revision --autogenerate -m "descricao"
```

Rodando a partir da raiz do projeto:

```bash
py -m alembic -c "src/alembic.ini" upgrade head
py -m alembic -c "src/alembic.ini" revision --autogenerate -m "descricao"
```

## Como Executar

### 1. Criar e ativar ambiente virtual

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Aplicar migrations

Na pasta `src`:

```bash
alembic upgrade head
```

### 4. Subir a API

Na pasta `src`:

```bash
uvicorn main:app --reload
```

## Fluxos Principais

### Fluxo de criação de URL anônima

1. cliente chama `POST /short`
2. rota delega para `short_url_service.create_short_url(..., user_id=None)`
3. service valida a URL
4. service gera `short_id`
5. service define expiração de 7 dias
6. service persiste no banco
7. rota devolve a URL encurtada completa

### Fluxo de criação de URL autenticada

1. cliente chama `POST /user/createUrl`
2. FastAPI resolve `get_current_user`
3. rota chama `short_url_service.create_short_url(..., user_id=current_user.id)`
4. service define expiração de 30 dias
5. URL fica vinculada ao usuário

### Fluxo de redirecionamento

1. cliente acessa `GET /{short_id}`
2. service busca a URL pelo hash
3. service valida se a URL não expirou
4. service incrementa ou cria a métrica do dia
5. API responde com redirect para `origin_url`

### Fluxo de consulta de métricas

1. cliente chama rota de métricas com Bearer token
2. FastAPI resolve usuário autenticado
3. service localiza a URL pelo hash
4. service valida se a URL pertence ao usuário
5. service consulta ou agrega métricas
6. rota retorna o schema correspondente

## Limitações E Pontos De Atenção

Esta seção documenta o estado real atual do projeto.

### Dependências incompletas no `requirements.txt`

O arquivo `requirements.txt` atual não inclui algumas bibliotecas que o código usa diretamente, como:

- `alembic`
- `python-dotenv`
- `passlib`
- `bcrypt`
- `PyJWT`
- `qrcode`
- `slowapi`

Sem elas, a aplicação não sobe corretamente em um ambiente limpo.

### Incompatibilidade observada entre `passlib` e `bcrypt`

Foi observado erro de hashing com:

- `passlib==1.7.4`
- `bcrypt==5.0.0`

O sintoma aparece como erro de senha maior que 72 bytes mesmo para senhas curtas.

Sugestão prática:

- usar `bcrypt==4.0.1`

### `tokenUrl` diferente do endpoint real

Em `src/auth/auth.py`, o `OAuth2PasswordBearer` usa:

```python
tokenUrl="/users/login"
```

Mas a rota real registrada hoje é:

```text
POST /user/login
```

Isso deve ser ajustado para evitar inconsistência no Swagger e no fluxo OAuth2.

### Engine do banco e caminho do SQLite

O SQLAlchemy usa:

```python
sqlite:///banco.db
```

Como o banco real do projeto está em `src/banco.db`, o comportamento depende do diretório atual de execução. O ideal é padronizar esse caminho para evitar abrir bancos diferentes sem perceber.

### Ausência de testes automatizados

Hoje não há suíte de testes no repositório.

### Naming inconsistente

Alguns nomes ainda podem ser melhorados futuramente:

- `acess.py` em vez de `access.py`
- `shortenerRequest` e `shortenerResponse` com inicial minúscula
- `createUrl` misturando convenções de nome

## Melhorias Naturais Futuras

1. corrigir dependências do `requirements.txt`
2. alinhar `tokenUrl` com `/user/login`
3. padronizar caminho do banco SQLite
4. adicionar testes para services e rotas
5. adicionar deleção ou limpeza de URLs expiradas
6. adicionar planos de acesso com base em `AccessLevel`
7. padronizar nomes de rotas e schemas

## Estado Atual Resumido

O projeto já possui uma boa base funcional para um micro SaaS de encurtamento de URLs com:

- autenticação JWT
- diferenciação entre usuário anônimo e cadastrado
- expiração por política
- coleta de métricas
- QR Code
- migrations com Alembic
- separação de regra de negócio em services

Os próximos passos mais importantes são estabilizar dependências, alinhar migrations com o banco local e adicionar testes.
