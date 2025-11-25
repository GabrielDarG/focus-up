# 🛡️ Focus Up

![Status do Projeto](https://img.shields.io/badge/status-concluído_(TCC)-brightgreen)
![Linguagem](https://img.shields.io/badge/python-3.10%2B-blue)
![Framework](https://img.shields.io/badge/django-092E20?style=for-the-badge&logo=django&logoColor=white)
![AI](https://img.shields.io/badge/AI-Ollama-orange)

> Transforme sua rotina em um RPG: complete missões, ganhe XP e evolua.

O **Focus Up** é uma plataforma de produtividade gamificada desenvolvida como Trabalho de Conclusão de Curso (TCC). Ele resolve o problema da **procrastinação** ao transformar tarefas cotidianas em missões de RPG, utilizando Inteligência Artificial (Ollama) para gerar desafios personalizados baseados nos interesses do usuário.

---

## 📖 Índice

* [Sobre a Aventura](#-sobre-a-aventura)
* [Guia do Jogador (Funcionalidades)](#-guia-do-jogador-funcionalidades)
* [Pré-requisitos](#-pré-requisitos)
* [Instalação e Configuração](#-instalação-e-configuração)
* [Como Rodar](#️-como-rodar)
* [Tecnologias Utilizadas](#-tecnologias-utilizadas)
* [Licença](#-licença)

---

## 📜 Sobre a Aventura

Diferente de listas de tarefas comuns que apenas cobram produtividade, o Focus Up recompensa o usuário instantaneamente. O sistema combina gestão de hábitos com lógica de jogos:

1.  **IA Generativa:** O sistema lê o perfil do usuário e cria missões temáticas automaticamente.
2.  **Economia Virtual:** Tarefas geram moedas para comprar itens cosméticos e funcionais.
3.  **Sistema de Slots:** Limita a quantidade de tarefas para evitar sobrecarga (burnout), focando na qualidade da execução.

---

## 🎮 Guia do Jogador (Funcionalidades)

Aqui está como o sistema funciona por dentro:

### 1. O Objetivo & Perfil
Tudo começa na página **"Perfil Focos"**. O usuário cadastra seus objetivos e interesses. Nossa Inteligência Artificial (Ollama) lê essas informações para criar o contexto do jogo.

### 2. 🤖 Missões Diárias (IA)
Todo dia, o sistema gera automaticamente **6 tarefas exclusivas (Quests Principais)** baseadas nos focos cadastrados. Elas renovam a cada 24 horas.

### 3. 📅 Tarefas Pessoais & Sistema de Slots
O usuário pode criar hábitos recorrentes (ex: "Ir à academia" toda Seg, Qua, Sex).
* **A Regra dos Slots:** O usuário tem **3 Slots Pessoais** por dia inicialmente.
* **Sorteio:** Se houver 5 tarefas agendadas para hoje, o sistema sorteará aleatoriamente apenas 3 para ocupar os slots, garantindo dinamismo.
* **Sugestão Rápida:** Se sobrarem slots vazios, a IA pode sugerir uma tarefa extra na hora.

### 4. 💰 Recompensas e Loja
Ao completar uma tarefa, o jogador recebe:
* ⭐ **XP Variável:** Para subir de nível.
* 💰 **100 Moedas:** Valor fixo por tarefa.

Na **Loja**, é possível comprar:
* **Upgrades:** Até +3 slots extras de tarefas.
* **Cosméticos:** Molduras e cores de perfil.
* **Itens Mágicos:** Como o "Congelador de Ofensiva".

---

## 📋 Pré-requisitos

Antes de começar a aventura, você precisa ter instalado em sua máquina:

* **[Git](https://git-scm.com)**
* **[Python 3.10+](https://www.python.org/downloads/)**
* **[Ollama](https://ollama.com/)** (Para a geração de tarefas via IA)

---

## 🚀 Instalação e Configuração

Siga os passos abaixo para configurar o ambiente local:

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/GabrielDarG/focus-up.git](https://github.com/GabrielDarG/focus-up.git)
    ```

2.  **Navegue até o diretório do projeto:**
    ```bash
    cd focus-up
    ```

3.  **Crie e ative um ambiente virtual:**
    * **No Windows:**
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```
    * **No macOS/Linux:**
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```

4.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Prepare o Banco de Dados:**
    ```bash
    python manage.py migrate
    ```

---

## ▶️ Como Rodar

1.  **Inicie o servidor:**
    Com o ambiente virtual ativado, execute:

    ```bash
    python manage.py runserver
    ```

2.  **Acesse o jogo:**
    Abra seu navegador e acesse:
    [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 🛠️ Tecnologias Utilizadas

Ferramentas que deram vida ao projeto:

* **Back-end:** [Python](https://www.python.org/) & [Django](https://www.djangoproject.com/)
* **Inteligência Artificial:** [Ollama](https://ollama.com/) (LLM Local)
* **Front-end:** HTML5, CSS3 (Estilização personalizada)
* **Banco de Dados:** SQLite (Padrão Django)

---

## 📝 Licença

Este projeto está sob a licença MIT. Sinta-se livre para contribuir!

Feito por:
**Gabriel Darcolette Gomes**,
**Caio Aguiar Moutinho**,
**Luan Oliveira Santana**,
**Pedro Augusto Barbaroto dos Santos**. 
