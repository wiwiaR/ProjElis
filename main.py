from tkinter import *
from tkinter import ttk, messagebox
from tkinter import filedialog
import requests, json
import pandas as pd
from misc import *
#from view import *
import os

accessToken = os.getenv("ASAAS_ERIRMARA_KEY")

janela = Tk()
tabela = None
dict_clientes = None
btnEnviar = None
edtMeses = None
btnSelecionar = None
chkAlteraVencimento = False
nome_arquivo = StringVar(value='Arquivo')
qtd_arquivos = StringVar(value=' ')
alert = StringVar(value='                                          ')

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
            if response.status_code == 200:
                print(f"✅ Pagamento {index} enviado com sucesso!")
                if chkAlteraVencimento:
                    id_parcela = response.json().get("installment")
                    getCobrancasDoParcelamento(id_parcela)
            else:
                error_data = json.loads(response.text)
                descricao_erro = error_data['errors'][0]['description']
                alert.set(alert.get() + f"Pagamento {index + 1}: {descricao_erro}\n")
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
frm =  ttk.Frame(janela, padding="20")
frm.grid()

btnSelecionar = ttk.Button(frm, text="Selecionar", command=select_file, state=NORMAL)
btnSelecionar.grid(column=0, row=3, padx=(0, 13))

lbl_nome_arquivo = ttk.Label(frm, textvariable=nome_arquivo,
                                     background='white', relief='sunken', padding="5", width=40)
lbl_nome_arquivo.grid(row=3, column=1)

btnEnviar = ttk.Button(frm, text="Enviar", command=post_pagamento, state=DISABLED)
btnEnviar.grid(column=0, row=11, columnspan=2)

ttk.Label(frm, text=" ").grid(column=0, row=4)

ttk.Checkbutton(frm, text="Alterar intervalo da data de vencimento",
                variable=checkvar, command=verifica_check).grid(column=1, row=5)

edtMeses = Spinbox(frm, from_=0, to=12, increment=1, state="disabled", width=10)
edtMeses.grid(column=0, row=5, padx=(0, 10))

ttk.Label(frm, text=" ").grid(column=0, row=6)
ttk.Label(frm, text=" ").grid(column=0, row=8)

ttk.Label(frm, textvariable=alert, background='white', relief='sunken', padding="5", width=55).grid(column=0, row=7, columnspan=2)



if __name__ == '__main__':
     janela.mainloop()
