from flask import request, jsonify
from flask_login import current_user
from ext.configuration import URL, URL_OS, HEADERS
from bs4 import BeautifulSoup
import requests


def send_form():
    try:
        message = 'Dados enviados com sucesso!'

        cidades = {
            'GUARATINGUETA': '512921',
            'LAGOINHA': '516706',
            'PINDAMONHANGABA': '512927',
            'SILVEIRAS': '512915'
        }

        prioridades = {
            'BAIXA': '0',
            'MEDIA': '1',
            'ALTA': '2',
            'URGENTE': '3',
            'MUITO URGENTE': '4'
        }

        fornecedor = request.form.get("fornecedor")
        motorista = request.form.get("motorista")

        fornecedor_string = f"FORNECEDOR: {fornecedor}" if fornecedor else ""
        motorista_string = f"MOTORISTA: {motorista}" if motorista else ""
        prioridade = request.form.get("prioridade")

        collected_data = {
            "cliente_id": "39134045",
            "nome_vendedor": current_user.username.upper(),
            "data_entrada": request.form.get("data"),
            "horario": request.form.get("hora"),
            "prioridade": prioridades[prioridade],
            "situacao_id": "6909262",
            "centro_custo_id": cidades[request.form.get("cidade")],
            "observacoes": f"{fornecedor_string}\n{motorista_string}",
            "equipamentos": [
                {
                    "equipamento": {
                        "equipamento": request.form.get("placa"),
                        "serie": request.form.get("quilometragem"),
                        "defeitos": request.form.get("defeito"),
                        "solucao": request.form.get("solucao")
                    }
                }
            ]
        }

        # Envia os dados para a API e recebe o código da OS
        response = requests.post(URL, json=collected_data, headers=HEADERS)
        if response.status_code == 200:
            returned_data = response.json()
            os_code = returned_data.get("data").get("codigo")
            os_hash = requests.get(URL + "?codigo=" + os_code, headers=HEADERS).json()
            html_link = URL_OS + os_hash.get("data", [])[0].get("hash")

            # Obtém o conteúdo HTML
            html_response = requests.get(html_link)
            if html_response.status_code == 200:
                html_content = html_response.text

                soup = BeautifulSoup(html_content, 'html.parser')

                elementos_para_remover = [
                    'dados-pagamento',
                    None if fornecedor_string else 'dados-cliente',
                    'valor-total',
                ]

                for classe in elementos_para_remover:
                    for elemento in soup.find_all('div', class_=classe):
                        elemento.decompose()

                numero_pedido = soup.find('h2', class_='numero-pedido')
                if numero_pedido:
                    texto_existente = numero_pedido.get_text(strip=True)
                    texto_adicional = f" - {prioridade}"
                    numero_pedido.string = f"{texto_existente}{texto_adicional}"

                    # **Adicionar uma tabela em branco na segunda página**
                    # Criação de um separador de página
                    separador_pagina = soup.new_tag('div', **{'class': 'page-break'})
                    soup.body.append(separador_pagina)

                    # Criação da tabela em branco
                    tabela = soup.new_tag('table', **{'class': 'tabela-servicos'})

                    # Cabeçalho da tabela
                    thead = soup.new_tag('thead')
                    tr_head = soup.new_tag('tr')

                    colunas = ["SERVIÇO EXECUTADO", "HORA INICIAL", "HORA FINAL"]
                    for coluna in colunas:
                        th = soup.new_tag('th')
                        th.string = coluna
                        tr_head.append(th)
                    thead.append(tr_head)
                    tabela.append(thead)

                    # Corpo da tabela (em branco para preenchimento manual)
                    tbody = soup.new_tag('tbody')

                    # Definir o número de linhas para preencher a página
                    # Ajuste este número conforme necessário para preencher a página A4
                    numero_linhas = 30  # Exemplo: 30 linhas

                    for _ in range(numero_linhas):
                        tr = soup.new_tag('tr')
                        for _ in colunas:
                            td = soup.new_tag('td')
                            tr.append(td)
                        tbody.append(tr)

                    tabela.append(tbody)
                    soup.body.append(tabela)

                    # **Adicionar CSS para formatar a tabela e a quebra de página**
                    estilo = soup.new_tag('style')
                    estilo.string = """
                                @media print {
                                    .page-break {
                                        page-break-before: always;
                                    }
                                }
                                .tabela-servicos {
                                    width: 100%;
                                    border-collapse: collapse;
                                    margin-top: 20px;
                                }
                                .tabela-servicos th, .tabela-servicos td {
                                    border: 1px solid #000;
                                    padding: 16px;
                                    text-align: left;
                                }
                                .tabela-servicos th {
                                    background-color: #f2f2f2;
                                }
                                html, body {
                                    width: 210mm;
                                    height: 297mm;
                                    margin: 0;
                                    padding: 0;
                                    font-family: Arial, sans-serif;
                                    font-size: 12pt;
                                }
                                @page {
                                    size: A4;
                                    margin: 20mm;
                                }
                                /* Garantir que a tabela ocupe toda a altura da página */
                                body {
                                    display: flex;
                                    flex-direction: column;
                                    height: 100vh;
                                }
                                .tabela-servicos {
                                    flex-grow: 1;
                                }
                                """

                    # Inserir o estilo no head
                    if soup.head:
                        soup.head.append(estilo)
                    else:
                        head = soup.new_tag('head')
                        head.append(estilo)
                        soup.insert(0, head)

                    # Obter o HTML modificado como string
                    html_modificado = str(soup)

                return jsonify({
                    'type': 'success',
                    'message': 'Dados enviados com sucesso!',
                    'html': html_modificado
                })
            else:
                return jsonify({'type': 'error', 'message': 'Erro ao obter o HTML da OS.'})
        else:
            return jsonify({'type': 'error', 'message': f'Erro da API: {response.status_code}'})

    except Exception as e:
        return jsonify({'type': 'error', 'message': f'Erro na função: {str(e)}'})
