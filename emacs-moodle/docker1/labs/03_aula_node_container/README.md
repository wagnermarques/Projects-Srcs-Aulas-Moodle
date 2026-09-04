# 🟢 Aula 3: Container Node.js & Variáveis de Ambiente

Nesta terceira aula prática, rodamos um servidor HTTP nativo em **Node.js 20 (Alpine)**, explorando **Variáveis de Ambiente (`environment`)**, **Diretório de Trabalho (`working_dir`)** e **Execução de Comandos (`command`)**.

---

## 🚀 Como Executar

1. Certifique-se de estar nesta pasta (ou no branch `_3_aula_node_container`):
   ```bash
   cd 03_aula_node_container
   ```

2. Inicie o container em segundo plano:
   ```bash
   docker compose up -d
   ```

3. Abra o navegador no endereço:
   👉 **http://localhost:8080**

---

## 🔍 Conceitos Trabalhados

### 1. Injeção de Variáveis de Ambiente (`environment`)
* As variáveis definidas no `docker-compose.yml` são injetadas em tempo de execução e acessadas no Node via `process.env.SAUDACAO`, `process.env.PORT`, etc.
* **Boa prática do 12-Factor App:** Configurações que variam entre ambientes (dev, homologação, prod) são passadas via variáveis, mantendo o código imutável.

### 2. Definindo o Comando de Entrada (`command: node server.js`)
* O comando inicial padrão da imagem `node:alpine` é o REPL interativo. Nós sobrescrevemos para iniciar nosso servidor `node server.js` automaticamente.

---

## 🛑 Como Finalizar o Laboratório

Para parar e remover o container:
```bash
docker compose down
```
