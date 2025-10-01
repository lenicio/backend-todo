"""
API de Lista de Tarefas com Documentação Swagger
===============================================
Uma API RESTful para gerenciamento de tarefas com autenticação JWT.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import jwt
import datetime
from functools import wraps
import os
from flasgger import Swagger, swag_from

# Configuração da aplicação
app = Flask(__name__)
app.config['SECRET_KEY'] = 'chave-super-secreta-para-aula'

# Configuração do Flasgger (OpenAPI 3)
app.config['SWAGGER'] = {
    'title': 'API de Lista de Tarefas',
    'version': '1.0.0',
    'openapi': '3.0.2',
    'description': 'Uma API RESTful para gerenciamento de tarefas com autenticação JWT.',
    'termsOfService': 'http://example.com/terms',
    'contact': {
        'name': 'Lenício Jr',
        'email': 'lenicio.junior@gmail.com'
    },
    'license': {
        'name': 'Apache 2.0',
        'url': 'http://www.apache.org/licenses/LICENSE-2.0.html'
    },
    'components': {
        'securitySchemes': {
            'BearerAuth': {
                'type': 'http',
                'scheme': 'bearer',
                'bearerFormat': 'JWT'
            }
        }
    },
    'security': [{'BearerAuth': []}]
}
swagger = Swagger(app)

# CORS para desenvolvimento
CORS(app, origins="*", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

# Banco de dados
DATABASE = 'todo_list.db'

def init_db():
    """Inicializa o banco de dados SQLite."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Criar tabela de usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Criar tabela de tarefas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tarefas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descricao TEXT,
            concluida BOOLEAN DEFAULT 0,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            usuario_id INTEGER NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Obtém uma conexão com o banco de dados."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def token_obrigatorio(f):
    """Decorator para proteger rotas que precisam de autenticação."""
    @wraps(f)
    def decorado(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization'].strip()
            
            # Verificar diferentes formatos possíveis
            if auth_header.lower().startswith('bearer '):
                token = auth_header[7:].strip()  # Remove "Bearer " (case insensitive)
            elif ' ' in auth_header:
                # Formato: "Bearer token" ou "bearer token"
                parts = auth_header.split()
                if len(parts) >= 2 and parts[0].lower() in ['bearer', 'token']:
                    token = parts[1].strip()
                else:
                    return jsonify({'mensagem': 'Formato de token inválido! Use: Bearer <token>'}), 401
            else:
                # Se não tem espaço, pode ser só o token (fallback)
                token = auth_header.strip()
        
        if not token:
            return jsonify({'mensagem': 'Token é obrigatório!'}), 401
        
        try:
            dados = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            conn = get_db_connection()
            usuario_atual = conn.execute('SELECT * FROM usuarios WHERE id = ?', (dados['usuario_id'],)).fetchone()
            conn.close()
            
            if not usuario_atual:
                return jsonify({'mensagem': 'Usuário não encontrado!'}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({'mensagem': 'Token expirado!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'mensagem': 'Token inválido!'}), 401
        
        return f(dict(usuario_atual), *args, **kwargs)
    
    return decorado

# Rotas da API

@app.route('/health', methods=['GET'])
def health_check():
    """Verificar status da API e banco de dados
    ---
    tags:
      - Health
    summary: Verifica a saúde da API
    description: Retorna o status da aplicação, versão e se a conexão com o banco de dados está ativa.
    responses:
      200:
        description: A API está funcionando corretamente.
        content:
          application/json:
            schema:
              type: object
              properties:
                status:
                  type: string
                  example: OK
                mensagem:
                  type: string
                  example: API funcionando corretamente!
                banco_dados:
                  type: string
                  example: conectado
      500:
        description: A API ou o banco de dados encontraram um problema.
    """
    try:
        conn = get_db_connection()
        conn.execute('SELECT 1')
        conn.close()
        
        return jsonify({
            'status': 'OK',
            'mensagem': 'API funcionando corretamente!',
            'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'versao': '1.0.0',
            'banco_dados': 'conectado'
        })
    except Exception as e:
        return jsonify({
            'status': 'ERRO',
            'mensagem': 'Problemas na API',
            'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'versao': '1.0.0',
            'banco_dados': 'desconectado'
        }), 500

@app.route('/registro', methods=['POST'])
def registro_usuario():
    """Registrar novo usuário
    ---
    tags:
      - Autenticação
    summary: Cria um novo usuário no sistema.
    description: Registra um usuário com nome, email e senha. O email deve ser único.
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              nome:
                type: string
                example: "Usuário Teste"
              email:
                type: string
                format: email
                example: "teste@example.com"
              senha:
                type: string
                format: password
                example: "senha123"
            required:
              - nome
              - email
              - senha
    responses:
      201:
        description: Usuário criado com sucesso.
      400:
        description: Dados de entrada inválidos.
      409:
        description: O email fornecido já está em uso.
      500:
        description: Erro interno do servidor.
    """
    try:
        dados = request.get_json()
        
        if not dados or not dados.get('nome') or not dados.get('email') or not dados.get('senha'):
            return jsonify({'erro': 'Nome, email e senha são obrigatórios!'}), 400
        
        conn = get_db_connection()
        
        # Verificar se email já existe
        usuario_existente = conn.execute('SELECT id FROM usuarios WHERE email = ?', (dados['email'],)).fetchone()
        if usuario_existente:
            conn.close()
            return jsonify({'erro': 'Este email já está sendo usado!'}), 409
        
        # Criar novo usuário
        senha_hash = generate_password_hash(dados['senha'])
        cursor = conn.execute(
            'INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)',
            (dados['nome'], dados['email'], senha_hash)
        )
        
        usuario_id = cursor.lastrowid
        novo_usuario = conn.execute('SELECT * FROM usuarios WHERE id = ?', (usuario_id,)).fetchone()
        conn.commit()
        conn.close()
        
        return jsonify({
            'mensagem': 'Usuário criado com sucesso!',
            'usuario': {
                'id': novo_usuario['id'],
                'nome': novo_usuario['nome'],
                'email': novo_usuario['email'],
                'data_criacao': novo_usuario['data_criacao']
            }
        }), 201
        
    except Exception as e:
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@app.route('/login', methods=['POST'])
def login_usuario():
    """Autenticar usuário e obter token JWT
    ---
    tags:
      - Autenticação
    summary: Realiza o login de um usuário.
    description: Autentica um usuário com email e senha e retorna um token JWT para acesso às rotas protegidas.
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              email:
                type: string
                format: email
                example: "teste@example.com"
              senha:
                type: string
                format: password
                example: "senha123"
            required:
              - email
              - senha
    responses:
      200:
        description: Login bem-sucedido, retorna o token JWT.
      400:
        description: Email ou senha não fornecidos.
      401:
        description: Credenciais inválidas.
      500:
        description: Erro interno do servidor.
    """
    try:
        dados = request.get_json()
        
        if not dados or not dados.get('email') or not dados.get('senha'):
            return jsonify({'erro': 'Email e senha são obrigatórios!'}), 400
        
        conn = get_db_connection()
        usuario = conn.execute('SELECT * FROM usuarios WHERE email = ?', (dados['email'],)).fetchone()
        conn.close()
        
        if not usuario or not check_password_hash(usuario['senha'], dados['senha']):
            return jsonify({'erro': 'Email ou senha incorretos!'}), 401
        
        # Gerar token JWT
        token = jwt.encode({
            'usuario_id': usuario['id'],
            'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'mensagem': 'Login realizado com sucesso!',
            'token': token,
            'usuario': {
                'id': usuario['id'],
                'nome': usuario['nome'],
                'email': usuario['email']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@app.route('/tarefas', methods=['GET'])
@token_obrigatorio
def listar_tarefas(usuario_atual):
    """Listar todas as tarefas do usuário
    ---
    tags:
      - Tarefas
    summary: Lista todas as tarefas do usuário autenticado.
    description: Retorna uma lista de todas as tarefas associadas ao usuário que fez a requisição. Requer autenticação.
    security:
      - BearerAuth: []
    responses:
      200:
        description: Lista de tarefas retornada com sucesso.
      401:
        description: Token de autenticação inválido ou ausente.
      500:
        description: Erro interno do servidor.
    """
    try:
        conn = get_db_connection()
        tarefas = conn.execute(
            'SELECT * FROM tarefas WHERE usuario_id = ? ORDER BY data_criacao DESC',
            (usuario_atual['id'],)
        ).fetchall()
        conn.close()
        
        tarefas_lista = []
        for tarefa in tarefas:
            tarefas_lista.append({
                'id': tarefa['id'],
                'titulo': tarefa['titulo'],
                'descricao': tarefa['descricao'],
                'concluida': bool(tarefa['concluida']),
                'data_criacao': tarefa['data_criacao'],
                'data_atualizacao': tarefa['data_atualizacao'],
                'usuario_id': tarefa['usuario_id']
            })
        
        return jsonify({
            'tarefas': tarefas_lista,
            'total': len(tarefas_lista)
        }), 200
        
    except Exception as e:
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@app.route('/tarefas', methods=['POST'])
@token_obrigatorio
def criar_tarefa(usuario_atual):
    """Criar nova tarefa
    ---
    tags:
      - Tarefas
    summary: Cria uma nova tarefa para o usuário autenticado.
    description: Adiciona uma nova tarefa à lista do usuário. O título é obrigatório. Requer autenticação.
    security:
      - BearerAuth: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              titulo:
                type: string
                example: "Comprar pão"
              descricao:
                type: string
                example: "Ir à padaria da esquina."
            required:
              - titulo
    responses:
      201:
        description: Tarefa criada com sucesso.
      400:
        description: Título da tarefa não fornecido.
      401:
        description: Token de autenticação inválido ou ausente.
      500:
        description: Erro interno do servidor.
    """
    try:
        dados = request.get_json()
        
        if not dados or not dados.get('titulo'):
            return jsonify({'erro': 'Título é obrigatório!'}), 400
        
        conn = get_db_connection()
        cursor = conn.execute(
            'INSERT INTO tarefas (titulo, descricao, usuario_id) VALUES (?, ?, ?)',
            (dados['titulo'], dados.get('descricao', ''), usuario_atual['id'])
        )
        
        tarefa_id = cursor.lastrowid
        nova_tarefa = conn.execute('SELECT * FROM tarefas WHERE id = ?', (tarefa_id,)).fetchone()
        conn.commit()
        conn.close()
        
        return jsonify({
            'mensagem': 'Tarefa criada com sucesso!',
            'tarefa': {
                'id': nova_tarefa['id'],
                'titulo': nova_tarefa['titulo'],
                'descricao': nova_tarefa['descricao'],
                'concluida': bool(nova_tarefa['concluida']),
                'data_criacao': nova_tarefa['data_criacao'],
                'data_atualizacao': nova_tarefa['data_atualizacao'],
                'usuario_id': nova_tarefa['usuario_id']
            }
        }), 201
        
    except Exception as e:
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@app.route('/tarefas/<int:tarefa_id>', methods=['GET'])
@token_obrigatorio
def obter_tarefa(usuario_atual, tarefa_id):
    """Obter tarefa específica por ID
    ---
    tags:
      - Tarefas
    summary: Obtém os detalhes de uma tarefa específica.
    description: Retorna os dados de uma única tarefa, se ela pertencer ao usuário autenticado. Requer autenticação.
    security:
      - BearerAuth: []
    parameters:
      - name: tarefa_id
        in: path
        required: true
        description: O ID da tarefa a ser recuperada.
        schema:
          type: integer
    responses:
      200:
        description: Detalhes da tarefa retornados com sucesso.
      401:
        description: Token de autenticação inválido ou ausente.
      404:
        description: Tarefa não encontrada.
      500:
        description: Erro interno do servidor.
    """
    try:
        conn = get_db_connection()
        tarefa = conn.execute(
            'SELECT * FROM tarefas WHERE id = ? AND usuario_id = ?',
            (tarefa_id, usuario_atual['id'])
        ).fetchone()
        conn.close()
        
        if not tarefa:
            return jsonify({'erro': 'Tarefa não encontrada!'}), 404
        
        return jsonify({
            'tarefa': {
                'id': tarefa['id'],
                'titulo': tarefa['titulo'],
                'descricao': tarefa['descricao'],
                'concluida': bool(tarefa['concluida']),
                'data_criacao': tarefa['data_criacao'],
                'data_atualizacao': tarefa['data_atualizacao'],
                'usuario_id': tarefa['usuario_id']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@app.route('/tarefas/<int:tarefa_id>', methods=['PUT'])
@token_obrigatorio
def atualizar_tarefa(usuario_atual, tarefa_id):
    """Atualizar tarefa específica
    ---
    tags:
      - Tarefas
    summary: Atualiza uma tarefa existente.
    description: Modifica o título, a descrição ou o status de conclusão de uma tarefa. Requer autenticação.
    security:
      - BearerAuth: []
    parameters:
      - name: tarefa_id
        in: path
        required: true
        description: O ID da tarefa a ser atualizada.
        schema:
          type: integer
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              titulo:
                type: string
                example: "Comprar leite integral"
              descricao:
                type: string
                example: "Não esquecer que é o integral."
              concluida:
                type: boolean
                example: false
    responses:
      200:
        description: Tarefa atualizada com sucesso.
      400:
        description: Dados de entrada inválidos.
      401:
        description: Token de autenticação inválido ou ausente.
      404:
        description: Tarefa não encontrada.
      500:
        description: Erro interno do servidor.
    """
    try:
        conn = get_db_connection()
        tarefa = conn.execute(
            'SELECT * FROM tarefas WHERE id = ? AND usuario_id = ?',
            (tarefa_id, usuario_atual['id'])
        ).fetchone()
        
        if not tarefa:
            conn.close()
            return jsonify({'erro': 'Tarefa não encontrada!'}), 404
        
        dados = request.get_json()
        if not dados:
            conn.close()
            return jsonify({'erro': 'Dados não fornecidos!'}), 400
        
        # Preparar campos para atualização
        titulo = dados.get('titulo', tarefa['titulo'])
        descricao = dados.get('descricao', tarefa['descricao'])
        concluida = dados.get('concluida', tarefa['concluida'])
        
        if 'titulo' in dados and not dados['titulo']:
            conn.close()
            return jsonify({'erro': 'Título não pode estar vazio!'}), 400
        
        # Atualizar tarefa
        conn.execute(
            '''UPDATE tarefas 
               SET titulo = ?, descricao = ?, concluida = ?, data_atualizacao = ? 
               WHERE id = ? AND usuario_id = ?''',
            (titulo, descricao, concluida, datetime.datetime.now(datetime.timezone.utc).isoformat(), tarefa_id, usuario_atual['id'])
        )
        
        # Buscar tarefa atualizada
        tarefa_atualizada = conn.execute('SELECT * FROM tarefas WHERE id = ?', (tarefa_id,)).fetchone()
        conn.commit()
        conn.close()
        
        return jsonify({
            'mensagem': 'Tarefa atualizada com sucesso!',
            'tarefa': {
                'id': tarefa_atualizada['id'],
                'titulo': tarefa_atualizada['titulo'],
                'descricao': tarefa_atualizada['descricao'],
                'concluida': bool(tarefa_atualizada['concluida']),
                'data_criacao': tarefa_atualizada['data_criacao'],
                'data_atualizacao': tarefa_atualizada['data_atualizacao'],
                'usuario_id': tarefa_atualizada['usuario_id']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@app.route('/tarefas/<int:tarefa_id>', methods=['DELETE'])
@token_obrigatorio
def excluir_tarefa(usuario_atual, tarefa_id):
    """Excluir tarefa específica
    ---
    tags:
      - Tarefas
    summary: Exclui uma tarefa.
    description: Remove permanentemente uma tarefa do banco de dados. Requer autenticação.
    security:
      - BearerAuth: []
    parameters:
      - name: tarefa_id
        in: path
        required: true
        description: O ID da tarefa a ser excluída.
        schema:
          type: integer
    responses:
      200:
        description: Tarefa excluída com sucesso.
      401:
        description: Token de autenticação inválido ou ausente.
      404:
        description: Tarefa não encontrada.
      500:
        description: Erro interno do servidor.
    """
    try:
        conn = get_db_connection()
        tarefa = conn.execute(
            'SELECT * FROM tarefas WHERE id = ? AND usuario_id = ?',
            (tarefa_id, usuario_atual['id'])
        ).fetchone()
        
        if not tarefa:
            conn.close()
            return jsonify({'erro': 'Tarefa não encontrada!'}), 404
        
        conn.execute('DELETE FROM tarefas WHERE id = ? AND usuario_id = ?', (tarefa_id, usuario_atual['id']))
        conn.commit()
        conn.close()
        
        return jsonify({'mensagem': 'Tarefa excluída com sucesso!'}), 200
        
    except Exception as e:
        return jsonify({'erro': 'Erro interno do servidor'}), 500

# ===== ROTA PARA SERVIR A ESPECIFICAÇÃO OPENAPI =====

@app.route('/api-spec.json')
def serve_openapi_spec():
    """
    Serve o arquivo de especificação OpenAPI 3 em formato JSON.
    """
    # Criar a especificação manualmente baseada na configuração
    spec = {
        "openapi": "3.0.2",
        "info": {
            "title": app.config['SWAGGER']['title'],
            "version": app.config['SWAGGER']['version'],
            "description": app.config['SWAGGER']['description'],
            "termsOfService": app.config['SWAGGER']['termsOfService'],
            "contact": app.config['SWAGGER']['contact'],
            "license": app.config['SWAGGER']['license']
        },
        "components": app.config['SWAGGER']['components'],
        "security": app.config['SWAGGER']['security'],
        "servers": [
            {
                "url": "http://localhost:5000",
                "description": "Servidor de desenvolvimento"
            }
        ],
        "paths": {
            "/health": {
                "get": {
                    "tags": ["Health"],
                    "summary": "Verifica a saúde da API",
                    "description": "Retorna o status da aplicação, versão e se a conexão com o banco de dados está ativa.",
                    "responses": {
                        "200": {
                            "description": "A API está funcionando corretamente.",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string", "example": "OK"},
                                            "mensagem": {"type": "string", "example": "API funcionando corretamente!"},
                                            "banco_dados": {"type": "string", "example": "conectado"}
                                        }
                                    }
                                }
                            }
                        },
                        "500": {
                            "description": "A API ou o banco de dados encontraram um problema."
                        }
                    }
                }
            },
            "/registro": {
                "post": {
                    "tags": ["Autenticação"],
                    "summary": "Cria um novo usuário no sistema.",
                    "description": "Registra um usuário com nome, email e senha. O email deve ser único.",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "nome": {"type": "string", "example": "Usuário Teste"},
                                        "email": {"type": "string", "format": "email", "example": "teste@example.com"},
                                        "senha": {"type": "string", "format": "password", "example": "senha123"}
                                    },
                                    "required": ["nome", "email", "senha"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {"description": "Usuário criado com sucesso."},
                        "400": {"description": "Dados de entrada inválidos."},
                        "409": {"description": "O email fornecido já está em uso."},
                        "500": {"description": "Erro interno do servidor."}
                    }
                }
            },
            "/login": {
                "post": {
                    "tags": ["Autenticação"],
                    "summary": "Realiza o login de um usuário.",
                    "description": "Autentica um usuário com email e senha e retorna um token JWT para acesso às rotas protegidas.",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "email": {"type": "string", "format": "email", "example": "teste@example.com"},
                                        "senha": {"type": "string", "format": "password", "example": "senha123"}
                                    },
                                    "required": ["email", "senha"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {"description": "Login bem-sucedido, retorna o token JWT."},
                        "400": {"description": "Email ou senha não fornecidos."},
                        "401": {"description": "Credenciais inválidas."},
                        "500": {"description": "Erro interno do servidor."}
                    }
                }
            },
            "/tarefas": {
                "get": {
                    "tags": ["Tarefas"],
                    "summary": "Lista todas as tarefas do usuário autenticado.",
                    "description": "Retorna uma lista de todas as tarefas associadas ao usuário que fez a requisição. Requer autenticação.",
                    "security": [{"BearerAuth": []}],
                    "responses": {
                        "200": {"description": "Lista de tarefas retornada com sucesso."},
                        "401": {"description": "Token de autenticação inválido ou ausente."},
                        "500": {"description": "Erro interno do servidor."}
                    }
                },
                "post": {
                    "tags": ["Tarefas"],
                    "summary": "Cria uma nova tarefa para o usuário autenticado.",
                    "description": "Adiciona uma nova tarefa à lista do usuário. O título é obrigatório. Requer autenticação.",
                    "security": [{"BearerAuth": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "titulo": {"type": "string", "example": "Comprar pão"},
                                        "descricao": {"type": "string", "example": "Ir à padaria da esquina."}
                                    },
                                    "required": ["titulo"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {"description": "Tarefa criada com sucesso."},
                        "400": {"description": "Título da tarefa não fornecido."},
                        "401": {"description": "Token de autenticação inválido ou ausente."},
                        "500": {"description": "Erro interno do servidor."}
                    }
                }
            },
            "/tarefas/{tarefa_id}": {
                "get": {
                    "tags": ["Tarefas"],
                    "summary": "Obtém os detalhes de uma tarefa específica.",
                    "description": "Retorna os dados de uma única tarefa, se ela pertencer ao usuário autenticado. Requer autenticação.",
                    "security": [{"BearerAuth": []}],
                    "parameters": [{
                        "name": "tarefa_id",
                        "in": "path",
                        "required": True,
                        "description": "O ID da tarefa a ser recuperada.",
                        "schema": {"type": "integer"}
                    }],
                    "responses": {
                        "200": {"description": "Detalhes da tarefa retornados com sucesso."},
                        "401": {"description": "Token de autenticação inválido ou ausente."},
                        "404": {"description": "Tarefa não encontrada."},
                        "500": {"description": "Erro interno do servidor."}
                    }
                },
                "put": {
                    "tags": ["Tarefas"],
                    "summary": "Atualiza uma tarefa existente.",
                    "description": "Modifica o título, a descrição ou o status de conclusão de uma tarefa. Requer autenticação.",
                    "security": [{"BearerAuth": []}],
                    "parameters": [{
                        "name": "tarefa_id",
                        "in": "path",
                        "required": True,
                        "description": "O ID da tarefa a ser atualizada.",
                        "schema": {"type": "integer"}
                    }],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "titulo": {"type": "string", "example": "Comprar leite integral"},
                                        "descricao": {"type": "string", "example": "Não esquecer que é o integral."},
                                        "concluida": {"type": "boolean", "example": False}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {"description": "Tarefa atualizada com sucesso."},
                        "400": {"description": "Dados de entrada inválidos."},
                        "401": {"description": "Token de autenticação inválido ou ausente."},
                        "404": {"description": "Tarefa não encontrada."},
                        "500": {"description": "Erro interno do servidor."}
                    }
                },
                "delete": {
                    "tags": ["Tarefas"],
                    "summary": "Exclui uma tarefa.",
                    "description": "Remove permanentemente uma tarefa do banco de dados. Requer autenticação.",
                    "security": [{"BearerAuth": []}],
                    "parameters": [{
                        "name": "tarefa_id",
                        "in": "path",
                        "required": True,
                        "description": "O ID da tarefa a ser excluída.",
                        "schema": {"type": "integer"}
                    }],
                    "responses": {
                        "200": {"description": "Tarefa excluída com sucesso."},
                        "401": {"description": "Token de autenticação inválido ou ausente."},
                        "404": {"description": "Tarefa não encontrada."},
                        "500": {"description": "Erro interno do servidor."}
                    }
                }
            }
        }
    }
    
    return jsonify(spec)

# ===== ROTA PARA DOCUMENTAÇÃO REDOC =====

@app.route('/docs')
def redoc_ui():
    """Serve a interface do Redoc."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Redoc</title>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
        <style>
            body {
                margin: 0;
                padding: 0;
            }
        </style>
    </head>
    <body>
        <redoc spec-url='/api-spec.json'></redoc>
        <script src="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"> </script>
    </body>
    </html>
    """

# ===== TRATAMENTO DE ERROS GLOBAIS =====

@app.errorhandler(404)
def nao_encontrado(error):
    """Trata erros 404 - Não encontrado."""
    return jsonify({'erro': 'Rota não encontrada!'}), 404

@app.errorhandler(405)
def metodo_nao_permitido(error):
    """Trata erros 405 - Método não permitido."""
    return jsonify({'erro': 'Método HTTP não permitido para esta rota!'}), 405

@app.errorhandler(500)
def erro_interno(error):
    """Trata erros 500 - Erro interno do servidor."""
    return jsonify({'erro': 'Erro interno do servidor!'}), 500

if __name__ == '__main__':
    init_db()
    print("✅ Banco inicializado")
    print("🚀 API rodando em: http://localhost:5000")
    
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    app.run(debug=debug, host='0.0.0.0', port=port)