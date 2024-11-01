from flask import request, jsonify, send_file
from flask_login import current_user
from ext.configuration import URL, URL_PDF, HEADERS
from PyPDF2 import PdfReader, PdfWriter
import os
from io import BytesIO
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

        fornecedor = request.form.get("fornecedor")
        motorista = request.form.get("motorista")

        fornecedor_string = f"FORNECEDOR: {fornecedor}" if fornecedor else ""
        motorista_string = f"MOTORISTA: {motorista}" if motorista else ""

        collected_data = {
            "cliente_id": "39134045",
            "nome_vendedor": current_user.username.upper(),
            "data_entrada": request.form.get("data"),
            "horario": request.form.get("hora"),
            "prioridade": request.form.get("prioridade"),
            "situacao_id": "6909262",
            "centro_custo_id": cidades[request.form.get("cidade")],
            "observacoes": f"{fornecedor_string}\n{motorista_string}",
            "equipamentos": [
                {
                    "equipamento": {
                        "equipamento": request.form.get("placa"),
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
            pdf_link = URL_PDF + os_hash.get("data", [])[0].get("hash")

            # Baixa o PDF original usando o pdf_link
            original_pdf_response = requests.get(pdf_link)
            original_pdf = PdfReader(BytesIO(original_pdf_response.content))

            # Carrega uma nova página de outro PDF que você deseja adicionar
            new_page_pdf_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'static', 'verso.pdf')
            new_pdf = PdfReader(new_page_pdf_path)

            # Cria um escritor para o PDF combinado
            pdf_writer = PdfWriter()

            # Adiciona todas as páginas do PDF original
            for page in original_pdf.pages:
                pdf_writer.add_page(page)

            # Adiciona todas as páginas do novo PDF
            for page in new_pdf.pages:
                pdf_writer.add_page(page)

            # Salva o PDF combinado em um objeto BytesIO
            combined_pdf = BytesIO()
            pdf_writer.write(combined_pdf)
            combined_pdf.seek(0)

            # Retorna o PDF combinado diretamente como resposta
            return send_file(combined_pdf, download_name="combined.pdf", as_attachment=True)

        else:
            return jsonify({'type': 'error', 'message': response.status_code})

    except Exception as e:
        return jsonify({'type': 'error', 'message': 'Erro na função: ' + str(e)})
