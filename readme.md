# Sistema de Automação de Notas e Relatórios (Excel Notas)

Este é um sistema web desenvolvido em **Python com Flask** projetado para automatizar a geração de relatórios financeiros a partir de sistemas IXC Soft e realizar a conversão e extração de dados de arquivos PDF para Excel.

O sistema visa agilizar o processo de conferência de notas fiscais, integrando-se via API com provedores (Netflex, Fiberflex, Atuamax) e fornecendo ferramentas utilitárias para manipulação de documentos.

## Funcionalidades Principais

### 1. Gerador de Relatórios Financeiros
- **Integração via API:** Conecta-se aos sistemas IXC Soft de diferentes provedores.
- **Processamento em Lote:** Aceita uma lista de IDs de Venda/Notas e processa todos simultaneamente usando *multi-threading*.
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

##  Instalação e Configuração

### Pré-requisitos
- Python 3.10 ou superior
- Pip (Gerenciador de pacotes do Python)

### Passo a Passo

1. **Clone o repositório** (ou baixe os arquivos):
   ```bash
   git clone <url-do-repositorio>
   cd flask-notas

### Obrigado ;)