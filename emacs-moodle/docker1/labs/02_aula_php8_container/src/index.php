<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Aula 2 - Docker PHP 8.3 & Redes</title>
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
      color: #7c3aed;
      margin-top: 0;
      border-bottom: 2px solid #ede9fe;
      padding-bottom: 12px;
    }
    .badge {
      display: inline-block;
      padding: 4px 12px;
      border-radius: 20px;
      background-color: #7c3aed;
      color: white;
      font-size: 0.85rem;
      font-weight: 600;
      margin-bottom: 15px;
    }
    .card {
      background: #f5f3ff;
      border-left: 4px solid #7c3aed;
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
    <span class="badge">Passo 2 / 3</span>
    <h1>🐘 Aula 2: PHP 8.3 & Docker Network</h1>
    <p>Parabéns! O Nginx e o PHP-FPM estão se comunicando perfeitamente através da rede interna do Docker (<code>aula-rede</code>).</p>

    <div class="card">
      <h3>🌐 Informações em Tempo Real do Ambiente PHP:</h3>
      <table class="info-table">
        <tr>
          <th>Versão do PHP</th>
          <td><strong><?php echo phpversion(); ?></strong></td>
        </tr>
        <tr>
          <th>Data e Hora do Servidor</th>
          <td><?php echo date('d/m/Y H:i:s'); ?></td>
        </tr>
        <tr>
          <th>Hostname do Container PHP</th>
          <td><code><?php echo gethostname(); ?></code></td>
        </tr>
        <tr>
          <th>Servidor Web (Gateway)</th>
          <td><code><?php echo $_SERVER['SERVER_SOFTWARE'] ?? 'Nginx'; ?></code></td>
        </tr>
      </table>
    </div>

    <div class="card">
      <h3>🔍 Como a Comunicação Funciona?</h3>
      <ol>
        <li>Seu navegador envia uma requisição para <code>http://localhost:8080/index.php</code>.</li>
        <li>O container <strong>aula_nginx</strong> recebe a requisição na porta 80.</li>
        <li>O Nginx identifica que é um arquivo <code>.php</code> e encaminha para <code>aula_php:9000</code> via rede interna <code>aula-rede</code>.</li>
        <li>O <strong>DNS interno do Docker</strong> resolve o nome <code>aula_php</code> diretamente para o IP do container PHP.</li>
        <li>O PHP executa o script e devolve o HTML processado para o Nginx exibir no seu navegador!</li>
      </ol>
    </div>
  </div>
</body>
</html>
