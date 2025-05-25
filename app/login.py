import tkinter as tk
from tkinter import messagebox
from .database import (
    inserir_cliente,
    buscar_cliente_por_email,
    buscar_cliente_por_nome
)
from .agenda import criar_interface

cliente_logado_id = None

# --- Configurações Visuais ---
COR_FUNDO_JANELA = "#2E2E2E"
COR_TEXTO_LABEL = "#E0E0E0"
COR_FUNDO_ENTRY = "#3C3C3C"
COR_TEXTO_ENTRY = "#FFFFFF"
COR_CURSOR_ENTRY = "#FFFFFF"

COR_BOTAO_PRIMARIO_BG = "#0078D4" # Azul
COR_BOTAO_PRIMARIO_FG = "#FFFFFF"
COR_BOTAO_PRIMARIO_ACTIVE_BG = "#005A9E"

COR_BOTAO_SECUNDARIO_BG = "#555555" # Cinza escuro
COR_BOTAO_SECUNDARIO_FG = "#FFFFFF"
COR_BOTAO_SECUNDARIO_ACTIVE_BG = "#6E6E6E"

FONTE_PADRAO = ("Segoe UI", 10)
FONTE_LABEL = ("Segoe UI", 11)
FONTE_BOTAO = ("Segoe UI", 10, "bold")
FONTE_TITULO_JANELA = ("Segoe UI", 14, "bold")


def centralizar_janela(janela, largura, altura):
    largura_tela = janela.winfo_screenwidth()
    altura_tela = janela.winfo_screenheight()
    x = (largura_tela // 2) - (largura // 2)
    y = (altura_tela // 2) - (altura // 2)
    janela.geometry(f'{largura}x{altura}+{x}+{y}')

def verificar_email_existente(email: str) -> bool:
    cliente = buscar_cliente_por_email(email)
    return cliente is not None

def cadastrar_usuario_nova_conta(nome_entry, email_entry, telefone_entry, senha_entry, tela_cadastro):
    nome = nome_entry.get().strip()
    email = email_entry.get().strip()
    telefone = telefone_entry.get().strip()
    senha = senha_entry.get()

    if not all([nome, email, telefone, senha]):
        messagebox.showerror("Erro de Cadastro", "Todos os campos são obrigatórios!", parent=tela_cadastro)
        return
    if "@" not in email or "." not in email:
        messagebox.showerror("Erro de Cadastro", "Formato de email inválido.", parent=tela_cadastro)
        return

    if verificar_email_existente(email):
        messagebox.showerror("Erro de Cadastro", f"O email '{email}' já está cadastrado.", parent=tela_cadastro)
        return
    
    cliente_por_nome = buscar_cliente_por_nome(nome)
    if cliente_por_nome:
        messagebox.showerror("Erro de Cadastro", f"Nome de usuário '{nome}' já em uso. Por favor, escolha outro nome.", parent=tela_cadastro)
        return

    if inserir_cliente(nome, email, telefone, senha):
        messagebox.showinfo("Sucesso", "Cadastro realizado com sucesso!", parent=tela_cadastro)
        tela_cadastro.destroy()
    else:
        messagebox.showerror("Erro de Cadastro", "Não foi possível realizar o cadastro.", parent=tela_cadastro)

def autenticar_usuario(email_entry, senha_entry, tela_login_atual):
    global cliente_logado_id

    email = email_entry.get().strip()
    senha = senha_entry.get()

    if not email or not senha:
        messagebox.showerror("Erro de Login", "Email e Senha são obrigatórios!", parent=tela_login_atual)
        return

    cliente = buscar_cliente_por_email(email)

    if cliente and cliente['senha_cliente'] == senha:
        messagebox.showinfo("Login", f"Bem-vindo(a) {cliente['nome_cliente']}!", parent=tela_login_atual)
        cliente_logado_id = cliente['id_cliente']
        tela_login_atual.destroy()
        abrir_tela_agenda(cliente_logado_id)
    else:
        messagebox.showerror("Erro de Login", "Email ou Senha incorretos!", parent=tela_login_atual)
        cliente_logado_id = None

def abrir_tela_agenda(id_cliente_logado: int):
    app_agenda = tk.Tk()
    app_agenda.title("Sistema de Agendamento - Barbearia")
    # A geometria será definida pela tela de agenda, mas podemos configurar o fundo aqui se quisermos
    # app_agenda.configure(bg=COR_FUNDO_JANELA) 
    criar_interface(app_agenda, id_cliente_logado)
    app_agenda.mainloop()

def abrir_janela_cadastro(tela_login_principal):
    largura_cadastro = 400
    altura_cadastro = 280
    
    tela_cadastro = tk.Toplevel(tela_login_principal)
    tela_cadastro.title("Cadastrar Nova Conta")
    tela_cadastro.configure(bg=COR_FUNDO_JANELA)
    tela_cadastro.grab_set()
    tela_cadastro.resizable(False, False)
    centralizar_janela(tela_cadastro, largura_cadastro, altura_cadastro)


    tk.Label(tela_cadastro, text="Criar Nova Conta", font=FONTE_TITULO_JANELA, bg=COR_FUNDO_JANELA, fg=COR_TEXTO_LABEL).pack(pady=(15,10))

    frame_campos = tk.Frame(tela_cadastro, bg=COR_FUNDO_JANELA)
    frame_campos.pack(pady=5, padx=20, fill=tk.X)

    label_width = 15 

    tk.Label(frame_campos, text="Nome Completo:", font=FONTE_LABEL, bg=COR_FUNDO_JANELA, fg=COR_TEXTO_LABEL, width=label_width, anchor="w").grid(row=0, column=0, sticky=tk.W, pady=3)
    nome_entry_cad = tk.Entry(frame_campos, font=FONTE_PADRAO, width=25, bg=COR_FUNDO_ENTRY, fg=COR_TEXTO_ENTRY, insertbackground=COR_CURSOR_ENTRY, relief=tk.FLAT, borderwidth=2)
    nome_entry_cad.grid(row=0, column=1, pady=3, sticky="ew")

    tk.Label(frame_campos, text="Email:", font=FONTE_LABEL, bg=COR_FUNDO_JANELA, fg=COR_TEXTO_LABEL, width=label_width, anchor="w").grid(row=1, column=0, sticky=tk.W, pady=3)
    email_entry_cad = tk.Entry(frame_campos, font=FONTE_PADRAO, width=25, bg=COR_FUNDO_ENTRY, fg=COR_TEXTO_ENTRY, insertbackground=COR_CURSOR_ENTRY, relief=tk.FLAT, borderwidth=2)
    email_entry_cad.grid(row=1, column=1, pady=3, sticky="ew")

    tk.Label(frame_campos, text="Telefone:", font=FONTE_LABEL, bg=COR_FUNDO_JANELA, fg=COR_TEXTO_LABEL, width=label_width, anchor="w").grid(row=2, column=0, sticky=tk.W, pady=3)
    telefone_entry_cad = tk.Entry(frame_campos, font=FONTE_PADRAO, width=25, bg=COR_FUNDO_ENTRY, fg=COR_TEXTO_ENTRY, insertbackground=COR_CURSOR_ENTRY, relief=tk.FLAT, borderwidth=2)
    telefone_entry_cad.grid(row=2, column=1, pady=3, sticky="ew")

    tk.Label(frame_campos, text="Senha:", font=FONTE_LABEL, bg=COR_FUNDO_JANELA, fg=COR_TEXTO_LABEL, width=label_width, anchor="w").grid(row=3, column=0, sticky=tk.W, pady=3)
    senha_entry_cad = tk.Entry(frame_campos, show="*", font=FONTE_PADRAO, width=25, bg=COR_FUNDO_ENTRY, fg=COR_TEXTO_ENTRY, insertbackground=COR_CURSOR_ENTRY, relief=tk.FLAT, borderwidth=2)
    senha_entry_cad.grid(row=3, column=1, pady=3, sticky="ew")
    
    frame_campos.grid_columnconfigure(1, weight=1) # Faz a coluna dos entries expandir

    btn_cadastrar = tk.Button(tela_cadastro, text="Cadastrar", font=FONTE_BOTAO, 
                              bg=COR_BOTAO_PRIMARIO_BG, fg=COR_BOTAO_PRIMARIO_FG, 
                              activebackground=COR_BOTAO_PRIMARIO_ACTIVE_BG, activeforeground=COR_BOTAO_PRIMARIO_FG,
                              relief=tk.FLAT, borderwidth=0, width=15, cursor="hand2",
                              command=lambda: cadastrar_usuario_nova_conta(
                                  nome_entry_cad, email_entry_cad, telefone_entry_cad, senha_entry_cad, tela_cadastro
                              ))
    btn_cadastrar.pack(pady=(15, 20))
    
    nome_entry_cad.focus_set()

def tela_login_principal():
    largura_login = 350
    altura_login = 330

    root_login = tk.Tk()
    root_login.title("Login - Barbearia do Zé") # Exemplo de nome
    root_login.configure(bg=COR_FUNDO_JANELA)
    root_login.resizable(False, False)
    centralizar_janela(root_login, largura_login, altura_login)
    
    # Para um ícone (opcional, precisa de um arquivo .ico)
    # try:
    #     root_login.iconbitmap('caminho/para/seu/icone.ico')
    # except tk.TclError:
    #     print("Ícone não encontrado ou formato inválido.")

    tk.Label(root_login, text="Bem-vindo!", font=FONTE_TITULO_JANELA, bg=COR_FUNDO_JANELA, fg=COR_TEXTO_LABEL).pack(pady=(20,10))

    frame_campos_login = tk.Frame(root_login, bg=COR_FUNDO_JANELA)
    frame_campos_login.pack(pady=10, padx=30, fill=tk.X)

    tk.Label(frame_campos_login, text="Email:", font=FONTE_LABEL, bg=COR_FUNDO_JANELA, fg=COR_TEXTO_LABEL, anchor="w").pack(fill=tk.X, pady=(5,0))
    email_entry_login = tk.Entry(frame_campos_login, font=FONTE_PADRAO, width=30, bg=COR_FUNDO_ENTRY, fg=COR_TEXTO_ENTRY, insertbackground=COR_CURSOR_ENTRY, relief=tk.FLAT, borderwidth=2)
    email_entry_login.pack(fill=tk.X, ipady=2) # ipady para altura interna
    email_entry_login.focus_set()

    tk.Label(frame_campos_login, text="Senha:", font=FONTE_LABEL, bg=COR_FUNDO_JANELA, fg=COR_TEXTO_LABEL, anchor="w").pack(fill=tk.X, pady=(10,0))
    senha_entry_login = tk.Entry(frame_campos_login, show="*", font=FONTE_PADRAO, width=30, bg=COR_FUNDO_ENTRY, fg=COR_TEXTO_ENTRY, insertbackground=COR_CURSOR_ENTRY, relief=tk.FLAT, borderwidth=2)
    senha_entry_login.pack(fill=tk.X, ipady=2)

    frame_botoes_login = tk.Frame(root_login, bg=COR_FUNDO_JANELA)
    frame_botoes_login.pack(pady=20, padx=30, fill=tk.X)

    btn_entrar = tk.Button(frame_botoes_login, text="Entrar", font=FONTE_BOTAO, 
                           bg=COR_BOTAO_PRIMARIO_BG, fg=COR_BOTAO_PRIMARIO_FG,
                           activebackground=COR_BOTAO_PRIMARIO_ACTIVE_BG, activeforeground=COR_BOTAO_PRIMARIO_FG,
                           relief=tk.FLAT, borderwidth=0, width=12, height=1, cursor="hand2",
                           command=lambda: autenticar_usuario(
                               email_entry_login, senha_entry_login, root_login
                           ))
    btn_entrar.pack(side=tk.LEFT, expand=True, padx=(0,5))

    btn_criar_conta = tk.Button(frame_botoes_login, text="Criar Conta", font=FONTE_BOTAO,
                                bg=COR_BOTAO_SECUNDARIO_BG, fg=COR_BOTAO_SECUNDARIO_FG,
                                activebackground=COR_BOTAO_SECUNDARIO_ACTIVE_BG, activeforeground=COR_BOTAO_SECUNDARIO_FG,
                                relief=tk.FLAT, borderwidth=0, width=12, height=1, cursor="hand2",
                                command=lambda: abrir_janela_cadastro(root_login))
    btn_criar_conta.pack(side=tk.RIGHT, expand=True, padx=(5,0))
    
    root_login.mainloop()

if __name__ == "__main__":
    tela_login_principal()