# Sistema de Automação de Notas e Relatórios (Excel Notas)

Este é um sistema web desenvolvido em **Python com Flask** projetado para automatizar a geração de relatórios financeiros a partir de sistemas IXC Soft e realizar a conversão e extração de dados de arquivos PDF para Excel.

O sistema visa agilizar o processo de conferência de notas fiscais, integrando-se via API com provedores (Netflex, Fiberflex, Atuamax) e fornecendo ferramentas utilitárias para manipulação de documentos.

## Funcionalidades Principais

### 1. Gerador de Relatórios Financeiros

- **Integração via API:** Conecta-se aos sistemas IXC Soft de diferentes provedores.
- **Processamento em Lote:** Aceita uma lista de IDs de Venda/Notas e processa todos simultaneamente usando _multi-threading_.
- **Filtros Inteligentes:**
  - Filtro por IDs de produtos específicos.
  - Filtro por palavras-chave (ex: "RESIDENCIAL", "FIBRA", "MEGA").
- **Geração de Excel:** Exporta um relatório `.xlsx` formatado contendo:
  - ID da Venda, Data de Emissão, Cliente.
  - Valores totais e discriminados.
  - Fórmulas automáticas de soma no Excel gerado.

### 2. Conversor de PDF para Excel

- **Extração de Tabelas:** Identifica e extrai tabelas de arquivos PDF automaticamente.
- **Extração de Texto:** Caso não encontre tabelas, tenta estruturar o texto solto em colunas.
- **Seleção de Páginas:** Permite converter o documento inteiro ou páginas específicas (ex: "1, 3, 5-7").

### 3. Wiki Interna

- Documentação integrada para orientar a equipe sobre os processos manuais e automáticos.
- Tutoriais visuais sobre como baixar relatórios e utilizar as planilhas auxiliares.

### 4. Interface (UI/UX)

- **Modo Escuro (Dark Mode):** Suporte nativo a tema claro e escuro.
- **Design Responsivo:** Interface moderna e amigável para uso em desktop.
- **Feedback Visual:** Indicadores de carregamento e mensagens de erro/sucesso.

---

## Tecnologias Utilizadas

- **Backend:** Python 3, Flask
- **Manipulação de Dados:** Pandas, NumPy, OpenPyXL, XlsxWriter
- **Processamento de PDF:** PDFPlumber
- **Requisições HTTP:** Requests
- **Segurança & Performance:** Flask-Talisman, Flask-Limiter, CSRFProtect
- **Frontend:** HTML5, CSS3, JavaScript

---

## Instalação e Configuração

### Pré-requisitos

- Python 3.10 ou superior
- Pip (Gerenciador de pacotes do Python)

### Passo a Passo (Rodando Localmente)

1. **Clone o repositório** (ou baixe os arquivos):

   ```bash
   git clone <url-do-repositorio>
   cd flask-notas
   ```

2. **Crie um ambiente virtual (recomendado):**

   ```bash
   python -m venv venv
   # No Windows:
   venv\Scripts\activate
   # No Linux/Mac:
   source venv/bin/activate
   ```

3. **Instale as dependências:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configuração das Variáveis de Ambiente:**
   Renomeie o arquivo `.env.example` para `.env` e preencha as chaves:

   ```env
   # Configurações de Segurança
   SECRET_KEY=sua_chave_secreta_aqui
   # Credenciais dos provedores...
   ```

5. **Executar:**
   ```bash
   python app.py
   ```
   Acesse: `http://127.0.0.1:5000`

---

## Passo a Passo (Rodando com Docker)

Se preferir não instalar o Python/dependências na sua máquina, use o Docker:

1. **Pré-requisitos:**
   - Docker e Docker Compose instalados.

2. **Configuração:**
   - Crie o arquivo `.env` na raiz do projeto conforme explicado acima.

3. **Rodar o container:**
   No terminal, dentro da pasta do projeto:

   ```bash
   docker-compose up --build
   ```

   O sistema estará disponível em: `http://127.0.0.1:5000`

   Para parar a aplicação:

   ```bash
   docker-compose down
   ```

---

## Como Usar

### Gerar Relatório de Notas

1. Na página inicial, selecione o **Provedor**.
2. Cole a lista de **IDs das Notas** na área de texto.
3. Clique em **"Processar e Baixar Excel"**.

### Converter PDF

1. Acesse a aba **"Conversor PDF"**.
2. Arraste ou selecione seu arquivo PDF.
3. Escolha as páginas e baixe a planilha convertida.

---

## Estrutura do Projeto

```
flask-notas/
├── app.py                 # Core da aplicação
├── Dockerfile             # Configuração da imagem Docker
├── docker-compose.yml     # Orquestração dos containers
├── requirements.txt       # Dependências Python
├── static/                # Assets (CSS, JS, Img)
└── templates/             # HTML (Jinja2)
```
