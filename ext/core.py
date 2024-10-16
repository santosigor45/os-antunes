from flask import request, jsonify
from flask_login import current_user
from ext.configuration import URL, URL_PDF, HEADERS
import requests


def send_form():
    try:
        message = 'Dados enviados com sucesso!'
        collected_data = {
            "cliente_id": "39134045",
            "nome_vendedor": current_user.username.upper(),
            "data_entrada": request.form.get("data"),
            "situacao_id": "6909262",
            "observacoes": request.form.get("destino"),
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

        response = requests.post(URL, json=collected_data, headers=HEADERS)
        if response.status_code == 200:
            returned_data = response.json()
            os_code = returned_data.get("data").get("codigo")
            os_hash = requests.get(URL + "?codigo=" + os_code, headers=HEADERS).json()
            pdf_link = URL_PDF + os_hash.get("data", [])[0].get("hash")
            return jsonify({'type': 'success', 'message': message, 'pdf_link': pdf_link})
        else:
            return jsonify({'type': 'error', 'message': response.status_code})

    except Exception as e:
        return jsonify({'type': 'error', 'message': 'function error:' + str(e)})
