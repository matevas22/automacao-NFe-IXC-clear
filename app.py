from flask import Flask, render_template, request, send_file, make_response
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import requests
import json
import pandas as pd
import concurrent.futures
import io
import os
import pdfplumber
import re

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chave-super-secreta-padrao-troque-em-producao')

csp = {
    'default-src': ["'self'"],
    'frame-src': ["'self'", "https://docs.google.com"],
    'style-src': ["'self'", "https://fonts.googleapis.com", "'unsafe-inline'"],
    'font-src': ["'self'", "https://fonts.gstatic.com"],
    'img-src': ["'self'", "data:", "https://wiki.internetflex.com"], 
}

talisman = Talisman(app, content_security_policy=csp, force_https=False) 
limiter = Limiter(get_remote_address, app=app, default_limits=["2000 per day", "100 per hour"], storage_uri="memory://")
csrf = CSRFProtect(app)

@app.errorhandler(429)
def ratelimit_handler(e):
    return render_template("index.html", error="Você excedeu o limite de requisições. Por favor, aguarde um pouco e tente novamente (Limite: 100/hora ou 2000/dia)."), 429



CONFIGS = {
    "netflex": {
        "url": "https://ixc.netflexisp.com.br/webservice/v1",
        "headers": {
            'ixcsoft': 'listar',
            'Content-Type': 'application/json',
            'Authorization': os.environ.get('NETFLEX_AUTH'),
            'Cookie': os.environ.get('NETFLEX_COOKIE')
        },
        "filter_type": "ids",
        "name": "Netflex"
    },
    "fiberflex": {
        "url": "https://ixc.netflexisp.com.br/webservice/v1",
        "headers": {
            'ixcsoft': 'listar',
            'Content-Type': 'application/json',
            'Authorization': os.environ.get('FIBERFLEX_AUTH'),
            'Cookie': os.environ.get('FIBERFLEX_COOKIE')
        },
        "filter_type": "ids",
        "name": "Fiberflex"
    },
    "atuamax": {
        "url": "https://ixc.atuamax.com.br/webservice/v1",
        "headers": {
            'ixcsoft': 'listar',
            'Content-Type': 'application/json',
            'Authorization': os.environ.get('ATUAMAX_AUTH'),
            'Cookie': os.environ.get('ATUAMAX_COOKIE')
        },
        "filter_type": "keywords",
        "name": "Atuamax"
    }
}

IDS_PRODUTOS_PERMITIDOS = [
    '1702', '995', '994', '993', '992', '991', '990', '989', '988', '987', '986', '985', '984', '983', '982', '981', '980', 
    '948', '946', '922', '840', '842',  '834', '826', '819', '772', '766', '756', '749', '747', '741', '740', '739', '738', '734', 
    '733', '732', '731', '730', '725', '722', '721', '704', '695', '693', '692', '672', '671', '668', '667', '666', '665', '664', 
    '663', '662', '661', '660', '202', '201', '200', '199', '198', '197', '195', '194', '193', '192', '191', '190', '189', '188', 
    '187', '186', '185', '184', '183', '182', '181', '178', '177', '176', '175', '174', '173', '172', '171', '170', '169', '168', 
    '167', '166', '165', '164', '163', '162', '161', '160', '159', '158', '157', '156', '155', '154', '152', '151', '150', '149', 
    '148', '147', '146', '144', '143', '142', '141', '140', '139', '138', '137', '136', '135', '134', '133', '132', '131', '130', 
    '129', '128', '127', '126', '125', '124', '123', '122', '121', '119', '118', '117', '116', '115', '114', '113', '112', '111', 
    '110', '109', '108', '107', '106', '105', '104', '103', '102', '101', '100', '99', '98', '97', '96', '91', '90', '89', '88', 
    '58', '57', '56', '55', '54', '53', '52', '50', '49', '48', '46', '45', '44', '43', '42', '41', '40', '39', '37', '34', '31', 
    '30', '29', '28'
]

cache_clientes = {}

def buscar_venda_por_id(id_venda, session, url_base):
    url = f"{url_base}/vd_saida"
    payload = json.dumps({
        "qtype": "vd_saida.id",
        "query": str(id_venda),
        "oper": "=",
        "page": "1",
        "rp": "1"
    })
    
    try:
        response = session.get(url, data=payload, timeout=5)
        if response.status_code == 200:
            data = response.json()
            registros = data.get('registros', [])
            if registros:
                return registros[0]
    except Exception as e:
        print(f"Erro ao buscar detalhes da venda {id_venda}: {e}")
    
    return None

def buscar_cliente(id_cliente, session, url_base, provider_key):
    cache_key = (provider_key, id_cliente)
    if cache_key in cache_clientes:
        return cache_clientes[cache_key]
        
    url = f"{url_base}/cliente"
    payload = json.dumps({
        "qtype": "cliente.id",
        "query": id_cliente,
        "oper": "=",
        "page": "1",
        "rp": "1"
    })
    
    try:
        response = session.get(url, data=payload, timeout=5)
        if response.status_code == 200:
            data = response.json()
            registros = data.get('registros', [])
            if registros:
                cliente = registros[0]
                nome = cliente.get('razao', 'Nome não encontrado')
                cache_clientes[cache_key] = nome
                return nome
    except:
        pass
        
    return "Erro ao buscar nome"

def buscar_produtos_venda(id_venda, session, url_base, filter_type):
    url = f"{url_base}/vd_saida_produtos"
    payload = json.dumps({
        "qtype": "movimento_produtos.id_saida",
        "query": str(id_venda),
        "oper": "=",
        "page": "1",
        "rp": "100" 
    })
    
    produtos_filtrados = []
    try:
        response = session.get(url, data=payload, timeout=5)
        if response.status_code == 200:
            data = response.json()
            registros = data.get('registros', [])
            
            for reg in registros:
                id_produto = str(reg.get('id_produto') or reg.get('produto', ''))
                nome_prod = reg.get('descricao') or reg.get('descrisao') or "Sem Nome"
                valor = reg.get('valor_total', '0.00')
                
                if filter_type == "ids":
                    if id_produto in IDS_PRODUTOS_PERMITIDOS:
                        produtos_filtrados.append({'nome': nome_prod, 'valor': valor, 'id_produto': id_produto})
                elif filter_type == "keywords":
                    nome_upper = nome_prod.upper()
                    keywords = ["RESIDENCIAL", "FIBRA", "MEGA"]
                    if any(k in nome_upper for k in keywords):
                        produtos_filtrados.append({'nome': nome_prod, 'valor': valor, 'id_produto': id_produto})
                    
    except Exception as e:
        print(f"Erro prod venda {id_venda}: {e}")
        
    return produtos_filtrados

def processar_id_venda(id_venda, provider_key):
    config = CONFIGS.get(provider_key)
    if not config:
        return None

    session = requests.Session()
    session.headers.update(config["headers"])
    url_base = config["url"]
    filter_type = config["filter_type"]

    id_venda = str(id_venda).strip()
    if not id_venda:
        return None

    produtos = buscar_produtos_venda(id_venda, session, url_base, filter_type)
    
    if not produtos:
        return None
        
    dados_venda = buscar_venda_por_id(id_venda, session, url_base)
    if not dados_venda:
        return None
        
    id_cliente = dados_venda.get('id_cliente')
    nome_cliente = buscar_cliente(id_cliente, session, url_base, provider_key)
    
    nomes_str = " | ".join([p['nome'] for p in produtos])
    
    soma_valores = 0.0
    for p in produtos:
        try:
            val = float(p['valor'])
            if val > 0:
                soma_valores += val
        except:
            pass
    valores_float = soma_valores

    try:
        valor_cheio_float = float(dados_venda.get('valor_total', '0'))
    except:
        valor_cheio_float = 0.0
    
    ids_prods_str = " | ".join([p['id_produto'] for p in produtos])
    
    return {
        "ID Venda": id_venda,
        "Data Emissão": dados_venda.get('data_emissao'),
        "Data Saída": dados_venda.get('data_saida'),
        "ID Cliente": id_cliente,
        "Nome Cliente": nome_cliente,
        "Valor Total (Cheio)": valor_cheio_float,
        "Produtos": nomes_str,
        "Valor Item": valores_float,
        "IDs Produtos": ids_prods_str
    }

@app.route("/wiki")
def wiki():
    return render_template("wiki.html")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        ids_texto = request.form.get("ids_notas")
        provider = request.form.get("provider", "").strip()
        
        if not provider or provider not in CONFIGS:
            return render_template("index.html", error="Provedor inválido.")

        config = CONFIGS[provider]
        
        ids_para_processar = [line.strip() for line in ids_texto.splitlines() if line.strip()]
        
        if not ids_para_processar:
            return render_template("index.html", error="Nenhum ID informado.")

        dados_finais = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
            future_to_id = {executor.submit(processar_id_venda, id_venda, provider): id_venda for id_venda in ids_para_processar}
            
            for future in concurrent.futures.as_completed(future_to_id):
                try:
                    res = future.result()
                    if res:
                        dados_finais.append(res)
                except Exception:
                    pass

        if not dados_finais:
            return render_template("index.html", error=f"Nenhuma venda encontrada para {config['name']} com os critérios.")

        df = pd.DataFrame(dados_finais)
        try:
            df['ID Venda'] = df['ID Venda'].astype(int)
            df = df.sort_values(by='ID Venda')
        except:
            pass 
        
        num_linhas = len(df)
        linha_total = {
            "ID Venda": "TOTAL",
            "Data Emissão": "",
            "Data Saída": "",
            "ID Cliente": "",
            "Nome Cliente": "",
            "Valor Total (Cheio)": f"=SUM(F2:F{num_linhas + 1})",
            "Produtos": "",
            "Valor Item": f"=SUM(H2:H{num_linhas + 1})",
            "IDs Produtos": ""
        }
        df = pd.concat([df, pd.DataFrame([linha_total])], ignore_index=True)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Relatorio')
            workbook  = writer.book
            worksheet = writer.sheets['Relatorio']
            
            contabil_format = workbook.add_format({'num_format': '_-R$ * #,##0.00_-;-R$ * #,##0.00_-;_-R$ * "-"??_-;_-@_-'})
            border_format = workbook.add_format({'border': 1})
            
            worksheet.set_column('F:F', 20, contabil_format) 
            worksheet.set_column('H:H', 20, contabil_format)
            
            worksheet.set_column('A:A', 12) 
            worksheet.set_column('B:C', 12) 
            worksheet.set_column('D:D', 10) 
            worksheet.set_column('E:E', 40) 
            worksheet.set_column('G:G', 50) 
            worksheet.set_column('I:I', 15) 

            max_row = len(df) 
            max_col = len(df.columns) - 1
            worksheet.conditional_format(0, 0, max_row, max_col, 
                                        {'type': 'formula', 'criteria': 'True', 'format': border_format})

        output.seek(0)
        
        filename = f"relatorio_notas_{config['name']}.xlsx"
        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    return render_template("index.html")

@app.route('/converter')
def converter():
    return render_template('converter.html')

@app.route('/convert_pdf', methods=['POST'])
def convert_pdf():
    if 'pdf_file' not in request.files:
        return "Nenhum arquivo enviado", 400
    file = request.files['pdf_file']
    if file.filename == '':
        return "Nenhum arquivo selecionado", 400
    
    conversion_mode = request.form.get('conversion_mode', 'all')
    pages_input = request.form.get('pages', '')

    if file and file.filename.lower().endswith('.pdf'):
        try:
            output = io.BytesIO()
            with pdfplumber.open(file) as pdf:
                
                target_pages_indices = []
                total_pages = len(pdf.pages)
                
                if conversion_mode == 'all':
                    target_pages_indices = list(range(total_pages))
                else:
                    try:
                        parts = pages_input.split(',')
                        for part in parts:
                            part = part.strip()
                            if not part: continue
                            if '-' in part:
                                start, end = map(int, part.split('-'))
                                target_pages_indices.extend(range(start-1, end))
                            elif part.isdigit():
                                target_pages_indices.append(int(part)-1)
                        
                        target_pages_indices = sorted(list(set(target_pages_indices)))
                        target_pages_indices = [p for p in target_pages_indices if 0 <= p < total_pages]
                        
                    except Exception:
                        return "Formato de páginas inválido. Use formato: 1,3,5-7", 400
                
                if not target_pages_indices and conversion_mode == 'single':
                     return "Nenhuma página válida selecionada.", 400

                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    row_offset = 0
                    has_data = False
                    
                    found_tables = False
                    
                    for i in target_pages_indices:
                        page = pdf.pages[i]
                        
                        tables = page.extract_tables()
                        
                        if not tables:
                            tables = page.extract_tables({
                                "vertical_strategy": "text", 
                                "horizontal_strategy": "text",
                                "snap_tolerance": 3,
                            })

                        if tables:
                            for table in tables:
                                if table:
                                    clean_table = [[col if col else "" for col in row] for row in table]
                                    clean_table = [row for row in clean_table if any(cell.strip() for cell in row)]
                                    
                                    if clean_table:
                                        found_tables = True
                                        df = pd.DataFrame(clean_table)
                                        df.to_excel(writer, sheet_name='Dados Extraidos', startrow=row_offset, index=False, header=False)
                                        row_offset += len(df) + 2
                    
                    if not found_tables:
                        row_offset = 0
                        for i in target_pages_indices:
                            page = pdf.pages[i]
                            text = page.extract_text()
                            if text:
                                lines = text.split('\n')
                                parsed_data = []
                                for line in lines:
                                    if line.strip():
                                        cols = re.split(r'\s{2,}', line.strip())
                                        if len(cols) > 1:
                                            parsed_data.append(cols)
                                        else:
                                            parsed_data.append([line.strip()])
                                
                                if parsed_data:
                                    df = pd.DataFrame(parsed_data)
                                    df.to_excel(writer, sheet_name='Texto Extraidos', startrow=row_offset, index=False, header=False)
                                    row_offset += len(df) + 2
                                    has_data = True
                    else:
                        has_data = True

            if not has_data:
                return "Não foi possível encontrar dados no PDF nas páginas selecionadas.", 400

            output.seek(0)
            
            safe_filename = secure_filename(file.filename)
            base_name = os.path.splitext(safe_filename)[0]
            if not base_name:
                 base_name = "relatorio_convertido"

            return send_file(
                output,
                as_attachment=True,
                download_name=f"{base_name}.xlsx",
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        except Exception as e:
            return f"Erro ao processar arquivo: {str(e)}", 500
            
    return "Tipo de arquivo inválido. Por favor envie um PDF.", 400

if __name__ == "__main__":
    app.run(debug=True)
