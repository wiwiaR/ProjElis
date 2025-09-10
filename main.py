from tkinter import *
from tkinter import ttk, messagebox
from tkinter import filedialog
import requests
import pandas as pd
from misc import *

janela = Tk()
tabela = None
dict_clientes = None


def select_file(callback=None):
    global tabela, dict_clientes
    filename = filedialog.askopenfilename(title="Selecionar Arquivo",
                                          filetypes=(("Planilhas", "*.csv"),
                                                     ("Excel", "*.xlsx"),))
    if filename:
        try:
            getClientes()

            tabela = pd.read_csv(filename)

            tabela['customer'] = tabela['customer'].replace(dict_clientes)
            print(f"Arquivo {filename} carregado com sucesso!")
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
            "billingType": "BOLETO",
            "installmentCount": int(row["installmentCount"]),
            "customer": str(row["customer"]),
            "installmentValue": float(row["value"]),
            "dueDate": str(row["dueDate"]),
            "description": str(row["description"]),
        }

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "access_token": "$aact_prod_000MzkwODA2MWY2OGM3MWRlMDU2NWM3MzJlNzZmNGZhZGY6OjBmMmEzYzFhLTMxM2YtNDFlZC1hMDRlLTdmYjg5ZDc5MTNkNTo6JGFhY2hfNmQzYWRjNTAtNDJiNi00NzVmLWIxMGItYjYxMmNjMjVkNWQw"
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

def putVencimentoCobranca(dados_pagamento):
    for pagamento in dados_pagamento:
        url = "https://api.asaas.com/v3/payments/" + str(pagamento["id"])
        payload = {
            "billingType": "BOLETO",
            "value": float(pagamento["paymentValue"]),
            "dueDate": str(pagamento["dueDate"]),
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "access_token": "$aact_prod_000MzkwODA2MWY2OGM3MWRlMDU2NWM3MzJlNzZmNGZhZGY6OjBmMmEzYzFhLTMxM2YtNDFlZC1hMDRlLTdmYjg5ZDc5MTNkNTo6JGFhY2hfNmQzYWRjNTAtNDJiNi00NzVmLWIxMGItYjYxMmNjMjVkNWQw"
        }

        try:
            response = requests.put(url, json=payload, headers=headers)

            if response.status_code == 200:
                print(f"✅ Vencimento {dados_pagamento.index} atualizado com sucesso!")
            else:
                print(f"❌ Erro na atualização do vencimento {dados_pagamento.index}: {response.status_code}, mensagem {response.text}")
        except Exception as e:
            print(f"❌ Exception no vencimento {dados_pagamento.index}: {e}")


def getCobrancasDoParcelamento(id_parcela):
    url = "https://api.asaas.com/v3/installments/" + str(id_parcela) + "/payments"
    headers = {
        "accept": "application/json",
        "access_token": "$aact_prod_000MzkwODA2MWY2OGM3MWRlMDU2NWM3MzJlNzZmNGZhZGY6OjBmMmEzYzFhLTMxM2YtNDFlZC1hMDRlLTdmYjg5ZDc5MTNkNTo6JGFhY2hfNmQzYWRjNTAtNDJiNi00NzVmLWIxMGItYjYxMmNjMjVkNWQw"
    }
    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            dados_pagamento = response.json()
            dados_corrigidos = extrair_dados_pagamentos(dados_pagamento)
            putVencimentoCobranca(dados_corrigidos)
        else:
            print("babou")
    except Exception as e:
        print(f"Falhou: {e}")

def getClientes():
    global dict_clientes
    url = "https://api.asaas.com/v3/customers"
    headers = {
        "accept": "application/json",
        "access_token": "$aact_prod_000MzkwODA2MWY2OGM3MWRlMDU2NWM3MzJlNzZmNGZhZGY6OjBmMmEzYzFhLTMxM2YtNDFlZC1hMDRlLTdmYjg5ZDc5MTNkNTo6JGFhY2hfNmQzYWRjNTAtNDJiNi00NzVmLWIxMGItYjYxMmNjMjVkNWQw"
    }
    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            dict_clientes = extrair_clientes_por_nome(response.json())
            print("Get clientes executado com sucesso!")
        else:
            print(f"❌ Erro no get clientes: {response.status_code}, mensagem {response.text}")
    except Exception as e:
        print(f"❌ Exception no get: {e}")



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


