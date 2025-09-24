from tkinter import *
from tkinter import ttk, messagebox
from tkinter import filedialog
import requests, json
import pandas as pd
from misc import *

accessToken = '$aact_prod_000MzkwODA2MWY2OGM3MWRlMDU2NWM3MzJlNzZmNGZhZGY6Ojk0ZTllMGQwLWIyNmYtNDEyNi1hYmM4LTdhOWVmYjY5ZDdiYjo6JGFhY2hfODE3NmI4ZmQtMWQzNi00MGE3LWE1ZTUtMTAzNzlkZWRjYmM5'

janela = Tk()
tabela = None
dict_clientes = None
btnEnviar = None
edtMeses = None
btnSelecionar = None
#gauge = None
chkAlteraVencimento = False
nome_arquivo = StringVar(value='Arquivo')
qtd_arquivos = StringVar(value=' ')
alert = StringVar(value='')

def select_file(callback=None):
    global tabela, dict_clientes, nome_arquivo

    alert.set('')
    btnSelecionar.config(text='Selecionar')

    filename = filedialog.askopenfilename(title="Selecionar Arquivo",
                                          filetypes=(("Planilhas", "*.csv"),
                                                     ("Excel", "*.xlsx"),))
    if filename:
        try:
            getClientes()

            tabela = pd.read_csv(filename)
            nome_arquivo.set(filename)
            qtd_arquivos.set(f"{len(tabela)} Pagamentos")
            btnEnviar.config(state=NORMAL)

            tabela['customer'] = tabela['customer'].map(dict_clientes)
            print(f"Arquivo {filename} carregado com sucesso!")
            if callback:
                callback(tabela)
            return tabela
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao ler o arquivo: {e}")
    return None


def post_pagamento():
    global tabela
    janela.config(cursor="watch")
    janela.update()
    #gauge.config(maximum=len(tabela))
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
            "access_token": accessToken
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            #gauge['value'] += 1
            if response.status_code == 200:
                print(f"✅ Pagamento {index} enviado com sucesso!")
                if chkAlteraVencimento:
                    id_parcela = response.json().get("installment")
                    getCobrancasDoParcelamento(id_parcela)
            else:
                error_data = json.loads(response.text)
                descricao_erro = error_data['errors'][0]['description']
                alert.set(alert.get() + f"Pagamento {index}: {descricao_erro}\n")
                print(f"❌ Erro no pagamento {index}: {response.status_code}, mensagem {response.text}")

        except Exception as e:
            print(f"❌ Exception no pagamento {index}: {e}")

    janela.config(cursor="")
    btnSelecionar.config(text="Novo Pagamento")

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
            "access_token": accessToken
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
    url = "https://api.asaas.com/v3/installments/" + str(id_parcela) + "/payments?limit=100"
    headers = {
        "accept": "application/json",
        "access_token": accessToken
    }
    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            dados_pagamento = response.json()
            dados_corrigidos = extrair_dados_pagamentos(dados_pagamento, edtMeses.get())
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
        "access_token": accessToken
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
    global chkAlteraVencimento
    if checkvar.get():
        edtMeses.config(state=NORMAL)
        chkAlteraVencimento = True
    else:
        edtMeses.config(state=DISABLED)
        chkAlteraVencimento = False


checkvar = IntVar()
checkvar.set(0)


janela.title("Super Pagador 2000")
frm = ttk.Frame(janela, padding=100)
frm.grid()

ttk.Label(frm, textvariable=nome_arquivo).grid(column=0, row=0, columnspan=3)
ttk.Label(frm, textvariable=qtd_arquivos).grid(column=0, row=1, columnspan=3)

btnSelecionar = Button(frm, text="Selecionar", command=select_file, state=NORMAL)
btnSelecionar.grid(column=0, row=3)

btnEnviar = Button(frm, text="Enviar", command=post_pagamento, state=DISABLED)
btnEnviar.grid(column=2, row=3)

ttk.Label(frm, text=" ").grid(column=0, row=4, columnspan=3)

ttk.Checkbutton(frm, text="Alterar intervalo da data de vencimento",
                variable=checkvar, command=verifica_check).grid(column=0, row=6, columnspan=3)

edtMeses = Spinbox(frm, from_=0, to=12, increment=1, state="disabled")
edtMeses.grid(column=0, row=5, columnspan=3)

ttk.Label(frm, text=" ").grid(column=0, row=7, columnspan=3)

ttk.Label(frm, textvariable=alert).grid(column=0, row=8, columnspan=3)
#gauge = ttk.Progressbar(frm, orient=HORIZONTAL, length=300, mode="determinate")
#gauge.grid(column=0, row=8, columnspan=3)



if __name__ == '__main__':
    janela.mainloop()


