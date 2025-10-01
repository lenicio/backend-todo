# API de Lista de Tarefas com Documentação Swagger 📋

Uma API RESTful completa para gerenciamento de tarefas com autenticação de usuários, desenvolvida em Python com Flask e documentação Swagger/OpenAPI integrada.

## 🚀 Funcionalidades

- ✅ **Autenticação JWT** - Login seguro com tokens
- 👤 **Registro de usuários** - Criação de novas contas
- 📝 **CRUD completo de tarefas** - Criar, listar, atualizar e excluir
- 🔐 **Segurança** - Cada usuário acessa apenas suas próprias tarefas
- 💓 **Health Check** - Monitoramento da saúde da API
- 🗃️ **SQLite** - Banco de dados local, sem configuração adicional
- 📚 **Documentação Swagger** - Interface interativa para testar a API

## 📦 Instalação

1. **Clone ou baixe o projeto:**
```bash
# Navegue até a pasta do projeto
cd Todo
```

2. **Ative o ambiente virtual:**
```bash
# Windows
.\.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

3. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

4. **Execute a API:**
```bash
python app.py
```

A API estará disponível em: `http://localhost:5000`
**Documentação Swagger:** `http://localhost:5000/docs/`

## � Documentação Swagger

A API inclui documentação Swagger completa e interativa! Acesse `http://localhost:5000/docs/` para:

- **📖 Ver todos os endpoints** com descrições detalhadas
- **🧪 Testar a API diretamente** no navegador
- **📋 Ver modelos de dados** (schemas) de entrada e saída
- **🔐 Configurar autenticação** facilmente
- **📄 Baixar especificação OpenAPI** em JSON

### Como usar a documentação Swagger:

1. **Acesse** `http://localhost:5000/docs/`
2. **Registre um usuário** usando o endpoint `/registro`
3. **Faça login** no endpoint `/login` para obter um token
4. **Configure a autenticação:**
   - Clique em "Authorize" (cadeado verde)
   - Digite: `Bearer SEU_TOKEN_AQUI`
   - Clique em "Authorize"
5. **Teste os endpoints** de tarefas protegidos

## 🔗 Endpoints da API

### 🏥 Saúde
- `GET /health` - Verificar status da API

### 👤 Autenticação
- `POST /registro` - Registrar novo usuário
- `POST /login` - Fazer login e obter token JWT

### 📝 Tarefas (Requer autenticação)
- `GET /tarefas` - Listar todas as tarefas do usuário
- `POST /tarefas` - Criar nova tarefa
- `GET /tarefas/{id}` - Obter tarefa específica
- `PUT /tarefas/{id}` - Atualizar tarefa
- `DELETE /tarefas/{id}` - Excluir tarefa

## 🧪 Testando com Swagger

### 1. Registro de usuário
```json
POST /registro
{
    "nome": "João Silva",
    "email": "joao@email.com", 
    "senha": "senha123"
}
```

### 2. Login
```json
POST /login
{
    "email": "joao@email.com",
    "senha": "senha123"
}
```

### 3. Configurar token no Swagger
- Copie o token da resposta do login
- Clique em "Authorize" 
- Digite: `Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...`

### 4. Criar tarefa
```json
POST /tarefas
{
    "titulo": "Estudar Python",
    "descricao": "Revisar conceitos de POO"
}
```

## 🔧 Tecnologias Utilizadas

- **Python 3.x** - Linguagem de programação
- **Flask 3.0.0** - Framework web
- **Flask-RESTX 1.3.0** - Integração com Swagger/OpenAPI
- **SQLite** - Banco de dados
- **PyJWT** - Autenticação JWT
- **Flask-CORS** - Cross-Origin Resource Sharing

## 📊 Modelos de Dados

### Usuário
```json
{
    "id": 1,
    "nome": "João Silva",
    "email": "joao@email.com",
    "data_criacao": "2025-10-01 10:30:00"
}
```

### Tarefa
```json
{
    "id": 1,
    "titulo": "Estudar Python",
    "descricao": "Revisar conceitos de POO",
    "concluida": false,
    "data_criacao": "2025-10-01 10:30:00",
    "data_atualizacao": "2025-10-01 10:30:00",
    "usuario_id": 1
}
```

## 🛡️ Segurança

- **Autenticação JWT** com expiração de 24 horas
- **Isolamento de dados** - usuários só acessam suas próprias tarefas
- **Validação de entrada** em todos os endpoints
- **Hash de senhas** com Werkzeug
- **CORS configurado** para desenvolvimento

## 🌐 URLs Importantes

- **API Base:** `http://localhost:5000`
- **Documentação Swagger:** `http://localhost:5000/docs/`
- **Health Check:** `http://localhost:5000/health`
- **Especificação OpenAPI:** `http://localhost:5000/swagger.json`

---

🎉 **Uma API profissional com documentação Swagger completa!** 

Acesse `http://localhost:5000/docs/` e explore todos os recursos interativos da documentação.

### 2. Registrar um novo usuário

```bash
POST http://localhost:5000/registro
Content-Type: application/json

{
    "nome": "João Silva",
    "email": "joao@email.com",
    "senha": "minhasenha123"
}
```

**Resposta esperada:**
```json
{
    "mensagem": "Usuário criado com sucesso!",
    "usuario": {
        "id": 1,
        "nome": "João Silva",
        "email": "joao@email.com",
        "data_criacao": "2025-10-01T10:30:00"
    }
}
```

### 3. Fazer login

```bash
POST http://localhost:5000/login
Content-Type: application/json

{
    "email": "joao@email.com",
    "senha": "minhasenha123"
}
```

**Resposta esperada:**
```json
{
    "mensagem": "Login realizado com sucesso!",
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "usuario": {
        "id": 1,
        "nome": "João Silva",
        "email": "joao@email.com"
    }
}
```

**⚠️ IMPORTANTE:** Salve o token retornado! Você precisará dele para as próximas requisições.

### 4. Criar uma nova tarefa

```bash
POST http://localhost:5000/tarefas
Authorization: Bearer SEU_TOKEN_AQUI
Content-Type: application/json

{
    "titulo": "Estudar Python",
    "descricao": "Revisar conceitos de POO"
}
```

**Resposta esperada:**
```json
{
    "mensagem": "Tarefa criada com sucesso!",
    "tarefa": {
        "id": 1,
        "titulo": "Estudar Python",
        "descricao": "Revisar conceitos de POO",
        "concluida": false,
        "data_criacao": "2025-10-01T10:30:00",
        "data_atualizacao": "2025-10-01T10:30:00",
        "usuario_id": 1
    }
}
```

### 5. Listar todas as tarefas

```bash
GET http://localhost:5000/tarefas
Authorization: Bearer SEU_TOKEN_AQUI
```

**Resposta esperada:**
```json
{
    "tarefas": [
        {
            "id": 1,
            "titulo": "Estudar Python",
            "descricao": "Revisar conceitos de POO",
            "concluida": false,
            "data_criacao": "2025-10-01T10:30:00",
            "data_atualizacao": "2025-10-01T10:30:00",
            "usuario_id": 1
        }
    ],
    "total": 1
}
```

### 6. Obter uma tarefa específica

```bash
GET http://localhost:5000/tarefas/1
Authorization: Bearer SEU_TOKEN_AQUI
```

### 7. Atualizar uma tarefa

```bash
PUT http://localhost:5000/tarefas/1
Authorization: Bearer SEU_TOKEN_AQUI
Content-Type: application/json

{
    "titulo": "Estudar Python Avançado",
    "descricao": "Revisar conceitos de POO e decorators",
    "concluida": true
}
```

### 8. Excluir uma tarefa

```bash
DELETE http://localhost:5000/tarefas/1
Authorization: Bearer SEU_TOKEN_AQUI
```

**Resposta esperada:**
```json
{
    "mensagem": "Tarefa excluída com sucesso!"
}
```

## 📋 Resumo das Rotas

| Método | Rota | Autenticação | Descrição |
|--------|------|--------------|-----------|
| GET | `/health` | ❌ | Verificar saúde da API |
| POST | `/registro` | ❌ | Registrar novo usuário |
| POST | `/login` | ❌ | Fazer login e obter token |
| GET | `/tarefas` | ✅ | Listar todas as tarefas do usuário |
| POST | `/tarefas` | ✅ | Criar nova tarefa |
| GET | `/tarefas/<id>` | ✅ | Obter tarefa específica |
| PUT | `/tarefas/<id>` | ✅ | Atualizar tarefa |
| DELETE | `/tarefas/<id>` | ✅ | Excluir tarefa |

## 🔧 Testando com Ferramentas

### Usando curl:

```bash
# Registrar usuário
curl -X POST http://localhost:5000/registro \
  -H "Content-Type: application/json" \
  -d '{"nome":"João Silva","email":"joao@email.com","senha":"minhasenha123"}'

# Fazer login
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"email":"joao@email.com","senha":"minhasenha123"}'

# Criar tarefa (substitua SEU_TOKEN_AQUI pelo token recebido)
curl -X POST http://localhost:5000/tarefas \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{"titulo":"Estudar Python","descricao":"Revisar POO"}'
```

### Usando Postman ou Insomnia:

1. Importe as rotas acima
2. Configure o cabeçalho `Authorization: Bearer SEU_TOKEN` para rotas protegidas
3. Use `Content-Type: application/json` para requisições POST/PUT

## 🏗️ Estrutura do Projeto

```
Todo/
├── app.py              # Arquivo principal da API
├── requirements.txt    # Dependências do projeto
├── README.md          # Esta documentação
└── todo_list.db       # Banco SQLite (criado automaticamente)
```

## 🛡️ Segurança

- Senhas são criptografadas com hash seguro
- Tokens JWT expiram em 24 horas
- Cada usuário só acessa suas próprias tarefas
- Banco SQLite local e seguro

## 🎓 Para Professores

Esta API é ideal para aulas de front-end porque:

- **Simples de executar** - Apenas `python app.py`
- **Bem documentada** - Exemplos claros para os alunos
- **Realista** - Inclui autenticação como APIs reais
- **Flexível** - Permite focar no front-end sem complexidade backend
- **Completa** - Todas as operações CRUD necessárias
- **Compatível** - Funciona em qualquer máquina com Python

## 🆘 Resolução de Problemas

### Erro "Token é obrigatório":
- Certifique-se de incluir o cabeçalho: `Authorization: Bearer SEU_TOKEN`

### Erro "Token inválido":
- Faça login novamente para obter um novo token
- Verifique se copiou o token completo

### Erro de CORS:
- A API já tem CORS habilitado para desenvolvimento
- Se necessário, configure domínios específicos no código

### Banco de dados:
- O arquivo `todo_list.db` é criado automaticamente
- Para resetar os dados, delete o arquivo e reinicie a API

## 📞 Suporte

Para dúvidas sobre a API, consulte os comentários no código em `app.py` ou teste as rotas usando os exemplos acima.

---

**Desenvolvido para uso educacional** 🎓