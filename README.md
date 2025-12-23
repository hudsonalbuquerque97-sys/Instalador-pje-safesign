# Instalador SafeSign PJe

Script Python para automatizar a instalação do SafeSign Token e do PJe (Processo Judicial Eletrônico) no **Mint/Ubuntu/Debian**

## 📋 Descrição

Este projeto contém duas versões de um instalador que baixa, instala e configura o **SafeSign IC** + **PJe Office Pro** para autenticação com certificados digitais  Cada versão utiliza ícones diferente.

## 🎨 Versões Disponíveis

### Versão 1 (Instalador_safesign_pje_v1.py)

* Tema: Original

* Ícones: PJe branco + SafeSign original

* Arquivo: Instalador_safesign_pje_v1.py

### Versão 2 (Instalador_safesign_pje_v2.py)

* Tema: Black

* Ícones: Tema preto

* Arquivo: Instalador_safesign_pje_v2.py

## 🚀 Funcionalidades

Todos os instaladores incluem:

1 - Instalação automática de dependências necessárias

2 - Download e instalação do SafeSign IC

3 - Download e instalação do Pje Office Pro

4 - Criação de ícones na área de trabalho

5 - Configuração de permissões e grupos de usuário

## 🛠️ Requisitos do Sistema

* Sistema Operacional: Linux Mint 22+, Ubuntu 18.04+ ou Debian 10+

* Python: Python 3.x

* Privilégios: Acesso de superusuário (sudo)

## 📥 Instalação e Uso

1. Clone o repositório:

```bash

git clone https://github.com/hudsonalbuquerque97-sys/Instalador-safesign-pje.git
cd Instalador-safesign-pje
```

2. Execute a versão desejada:

Versão 1 (Original):

```bash
sudo python3 ./Instalador_safesign_pje_v1.py
```
Versão 2 (Black):

```bash
sudo python3 ./python3 Instalador_safesign_pje_v2.py
```

## ⚙️ Funcionamento

O script realiza as seguintes etapas:

1 - Verificação de privilégios - Confirma execução como root

2 - Instalação de dependências - Bibliotecas necessárias do sistema

3 - Download do SafeSign - Baixa o pacote mais recente

4 - Instalação do SafeSign - Executa a instalação do pacote

5 - Download do Pje Office Pro - Baixa o pacote mais recente

6 - Instalação do Pje Office Pro - Executa a instalação do pacote

7 - Criação de ícones - Adiciona atalhos na área de trabalho

8 - Configuração de grupos - Adiciona usuário aos grupos necessários

## 🔧 Pós-Instalação

Após a instalação:

1 - Reinicie o computador ou faça logout/login

2 - Conecte seu token ou leitor de cartão

3 - Acesse o PJe através do ícone criado

4 - Importe seus certificados digitais

## ❓ Solução de Problemas
Erro de permissão:
bash

### Se encontrar erro de permissão

```bash
sudo chmod +x Instalador_safesign_pje_v*.py
```

### Dependências faltando:

Instalar dependências manualmente se necessário

```bash
sudo apt update
sudo apt install wget libnss3-tools unzip
```

Problemas com navegadores:

Firefox:  Certifique-se de que a extensão do SafeSign está ativa

## ⚠️ Aviso

Este é um projeto de terceiros e não possui afiliação oficial com o PJe ou SafeSign. Use por sua conta e risco. Sempre verifique a autenticidade dos downloads de segurança.

## 🔗 Links Úteis

PJe - Processo Judicial Eletrônico

SafeSign Official

Documentação SafeSign IC

Nota: Reinicie seu sistema após a instalação para que todas as configurações tenham efeito completo.w
