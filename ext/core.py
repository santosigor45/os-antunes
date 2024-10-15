from flask import request, jsonify
from flask_login import current_user
import requests
import os


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
        url = os.environ.get('URL')
        headers = {'Content-Type': 'application/json',
                   'access-token': os.environ.get('ACCESS_TOKEN'),
                   'secret-access-token': os.environ.get('SECRET_ACCESS_TOKEN')}

        response = requests.post(url, json=collected_data, headers=headers)
        if response.status_code == 200:
            return jsonify({'type': 'success', 'message': message})
        else:
            return jsonify({'type': 'error', 'message': response.status_code})

    except Exception as e:
        return jsonify({'type': 'error', 'message': 'function error:' + str(e)})
