from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import requests
import pandas as pd

janela = Tk()
tabela = pd.DataFrame()


def select_file():
    filename = filedialog.askopenfilename(title="Selecionar Arquivo",
                                          filetypes=(("Planilhas", "*.csv"),
                                                     ("Excel", "*.xlsx"),))
    nome_arquivo.set(filename)
    file = open(filename, 'r')
    print(file.read())
    file.close()

    tabela = pd.read_csv(filename)




def post_pagamento():
    for linha in tabela.index:
        url = "https://api.asaas.com/v3/payments"

        payload = {
            "billingType": "UNDEFINED",
            "installmentCount": str(tabela.loc[linha, "installmentCount"]),
            "customer": str(tabela.loc[linha, "customer"]),
            "value": tabela.loc[linha, "value"],
            "dueDate": str(tabela.loc[linha, "dueDate"]),
            "description": str(tabela.loc[linha, "description"]),
        }

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "access_token": "$aact_prod_000MzkwODA2MWY2OGM3MWRlMDU2NWM3MzJlNzZmNGZhZGY6OjI0ZTcyOWZlLWRhNzktNDRlZi04MzhjLWJhMGZmMDZmMDY5OTo6JGFhY2hfYjRmNmYwZTMtNjExMC00MjVhLWJhNzMtZTAwMmYwZDFhYTcz"
        }

        response = requests.post(url, json=payload, headers=headers)

        print(response.text)

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


