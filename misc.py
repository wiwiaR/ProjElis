from datetime import datetime
from dateutil.relativedelta import relativedelta

def adicionar_meses(data_string, meses):
    try:
        data = datetime.strptime(data_string, "%Y-%m-%d")
        nova_data = data + relativedelta(months=meses)
        return nova_data.strftime("%Y-%m-%d")
    except ValueError:
        print(f"Data inválida: {data_string}")
        return data_string
    except Exception as e:
        print(f"Erro ao processar data: {e}")
        return data_string

def ajustar_datas_pagamentos(dados_ordenados, meses_para_adicionar):
    dados_ajustados = []
    data_aux = ''

    for pagamento in dados_ordenados:
        novo_pagamento = pagamento.copy()

        if pagamento['installmentNumber'] != 1:
            nova_data = adicionar_meses(data_aux, meses_para_adicionar)
            novo_pagamento['dueDate'] = nova_data
            novo_pagamento['meses_adicionados'] = meses_para_adicionar

            dados_ajustados.append(novo_pagamento)

        data_aux = novo_pagamento['dueDate']

    return dados_ajustados

def extrair_dados_pagamentos(response_data):
    dados_extraidos = []

    if 'data' in response_data and isinstance(response_data['data'], list):
        for pagamento in response_data['data']:
            dados = {
                'id': pagamento.get('id'),
                'dueDate': pagamento.get('dueDate'),
                'installmentNumber': pagamento.get('installmentNumber'),
                'paymentValue': pagamento.get('paymentValue'),
            }
            dados_extraidos.append(dados)

    dados_ordenados = sorted(dados_extraidos, key=lambda x: x['installmentNumber'])
    dados_ajustados = ajustar_datas_pagamentos(dados_ordenados, 3)

    return dados_ajustados