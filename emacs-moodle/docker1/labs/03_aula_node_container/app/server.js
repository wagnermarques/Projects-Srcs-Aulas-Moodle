const http = require('http');
const os = require('os');

const PORT = process.env.PORT || 3000;
const SAUDACAO = process.env.SAUDACAO || 'Olá do Node.js!';
const APP_NAME = process.env.APP_NAME || 'Node.js App';
const NODE_ENV = process.env.NODE_ENV || 'production';

const server = http.createServer((req, res) => {
  res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
  res.end(`<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Aula 3 - Docker Node.js Container</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      line-height: 1.6;
      color: #2c3e50;
      background: #f8fafc;
      margin: 0;
      padding: 40px 20px;
    }
    .container {
      max-width: 780px;
      margin: 0 auto;
      background: #ffffff;
      padding: 30px;
      border-radius: 12px;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    h1 {
      color: #16a34a;
      margin-top: 0;
      border-bottom: 2px solid #dcfce7;
      padding-bottom: 12px;
    }
    .badge {
      display: inline-block;
      padding: 4px 12px;
      border-radius: 20px;
      background-color: #16a34a;
      color: white;
      font-size: 0.85rem;
      font-weight: 600;
      margin-bottom: 15px;
    }
    .card {
      background: #f0fdf4;
      border-left: 4px solid #16a34a;
      padding: 16px 20px;
      border-radius: 6px;
      margin: 20px 0;
    }
    .info-table {
      width: 100%;
      border-collapse: collapse;
      margin: 15px 0;
    }
    .info-table th, .info-table td {
      border: 1px solid #e2e8f0;
      padding: 10px 14px;
      text-align: left;
    }
    .info-table th {
      background: #f1f5f9;
      font-weight: 600;
    }
    code {
      background: #e2e8f0;
      padding: 2px 6px;
      border-radius: 4px;
      font-family: Consolas, Monaco, "Courier New", monospace;
    }
  </style>
</head>
<body>
  <div class="container">
    <span class="badge">Passo 3 / 3</span>
    <h1>🟢 Aula 3: Node.js Container & Environment</h1>
    <p>O container <strong>aula_node</strong> está rodando seu próprio servidor HTTP nativo em JavaScript!</p>

    <div class="card">
      <h3>⚡ Dados Dinâmicos do Ambiente Node.js:</h3>
      <table class="info-table">
        <tr>
          <th>Mensagem (Variável de Ambiente)</th>
          <td><strong>${SAUDACAO}</strong></td>
        </tr>
        <tr>
          <th>Nome da Aplicação</th>
          <td>${APP_NAME}</td>
        </tr>
        <tr>
          <th>Ambiente (NODE_ENV)</th>
          <td><code>${NODE_ENV}</code></td>
        </tr>
        <tr>
          <th>Versão do Node.js</th>
          <td><code>${process.version}</code></td>
        </tr>
        <tr>
          <th>Plataforma / Arquitetura</th>
          <td><code>${os.platform()} (${os.arch()})</code></td>
        </tr>
        <tr>
          <th>Hostname do Container</th>
          <td><code>${os.hostname()}</code></td>
        </tr>
        <tr>
          <th>Porta Interna / Externa</th>
          <td>Interna: <code>${PORT}</code> | Host: <code>8080</code></td>
        </tr>
      </table>
    </div>

    <div class="card">
      <h3>🔍 O que aprendemos neste passo?</h3>
      <ul>
        <li><strong>Injeção de Configurações (<code>environment</code>)</strong>: O Docker Compose injeta variáveis diretamente em <code>process.env</code> sem alterar o código.</li>
        <li><strong>Comando Personalizado (<code>command</code>)</strong>: Definimos <code>node server.js</code> como ponto de partida da aplicação.</li>
        <li><strong>Execução Rápida em Alpine Linux</strong>: Usamos <code>node:20-alpine</code> gerando um ambiente leve e isolado.</li>
      </ul>
    </div>
  </div>
</body>
</html>`);
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`[✓] Servidor Node.js rodando na porta ${PORT}`);
});
