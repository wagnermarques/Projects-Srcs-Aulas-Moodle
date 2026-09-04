# 🐘 Aula 2: PHP 8.3 & Docker Network (Multi-Container)

Nesta aula, evoluímos nossa arquitetura para uma aplicação **Multi-Container**, integrando o **Nginx** (Web Server) com o **PHP 8.3 FPM** (Application Server) através de uma **Docker Network**.

---

## 🚀 Como Executar

1. Certifique-se de estar nesta pasta (ou no branch `_2_aula_php8_container`):
   ```bash
   cd 02_aula_php8_container
   ```

2. Inicie a stack de containers:
   ```bash
   docker compose up -d
   ```

3. Abra o navegador no endereço:
   👉 **http://localhost:8080**

---

## 🔍 Conceitos Trabalhados

### 1. Redes Internas do Docker (`networks: aula-rede`)
* Ao criar uma rede customizada do tipo `bridge`, o Docker ativa o **serviço de DNS interno**.
* O Nginx consegue se comunicar com o PHP chamando diretamente o nome do serviço (`aula_php:9000`), sem necessidade de configurar ou descobrir endereços IP manualmente.

### 2. Separação de Responsabilidades
* **`aula_nginx`:** Atua como ponto de entrada (porta 8080 no host), entrega arquivos estáticos e repassa scripts dinâmicos.
* **`aula_php`:** Container dedicado exclusivamente ao processamento do runtime PHP-FPM, isolado da rede pública externa.

---

## 🛑 Como Finalizar o Laboratório

Para parar e remover todos os containers e a rede criada:
```bash
docker compose down
```
