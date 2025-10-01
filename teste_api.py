#!/usr/bin/env python3
"""
Script para testar a API Todo após remoção do Swagger
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_health():
    """Testar endpoint de health"""
    print("🔍 Testando endpoint /health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Resposta: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Erro: {e}")
        return False

def test_registro():
    """Testar endpoint de registro"""
    print("\n🔍 Testando endpoint /registro...")
    dados = {
        "nome": "Teste Usuario",
        "email": "teste@exemplo.com", 
        "senha": "senha123"
    }
    try:
        response = requests.post(f"{BASE_URL}/registro", json=dados)
        print(f"Status: {response.status_code}")
        print(f"Resposta: {response.json()}")
        return response.status_code in [201, 409]  # 201 criado ou 409 já existe
    except Exception as e:
        print(f"Erro: {e}")
        return False

def test_login():
    """Testar endpoint de login"""
    print("\n🔍 Testando endpoint /login...")
    dados = {
        "email": "teste@exemplo.com",
        "senha": "senha123"
    }
    try:
        response = requests.post(f"{BASE_URL}/login", json=dados)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Resposta: {result}")
        if response.status_code == 200:
            return result.get('token')
        return None
    except Exception as e:
        print(f"Erro: {e}")
        return None

def test_tarefas(token):
    """Testar endpoints de tarefas"""
    print("\n🔍 Testando endpoint GET /tarefas...")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(f"{BASE_URL}/tarefas", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Resposta: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Erro: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando testes da API...")
    
    # Teste 1: Health Check
    if not test_health():
        print("❌ Falha no teste de health check")
        exit(1)
    
    # Teste 2: Registro  
    if not test_registro():
        print("❌ Falha no teste de registro")
        exit(1)
    
    # Teste 3: Login
    token = test_login()
    if not token:
        print("❌ Falha no teste de login")
        exit(1)
    
    # Teste 4: Tarefas
    if not test_tarefas(token):
        print("❌ Falha no teste de tarefas")
        exit(1)
    
    print("\n✅ Todos os testes passaram! API funcionando corretamente.")