# 📦 Guia Completo: Geração e Importação de Pacotes SCORM no Moodle

Este tutorial explica em detalhes como empacotar artefatos pedagógicos (lições HTML, exercícios e cursos completos) no padrão **SCORM 1.2 / 2004** e importá-los no **Moodle**.

---

## 📑 Índice
1. [O que é SCORM e Como Funciona?](#1-o-que-é-scorm-e-como-funciona)
2. [Estrutura Interna de um Pacote SCORM](#2-estrutura-interna-de-um-pacote-scorm)
3. [Estratégias de Empacotamento](#3-estratégias-de-empacotamento)
   - [Estratégia A: Artefato Específico (Single-SCO)](#estratégia-a-artefato-específico-single-sco)
   - [Estratégia B: Curso Completo com Múltiplos Módulos (Multi-SCO)](#estratégia-b-curso-completo-com-múltiplos-módulos-multi-sco)
4. [Como Gerar Pacotes SCORM no Projeto (CLI)](#4-como-gerar-pacotes-scorm-no-projeto-cli)
5. [Passo a Passo: Importando no Moodle](#5-passo-a-passo-importando-no-moodle)
6. [Boas Práticas e Resolução de Problemas](#6-boas-práticas-e-resolução-de-problemas)

---

## 1. O que é SCORM e Como Funciona?

**SCORM** (*Sharable Content Object Reference Model*) é o padrão internacional da indústria para objetos de aprendizagem interoperáveis.

### Principais Vantagens:
- **Portabilidade Universal:** O mesmo arquivo `.zip` funciona no Moodle, Canvas, Blackboard, Totara, etc.
- **Rastreamento de Progresso:** O SCORM comunica automaticamente com o LMS:
  - Status de conclusão (`completed`, `incomplete`, `passed`, `failed`).
  - Nota da atividade (`cmi.core.score.raw` enviada direto para o Livro de Notas do Moodle).
  - Tempo total dedicado pelo aluno.
- **Execução Confinada:** O conteúdo roda em um player integrado com barra de navegação.

---

## 2. Estrutura Interna de um Pacote SCORM

Um arquivo SCORM é um arquivo comprimido `.zip` contendo obrigatoriamente:

```text
pacote_scorm.zip
├── imsmanifest.xml          # [OBRIGATÓRIO] Manifesto XML com metadados e índice
├── index.html               # Página de entrada do conteúdo
├── scorm_api.js             # Script de comunicação com o Moodle API Adapter
├── css/ (opcional)          # Folhas de estilo
└── js/ (opcional)           # Scripts interativos
```

### O Arquivo `imsmanifest.xml`
O manifesto é o "cérebro" do SCORM. Ele define:
1. `<metadata>`: Versão do padrão (ex: `ADL SCORM 1.2`).
2. `<organizations>`: A hierarquia do curso (títulos de seções, capítulos e tópicos).
3. `<resources>`: A lista de arquivos HTML/mídia e o tipo de objeto (`sco` ou `asset`).

---

## 3. Estratégias de Empacotamento

### Estratégia A: Artefato Específico (Single-SCO)
* **Caso de Uso:** Uma lição interativa individual (ex: *Tutorial de Docker* ou um simulador).
* **Como o Moodle exibe:** Uma única atividade no tópico do curso.
* **Comunicação:** Ao terminar a leitura ou exercício, o JavaScript envia `cmi.core.lesson_status = "completed"`.

### Estratégia B: Curso Completo com Múltiplos Módulos (Multi-SCO)
* **Caso de Uso:** Todas as aulas e questionários do curso empacotados em um único arquivo `.zip`.
* **Como o Moodle exibe:** O player do Moodle abre uma barra lateral com **Sumário (Table of Contents)** contendo todos os capítulos e lições.
* **Vantagem:** Um único upload no Moodle disponibiliza toda a trilha pedagógica com rastreamento integrado.

---

## 4. Como Gerar Pacotes SCORM no Projeto (CLI)

Disponibilizamos o script automatizado **`scripts/build_scorm.py`**.

Por padrão, ao passar o caminho de uma **pasta de curso** (como `docker1`), o script:
1. Localiza a aula principal (`index.org` / `index.html`).
2. Varre todos os questionários `.org` da pasta (`quiz1_fundamentos.org`, `quiz2_dockerfile_compose.org`...) e os converte automaticamente em **páginas interativas de quiz** com correção imediata e envio automático de nota (`cmi.core.score.raw`) para o Livro de Notas do Moodle.
3. Constrói o manifesto **Multi-SCO** (`imsmanifest.xml`) com a árvore de navegação completa.
4. Compacta o arquivo `.zip` final pronto para upload.

### Comando para Gerar o Pacote Completo (Lição + Todos os Quizzes):
```bash
python3 scripts/build_scorm.py docker1 \
  -o dist/scorm/docker1_completo.zip \
  -t "Curso Completo: Docker & Containers"
```

Ou através do Makefile:
```bash
make scorm
```

O arquivo gerado em `dist/scorm/docker1_completo.zip` conterá todos os módulos:
- 📖 **1. Tutorial de Docker e Containers**
- 📝 **2. Quiz 1: Docker Fundamentos e CLI**
- 📝 **3. Quiz 2: Dockerfile, Armazenamento e Compose**

---

## 5. Passo a Passo: Importando no Moodle

Siga o roteiro abaixo para publicar seu pacote SCORM no Moodle (ex: no curso `https://fzlbpms.com.br/moodle/course/view.php?id=2`):

### Passo 1: Acessar o Curso e Ativar Edição
1. Faça login como **Professor** ou **Administrador** no Moodle.
2. Acesse seu curso.
3. No canto superior direito, clique no botão **"Ativar modo de edição"** (ou no ícone de engrenagem > *Ativar edição*).

### Passo 2: Adicionar a Atividade SCORM
1. Na seção/tópico desejado, clique em **"+ Adicionar uma atividade ou recurso"**.
2. Na lista de atividades, selecione **Pacote SCORM (SCORM package)**.

### Passo 3: Configurar os Parâmetros da Atividade
Preencha os campos principais:
* **Geral:**
  * **Nome:** Ex: `Tutorial Interativo: Docker e Containers`
  * **Descrição:** Breve resumo dos objetivos da aula.
* **Pacote:**
  * No campo **Arquivo de pacote**, arraste e solte o arquivo `.zip` (ex: `dist/scorm/docker1_tutorial.zip`) ou clique em *Escolher um arquivo*.
* **Aparência:**
  * **Janela de exibição:** *Janela atual* (dentro do tema do Moodle) ou *Nova janela* (pop-up limpo).
  * **Exibir estrutura do curso na página de entrada:** *Sim* (recomendado para pacotes Multi-SCO).
* **Avaliação (Grade):**
  * **Método de avaliação:** Escolha entre *Situação dos SCOs* (conclusão), *Maior nota*, ou *Média das tentativas*.
  * **Nota máxima:** Ex: `10,00` ou `100,00`.

### Passo 4: Salvar e Testar
1. Clique em **"Salvar e mostrar"**.
2. Clique no botão **"Entrar"** para testar a navegação e verificar o carregamento do conteúdo no player do Moodle.

---

## 6. Boas Práticas e Resolução de Problemas

1. **Manifesto na Raiz:** O arquivo `imsmanifest.xml` deve estar na **raiz** do arquivo `.zip`, e não dentro de uma subpasta compactada.
2. **Caminhos Relativos:** Todas as referências a CSS, JS e imagens dentro do HTML devem ser relativas (ex: `src="imagens/foto.png"` e nunca `/home/usuario/...` ou caminhos absolutos locais).
3. **Bloqueadores de Pop-up:** Se optar por exibir o SCORM em "Nova Janela", oriente os alunos a permitirem pop-ups no navegador para o domínio do Moodle.
4. **HTTPS:** Certifique-se de que todos os scripts e mídias externas incluídas usem `https://` para evitar bloqueios de conteúdo misto (*mixed content*) nos navegadores modernos.
