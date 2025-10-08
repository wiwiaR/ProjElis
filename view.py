import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkFont

class View:
    def __init__(self):
        self.janela = tk.Tk()
        self.janela.title("Super Pagador 2000")
        self.janela.geometry("600x500")
        self.janela.configure(bg='#f0f0f0')

        self.arquivo_selecionado = tk.StringVar(value="Nenhum arquivo selecionado")
        self.alterar_intervalo = tk.BooleanVar()
        self.meses_intervalo = tk.IntVar(value=0)

        self.criar_interface()

    def criar_interface(self):
        main_frame = ttk.Frame(self.janela, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.janela.columnconfigure(0, weight=1)
        self.janela.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        titulo_font = tkFont.Font(family="Arial", size=16, weight="bold")
        titulo = ttk.Label(main_frame, text="Super Pagador 2000",
                           font=titulo_font, foreground="#2c3e50")
        titulo.grid(row=0, column=0, columnspan=3, pady=(0, 30))

        self.criar_secao_arquivo(main_frame, row=1)

        separador1 = ttk.Separator(main_frame, orient='horizontal')
        separador1.grid(row=2, column=0, columnspan=3, sticky='ew', pady=20)

        self.criar_secao_intervalo(main_frame, row=3)

        separador2 = ttk.Separator(main_frame, orient='horizontal')
        separador2.grid(row=4, column=0, columnspan=3, sticky='ew', pady=20)

        self.criar_secao_informacoes(main_frame, row=5)

        separador3 = ttk.Separator(main_frame, orient='horizontal')
        separador3.grid(row=6, column=0, columnspan=3, sticky='ew', pady=20)

        self.criar_botao_principal(main_frame, row=7)

    def criar_secao_arquivo(self, parent, row):
        secao_font = tkFont.Font(family="Arial", size=12, weight="bold")
        lbl_arquivo = ttk.Label(parent, text="Arquivo", font=secao_font)
        lbl_arquivo.grid(row=row, column=0, sticky='w', pady=(0, 10))

        frame_arquivo = ttk.Frame(parent)
        frame_arquivo.grid(row=row + 1, column=0, columnspan=3, sticky='ew', pady=(0, 10))
        frame_arquivo.columnconfigure(1, weight=1)

        btn_selecionar = ttk.Button(frame_arquivo, text="Selecionar",
                                    command=self.selecionar_arquivo)
        btn_selecionar.grid(row=0, column=0, padx=(0, 10))

        lbl_nome_arquivo = ttk.Label(frame_arquivo, textvariable=self.arquivo_selecionado,
                                     background='white', relief='sunken', padding="5")
        lbl_nome_arquivo.grid(row=0, column=1, sticky='ew')

        self.btn_enviar = ttk.Button(frame_arquivo, text="Enviar",
                                     command=self.enviar_pagamentos, state='disabled')
        self.btn_enviar.grid(row=0, column=2, padx=(10, 0))

    def criar_secao_intervalo(self, parent, row):
        secao_font = tkFont.Font(family="Arial", size=12, weight="bold")
        lbl_intervalo = ttk.Label(parent, text="Intervalo", font=secao_font)
        lbl_intervalo.grid(row=row, column=0, sticky='w', pady=(0, 10))

        check_intervalo = ttk.Checkbutton(parent,
                                          text="Alterar o intervalo de meses nas datas de vencimento das parcelas",
                                          variable=self.alterar_intervalo,
                                          command=self.toggle_intervalo)
        check_intervalo.grid(row=row + 1, column=0, columnspan=2, sticky='w', pady=(0, 10))

        self.frame_controles_intervalo = ttk.Frame(parent)
        self.frame_controles_intervalo.grid(row=row + 2, column=0, columnspan=3, sticky='w', pady=(0, 10))

        lbl_meses = ttk.Label(self.frame_controles_intervalo, text="Meses:")
        lbl_meses.grid(row=0, column=0, padx=(0, 10))

        spin_meses = ttk.Spinbox(self.frame_controles_intervalo,
                                 from_=0, to=24,
                                 textvariable=self.meses_intervalo,
                                 width=5, state='disabled')
        spin_meses.grid(row=0, column=1)

        self.toggle_intervalo()

    def criar_secao_informacoes(self, parent, row):
        secao_font = tkFont.Font(family="Arial", size=12, weight="bold")
        lbl_info = ttk.Label(parent, text="Informações", font=secao_font)
        lbl_info.grid(row=row, column=0, sticky='nw', pady=(0, 10))

        frame_info = ttk.Frame(parent)
        frame_info.grid(row=row + 1, column=0, columnspan=3, sticky='ew', pady=(0, 10))
        frame_info.columnconfigure(0, weight=1)

        self.texto_info = tk.Text(frame_info, height=8, width=60, wrap='word',
                                  background='white', relief='sunken',
                                  borderwidth=1, padx=10, pady=10)

        scrollbar = ttk.Scrollbar(frame_info, orient='vertical', command=self.texto_info.yview)
        self.texto_info.configure(yscrollcommand=scrollbar.set)

        self.texto_info.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')

        texto_inicial = """• Nenhum arquivo carregado
        • Pronto para operar
        • Selecione um arquivo CSV para começar"""

        self.texto_info.insert('1.0', texto_inicial)
        self.texto_info.config(state='disabled')

    def criar_botao_principal(self, parent, row):
        estilo_botao = ttk.Style()
        estilo_botao.configure('BotaoPrincipal.TButton',
                               font=('Arial', 12, 'bold'),
                               padding='10 5')

        btn_gerar = ttk.Button(parent, text="Gerar Pagamento",
                               style='BotaoPrincipal.TButton',
                               command=self.gerar_pagamento)
        btn_gerar.grid(row=row, column=0, columnspan=3, pady=20)

    def toggle_intervalo(self):
        if self.alterar_intervalo.get():
            for widget in self.frame_controles_intervalo.winfo_children():
                widget.configure(state='normal')
        else:
            for widget in self.frame_controles_intervalo.winfo_children():
                if isinstance(widget, ttk.Spinbox):
                    widget.configure(state='disabled')

    def selecionar_arquivo(self):
        from tkinter import filedialog
        arquivo = filedialog.askopenfilename(
            title="Selecionar Arquivo",
            filetypes=(("CSV files", "*.csv"), ("Todos os arquivos", "*.*"))
        )

        if arquivo:
            self.arquivo_selecionado.set(arquivo.split('/')[-1])
            self.btn_enviar.config(state='normal')
            self.atualizar_informacoes(
                f"• Arquivo carregado: {arquivo.split('/')[-1]}\n• Pronto para enviar pagamentos")

    def enviar_informacoes(self, msg):
        self.atualizar_informacoes("• Enviando pagamentos...\n• Processando dados do arquivo")

    def atualizar_informacoes(self, msg):
        self.texto_info.config(state='normal')
        self.texto_info.delete('1.0', tk.END)
        self.texto_info.insert('1.0', msg)
        self.texto_info.config(state='disabled')

    def enviar_pagamentos(self):
        self.atualizar_informacoes("• Enviando pagamentos...\n• Processando dados do arquivo")

    def gerar_pagamento(self):
        meses = self.meses_intervalo.get() if self.alterar_intervalo.get() else 0
        self.atualizar_informacoes(f"• Gerando pagamentos...\n• Intervalo: {meses} meses\n• Processo iniciado")

    def executar(self):
        self.janela.mainloop()

