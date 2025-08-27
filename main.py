from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import requests
import pandas as pd

def select_file():
    filename = filedialog.askopenfilename(title="Selecionar Arquivo",
                                          filetypes=(("Planilhas", "*.csv"),
                                                     ("Excel", "*.xlsx"),))
    file = open(filename, 'r')
    print(file.read())
    file.close()

    tabela = pd.read_csv(filename)




def post_pagamento():
    url = "https://api.asaas.com/v3/payments"

    payload = {
        "object": "payment",
        "dateCreated": "2025-07-30",
        "customer": "cus_000131035438",
        "value": 500,
        "netValue": 499.01,
        "description": "Pedido #DEV001",
        "billingType": "PIX",
        "dueDate": "2025-10-15"
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "access_token": "$aact_prod_000MzkwODA2MWY2OGM3MWRlMDU2NWM3MzJlNzZmNGZhZGY6OjI0ZTcyOWZlLWRhNzktNDRlZi04MzhjLWJhMGZmMDZmMDY5OTo6JGFhY2hfYjRmNmYwZTMtNjExMC00MjVhLWJhNzMtZTAwMmYwZDFhYTcz"
    }

    response = requests.post(url, json=payload, headers=headers)

    print(response.text)


janela = Tk()

janela.title("Lançar Boletos")
frm = ttk.Frame(janela, padding=100)
frm.grid()
ttk.Button(frm, text="Selecionar", command=select_file).grid(column=1, row=0)
ttk.Button(frm, text="Enviar", command=post_pagamento).grid(column=2, row=0)

if __name__ == '__main__':
    janela.mainloop()


