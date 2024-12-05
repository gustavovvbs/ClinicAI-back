[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/OxqeFv_o)

# Sistema de Busca de Estudos Clínicos - Hospital Sírio-Libanês

Este projeto é um sistema backend em Python destinado à busca e gerenciamento de estudos clínicos, integrando dados do [ClinicalTrials.gov](https://clinicaltrials.gov/) com recursos avançados de busca, análise, chatbot e tradução. O objetivo é facilitar a recuperação, compreensão e análise de dados sobre ensaios clínicos, fornecendo uma API robusta e escalável.

## 📋 Índice
- [Sistema de Busca de Estudos Clínicos - Hospital Sírio-Libanês](#sistema-de-busca-de-estudos-clínicos---hospital-sírio-libanês)
  - [📋 Índice](#-índice)
  - [🎯 Sobre](#-sobre)
  - [⚡ Funcionalidades](#-funcionalidades)
  - [🏗 Arquitetura](#-arquitetura)
  - [📦 Requisitos](#-requisitos)
  - [🔧 Instalação](#-instalação)
  - [⚙ Configuração](#-configuração)
  - [🚀 Uso](#-uso)
  - [💻 Desenvolvimento](#-desenvolvimento)
    - [🕒 Tarefas Agendadas (APScheduler)](#-tarefas-agendadas-apscheduler)
    - [🔍 Busca Híbrida](#-busca-híbrida)
    - [🔐 Autenticação](#-autenticação)
  - [📝 Endpoints da API](#-endpoints-da-api)
      - [🔐 Autenticação](#-autenticação-1)
      - [🔍 Busca](#-busca)
      - [📋 Estudos](#-estudos)
      - [Análise de Dados](#análise-de-dados)
      - [📧 Email](#-email)
      - [🤖 Chatbot](#-chatbot)
      - [👤 Gestão de Usuários](#-gestão-de-usuários)
    - [🚢 Deploy](#-deploy)

## 🎯 Sobre
O sistema oferece uma API para busca e análise de estudos clínicos, integrando dados públicos, tradução automática, indexação vetorial e um chatbot para auxiliar na exploração das informações. A aplicação realiza ingestões diárias do ClinicalTrials.gov, permitindo manter a base de dados atualizada. Além disso, a aplicação emprega embeddings semânticos e busca vetorial (via Pinecone) para refinar resultados, bem como tradução PT-BR para facilitar a compreensão local.

## ⚡ Funcionalidades

**Core:**
- **Busca avançada de estudos clínicos**: Combinação de dados externos (ClinicalTrials.gov) e internos (MongoDB).
- **Chatbot assistente**: Suporte conversacional para orientação na pesquisa.
- **Análise de dados e métricas**: Geração de métricas, estatísticas e insights sobre os ensaios clínicos.
- **Tradução automática (PT-BR)**: Integração com Google Cloud Translate.
- **Exportação de resultados**: Exportação de resultados de busca em formatos comuns (JSON, CSV).

**Técnicas:**
- **Busca vetorial com Pinecone**: Melhoria da relevância através de embeddings semânticos.
- **Processamento de Linguagem Natural (NLP)**: Uso de modelos OpenAI para análise textual.
- **Ingestão automática de dados**: Tarefas agendadas para manter a base de dados atualizada.
- **Cache e otimização de consultas**: Melhorias de performance no tempo de resposta.
- **Autenticação JWT**: Controle de acesso seguro a endpoints protegidos.

## 🏗 Arquitetura

A seguir, a estrutura de pastas do projeto:

```
├── .github/
│ └── workflows/ 
│ └── deploy.yml # Workflow de deploy via GitHub Actions 
├── app/ 
│ ├── api/ │
│ └── endpoints/ # Endpoints da API │ ├── chatbot/ # Lógica do chatbot │ ├── core/ # Configurações, middlewares, autenticação 
│ ├── db/ 
│ │ └── mongo_client.py # Conexão com o MongoDB 
│ ├── models/ # Modelos de dados (ODM/ORM) 
│ ├── schemas/ # Schemas Pydantic para validação 
│ ├── services/ # Lógica de negócio e integração externa 
│ ├── tests/ # Testes automatizados │ ├── main.py # Ponto de entrada da aplicação FastAPI 
│ └── init.py 
├── requirements.txt # Dependências da aplicação 
├── Dockerfile # Definição da imagem Docker 
└── README.md # Documentação do projeto
```


## 📦 Requisitos

- **Linguagem**: Python 3.9+
- **Banco de Dados**: MongoDB
- **APIs Externas**:
  - [OpenAI API](https://platform.openai.com/)
  - [Pinecone API](https://www.pinecone.io/)
  - [Google Cloud Translate API](https://cloud.google.com/translate)

- **Opcional**:
  - Docker (para containerização e deploy simplificado)

## 🔧 Instalação

1. **Clonar o repositório**:
   ```bash
   git clone https://github.com/user/repo.git
   cd repo
   ```

## ⚙ Configuração

Antes de rodar a aplicação, defina as variáveis de ambiente em um arquivo .env na raiz do projeto:

```bash
MONGO_URI="mongodb+srv://<user>:<password>@<cluster>/dbname"
SECRET_KEY="sua_chave_secreta_da_api"
OPENAI_API_KEY="sua_chave_openai"
GOOGLE_CREDENTIALS='{"type":"service_account","project_id":"..."}'
SENDER_PASSWORD="sua_chave_de_aplicacao_do_email"
PINECONE_API_KEY="sua_chave_pinecone"
VECTORSTORE="nome_do_vectorstore_no_pinecone"
```

## 🚀 Uso

Rodando Localmente
```bash 
docker build -t image-name . 
docker run -p 8000:80 image-name
```

A API estará disponível em ```http://localhost:8000```

## 💻 Desenvolvimento

### 🕒 Tarefas Agendadas (APScheduler)

O sistema utiliza o [APScheduler](https://apscheduler.readthedocs.io/) para gerenciar tarefas agendadas, garantindo a atualização contínua dos dados e métricas essenciais.

- **Ingestão Diária de Dados**:
  - **Descrição**: Realiza a ingestão e atualização diária dos dados do [ClinicalTrials.gov](https://clinicaltrials.gov/).
  - **Frequência**: Diária
  - **Horário**: 2:00 UTC


- **Atualização de Métricas**:
  - **Descrição**: Recalcula métricas e indicadores para análises atualizadas.
  - **Frequência**: Horária
  - **Implementação**: Configurada como uma tarefa do tipo `interval` dentro do APScheduler.


### 🔍 Busca Híbrida

A funcionalidade de busca híbrida combina múltiplas fontes de dados e técnicas avançadas para fornecer resultados precisos e relevantes.

- **Fontes de Dados**:
  - **API do ClinicalTrials.gov**: Recupera dados atualizados diretamente da API pública.
  - **MongoDB Local**: Armazena dados localmente para acesso rápido e consultas adicionais.
  - **Busca Vetorial Semântica via Pinecone**: Utiliza embeddings semânticos para melhorar a relevância dos resultados.

- **Embeddings**:
  - **Modelo Utilizado**: `text-embedding-3-large` da OpenAI.
  - **Dimensão dos Vetores**: 3072.
  - **Descrição**: Os embeddings são gerados para capturar o significado semântico dos textos, permitindo uma busca mais inteligente e contextual.

### 🔐 Autenticação

A segurança do sistema é garantida através da implementação de autenticação baseada em JWT (JSON Web Tokens).

- **Mecanismo**:
  - **JWT**: Tokens são emitidos para usuários autenticados, permitindo acesso seguro a endpoints protegidos.
  - **Middleware de Autenticação**: Um middleware gerencia a verificação dos tokens JWT em cada requisição em rotas protegidas, assegurando que apenas usuários autorizados possam acessar recursos sensíveis.




## 📝 Endpoints da API

#### 🔐 Autenticação

- **POST /auth/register**
  - **Descrição**: Registra um usuário
  - **Corpo**:
    ```json
    {
      "username": "string",
      "email": "string",
      "password": "string"
    }
    ```
  - **Resposta**: `201 Created`

- **POST /auth/login**
  - **Descrição**: Login do usuário
  - **Corpo**:
    ```json
    {
      "email": "string",
      "password": "string"
    }
    ```
  - **Resposta**: `200 OK` com token JWT

- **POST /auth/verify**
  - **Descrição**: Verifica token JWT
  - **Corpo**:
    ```json
    {
      "token": "string"
    }
    ```
  - **Resposta**: `200 OK` se o token for válido

#### 🔍 Busca

- **POST /search/paciente**
  - **Descrição**: Pesquisa de estudo por paciente
  - **Corpo**:
    ```json
    {
      "keywords": "string?",
      "condition": "string?",
      "status": ["string"]?,
      "location": "string?",
      "intervention": "string?",
      "sponsor": "string?",
      "age": "string?",
      "sex": "string?"
    }
    ```
  - **Resposta**: `200 OK` com lista de estudos

- **POST /search/medico**
  - **Descrição**: Busca avançada para profissionais de saúde
  - **Corpo**:
    ```json
    {
      "title": "string?",
      "keywords": "string?",
      "condition": "string?",
      "status": ["string"]?,
      "location": "string?",
      "intervention": "string?",
      "sponsor": "string?",
      "age": "string?",
      "sex": "string?",
      "acceptsHealthyVolunteers": "boolean?",
      "studyPhase": "string?",
      "studyType": "string?",
      "hasResults": "boolean?",
      "organization": "string?",
      "studyId": "string?"
    }
    ```
  - **Resposta**: `200 OK` com lista de estudos

- **POST /search/advanced**
  - **Descrição**: Busca especialista com consulta personalizada
  - **Corpo**:
    ```json
    {
      "query": "string"
    }
    ```
  - **Resposta**: `200 OK` com lista de estudos

#### 📋 Estudos

- **POST /study**
  - **Descrição**: Cria um novo estudo
  - **Corpo**: `CreateStudySchema`
  - **Resposta**: `201 Created`

- **GET /study**
  - **Descrição**: Obtém todos os estudos
  - **Parâmetros de Query**:
    - `status`: Filtrar por status do estudo
  - **Cabeçalho**: Bearer token
  - **Resposta**: `200 OK` com lista de estudos

- **PUT /study/approve/{study_id}**
  - **Descrição**: Aprova um estudo
  - **Parâmetro de Caminho**: `study_id`
  - **Cabeçalho**: Bearer token
  - **Resposta**: `200 OK`

- **PUT /study/reject/{study_id}**
  - **Descrição**: Rejeita um estudo
  - **Parâmetro de Caminho**: `study_id`
  - **Cabeçalho**: Bearer token
  - **Resposta**: `200 OK`

#### Análise de Dados

- **GET /data/metrics**
  - **Descrição**: Obtém métricas do sistema
  - **Resposta**: `200 OK` com:
    ```json
    {
      "main_diseases": [],
      "representatividade": {},
      "top_centers": [],
      "types_per_centers": {},
      "main_treatments": [],
      "phase_percentages": []
    }
    ```

#### 📧 Email

- **POST /email/send**
  - **Descrição**: Envia resultados de estudos por email
  - **Corpo**:
    ```json
    {
      "email": "string",
      "studies": []
    }
    ```
  - **Resposta**: `200 OK` com arquivo Excel

#### 🤖 Chatbot

- **POST /chatbot/workflow**
  - **Descrição**: Processa interação do chatbot
  - **Corpo**: `GraphState`
    ```json
    {
      "user_message": "string",
      "has_doenca": "boolean?",
      "studies_list": "object?",
      "chat_history": [
        {
          "text": "string",
          "sender": "string"
        }
      ]
    }
    ```
  - **Resposta**: `200 OK` com estado do grafo (mesmo schema da entrada, só que constando com a resposta do chatbot e, caso tenha sido realizada uma busca, os estudos.)

#### 👤 Gestão de Usuários

- **GET /user/{user_id}**
  - **Descrição**: Obtém detalhes do usuário
  - **Parâmetro de Caminho**: `user_id`
  - **Resposta**: `200 OK` com dados do usuário

- **PUT /user/{user_id}**
  - **Descrição**: Atualiza detalhes do usuário
  - **Parâmetro de Caminho**: `user_id`
  - **Corpo**: `UpdateUserSchema`
  - **Resposta**: `200 OK`

- **DELETE /user/{user_id}**
  - **Descrição**: Deleta um usuário
  - **Parâmetro de Caminho**: `user_id`
  - **Resposta**: `200 OK`








### 🚢 Deploy

A aplicação possui um workflow de deploy via GitHub Actions (.github/workflows/deploy.yml). Para automatizar o deploy, ajuste o workflow de acordo com sua infraestrutura (AWS, GCP, Azure, etc.). 




