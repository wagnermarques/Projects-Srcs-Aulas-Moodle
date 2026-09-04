# 🐳 Aula 1: Criação do Container Nginx & Bind Mount

Nesta primeira aula prática, vamos subir um servidor web **Nginx** utilizando o **Docker Compose** e entender dois conceitos cruciais: **Mapeamento de Portas** e **Bind Mount de Volumes**.

---

## 🚀 Como Executar

1. Certifique-se de estar nesta pasta (ou no branch `_1_aula_nginx_container_creation`):
   ```bash
   cd 01_aula_nginx_container_creation
   ```

2. Inicie o container em segundo plano:
   ```bash
   docker compose up -d
   ```

3. Abra o navegador no endereço:
   👉 **http://localhost:8080**

---

## 🔍 Conceitos Trabalhados

### 1. Mapeamento de Portas (`ports: - "8080:80"`)
* **Host (seu computador):** Porta `8080`.
* **Container (Nginx):** Porta `80`.
* O Docker cria uma ponte de rede redirecionando automaticamente o tráfego recebido em `localhost:8080` para a porta `80` interna do Nginx.

### 2. Bind Mount de Volume (`volumes: - ./html:/usr/share/nginx/html:ro`)
* O diretório local `./html` é espelhado no caminho `/usr/share/nginx/html` do container.
* **Vantagem:** Qualquer edição no arquivo `html/index.html` na sua máquina reflete **instantaneamente** no navegador ao recarregar a página (<kbd>F5</kbd>), sem necessidade de reiniciar o container.

---

## 🛑 Como Finalizar o Laboratório

Para parar e remover o container:
```bash
docker compose down
```
