from tkinter import *
from tkinter import ttk, messagebox
from tkinter import filedialog
import requests
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

janela = Tk()
tabela = None

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

    for pagamento in dados_ordenados:
        # Cria uma cópia do dicionário para não modificar o original
        novo_pagamento = pagamento.copy()

        # Ajusta a data
        nova_data = adicionar_meses(pagamento['dueDate'], meses_para_adicionar)
        novo_pagamento['dueDate'] = nova_data
        novo_pagamento['meses_adicionados'] = meses_para_adicionar

        dados_ajustados.append(novo_pagamento)

    return dados_ajustados


def select_file(callback=None):
    global tabela
    filename = filedialog.askopenfilename(title="Selecionar Arquivo",
                                          filetypes=(("Planilhas", "*.csv"),
                                                     ("Excel", "*.xlsx"),))
    if filename:
        try:
            tabela = pd.read_csv(filename)
            print(f"Arquivo {filename} carregado com sucesso!")
            # Chama a função callback passando a tabela
            if callback:
                callback(tabela)
            return tabela
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao ler o arquivo: {e}")
    return None




def post_pagamento():
    global tabela
    for index, row in tabela.iterrows():
        url = "https://api.asaas.com/v3/payments"

        payload = {
            "billingType": "UNDEFINED",
            "installmentCount": int(row["installmentCount"]),
            "customer": str(row["customer"]),
            "installmentValue": float(row["value"]),
            "dueDate": str(row["dueDate"]),
            "description": str(row["description"]),
        }

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "access_token": "$aact_prod_000MzkwODA2MWY2OGM3MWRlMDU2NWM3MzJlNzZmNGZhZGY6OmI2MDI4NWI5LWQ4ZTAtNDZjYS1iOWY3LWM2NmI0NzhhYzU5Mjo6JGFhY2hfMjVhNDNiMDMtYjI3OC00MzVhLWEyOTAtYzI4MWE0NmRlYmIx"
        }

        try:
            response = requests.post(url, json=payload, headers=headers)

            if response.status_code == 200:
                print(f"✅ Pagamento {index} enviado com sucesso!")
                id_parcela = response.json().get("installment")
                getCobrancasDoParcelamento(id_parcela)
            else:
                print(f"❌ Erro no pagamento {index}: {response.status_code}, mensagem {response.text}")

        except Exception as e:
            print(f"❌ Exception no pagamento {index}: {e}")

def getCobrancasDoParcelamento(id_parcela):
    url = "https://api.asaas.com/v3/installments/" + str(id_parcela) + "/payments"
    headers = {
        "accept": "application/json",
        "access_token": "$aact_prod_000MzkwODA2MWY2OGM3MWRlMDU2NWM3MzJlNzZmNGZhZGY6OmI2MDI4NWI5LWQ4ZTAtNDZjYS1iOWY3LWM2NmI0NzhhYzU5Mjo6JGFhY2hfMjVhNDNiMDMtYjI3OC00MzVhLWEyOTAtYzI4MWE0NmRlYmIx"
    }
    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            extrair_dados_pagamentos(response.json())
        else:
            print("babou")
    except Exception as e:
        print(f"Falhou: {e}")


def extrair_dados_pagamentos(response_data):
    dados_extraidos = []

    if 'data' in response_data and isinstance(response_data['data'], list):
        for pagamento in response_data['data']:
            dados = {
                'id': pagamento.get('id'),
                'dueDate': pagamento.get('dueDate'),
                'installmentNumber': pagamento.get('installmentNumber')
            }
            dados_extraidos.append(dados)

    dados_ordenados = sorted(dados_extraidos, key=lambda x: x['installmentNumber'])
    dados_ajustados = ajustar_datas_pagamentos(dados_ordenados, 3)


    return dados_extraidos

def verifica_check():
    if checkvar.get():
        spin.config(state=NORMAL)
    else:
        spin.config(state=DISABLED)

nome_arquivo = StringVar(value='Arquivo')
checkvar = IntVar()
checkvar.set(0)


janela.title("Super Pagador 2000")
frm = ttk.Frame(janela, padding=100)
frm.grid()
ttk.Label(frm, textvariable=nome_arquivo).grid(column=0, row=0)
ttk.Button(frm, text="Selecionar", command=select_file).grid(column=0, row=1)
ttk.Button(frm, text="Enviar", command=post_pagamento).grid(column=0, row=2)
ttk.Checkbutton(frm, text="Alterar intervalo da data de vencimento", variable=checkvar, command=verifica_check).grid(column=1, row=3)

spin = Spinbox(frm, from_=0, to=12, increment=1, state="disabled")
spin.grid(column=0, row=3)


if __name__ == '__main__':
    janela.mainloop()


