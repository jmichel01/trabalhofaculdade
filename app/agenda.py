import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime, time, timedelta

from .database import (
    listar_funcionarios,
    listar_servicos,
    inserir_agendamento,
    listar_agendamentos_para_display,
    deletar_agendamento,
    verificar_conflito_horario,
    buscar_nome_cliente_por_id,
    listar_servicos_por_funcionario
)

COR_FUNDO_JANELA = "#F0F0F0"
COR_TEXTO_GERAL = "#222222"
COR_TEXTO_LABEL_DESTAQUE = "#000000"

COR_FUNDO_WIDGETS = "#FFFFFF"
COR_TEXTO_WIDGETS = "#000000"
COR_CURSOR_ENTRY = "#000000"

COR_BOTAO_PRIMARIO_BG = "#0078D4"
COR_BOTAO_PRIMARIO_FG = "#FFFFFF"
COR_BOTAO_PRIMARIO_ACTIVE_BG = "#005A9E"

COR_BOTAO_SECUNDARIO_BG = "#E0E0E0"
COR_BOTAO_SECUNDARIO_FG = "#000000"
COR_BOTAO_SECUNDARIO_ACTIVE_BG = "#C8C8C8"

COR_AZUL_CLARINHO_DESTAQUE = "#AEC6CF" 
COR_AZUL_CLARINHO_TEXTO = "#000000"

COR_DESTAQUE_SELECAO_TREEVIEW_BG = COR_BOTAO_PRIMARIO_BG 
COR_DESTAQUE_SELECAO_TREEVIEW_FG = COR_BOTAO_PRIMARIO_FG

FONTE_PADRAO = ("Segoe UI", 10)
FONTE_LABEL = ("Segoe UI", 10) 
FONTE_BOTAO = ("Segoe UI", 10, "bold")
FONTE_TITULO_JANELA = ("Segoe UI", 18, "bold")
FONTE_TREEVIEW_HEADING = ("Segoe UI", 10, "bold")
FONTE_TREEVIEW_TEXT = ("Segoe UI", 9)

tree_agendamentos = None
combobox_servico_global = None
combobox_barbeiro_global = None
data_entry_global = None
combobox_hora_global = None
combobox_minuto_global = None
btn_agendar_global = None

mapa_funcionarios = {}
mapa_servicos_todos = {}
id_cliente_logado_na_agenda = None

def centralizar_janela(janela, largura, altura):
    largura_tela = janela.winfo_screenwidth()
    altura_tela = janela.winfo_screenheight()
    x = (largura_tela // 2) - (largura // 2)
    y = (altura_tela // 2) - (altura // 2)
    janela.geometry(f'{largura}x{altura}+{x}+{y}')

def carregar_dados_iniciais():
    global mapa_funcionarios, mapa_servicos_todos
    global combobox_servico_global, combobox_barbeiro_global

    funcionarios_db = listar_funcionarios()
    mapa_funcionarios = {f['nome_funcionario']: f['id_funcionario'] for f in funcionarios_db}
    if combobox_barbeiro_global:
        combobox_barbeiro_global['values'] = sorted(list(mapa_funcionarios.keys()))

    servicos_db = listar_servicos()
    mapa_servicos_todos = {s['nome_servico']: {"id": s['id_servico'], "duracao": s['duracao_estimada_minutos']} for s in servicos_db}
    if combobox_servico_global:
        combobox_servico_global['values'] = sorted(list(mapa_servicos_todos.keys()))
        combobox_servico_global.set('')

def on_barbeiro_selecionado(event):
    global combobox_barbeiro_global, combobox_servico_global, mapa_funcionarios, mapa_servicos_todos
    
    nome_barbeiro_selecionado = combobox_barbeiro_global.get()
    combobox_servico_global.set('') 

    if nome_barbeiro_selecionado and nome_barbeiro_selecionado in mapa_funcionarios:
        id_funcionario_selecionado = mapa_funcionarios[nome_barbeiro_selecionado]
        servicos_do_barbeiro_db = listar_servicos_por_funcionario(id_funcionario_selecionado)
        
        nomes_servicos_filtrados = sorted([s['nome_servico'] for s in servicos_do_barbeiro_db])
        combobox_servico_global['values'] = nomes_servicos_filtrados
        if not nomes_servicos_filtrados and combobox_servico_global.winfo_exists():
             messagebox.showinfo("Info", f"{nome_barbeiro_selecionado} não possui serviços cadastrados.", parent=combobox_servico_global.winfo_toplevel())
    else:
        combobox_servico_global['values'] = sorted(list(mapa_servicos_todos.keys()))

def agendar_novo_horario(root_para_messagebox):
    global combobox_servico_global, combobox_barbeiro_global, data_entry_global
    global combobox_hora_global, combobox_minuto_global, btn_agendar_global, mapa_servicos_todos
    global id_cliente_logado_na_agenda
    
    if id_cliente_logado_na_agenda is None:
        messagebox.showerror("Erro Crítico", "ID do cliente não encontrado. Por favor, reinicie.", parent=root_para_messagebox)
        return

    if btn_agendar_global:
        btn_agendar_global.config(state=tk.DISABLED)

    try:
        nome_servico_selecionado = combobox_servico_global.get()
        nome_barbeiro_selecionado = combobox_barbeiro_global.get()
        
        try:
            data_agendamento_dt_obj = data_entry_global.get_date()
            data_agendamento_str = data_agendamento_dt_obj.strftime('%Y-%m-%d')
        except AttributeError:
            messagebox.showerror("Erro de Data", "Por favor, selecione uma data válida.", parent=root_para_messagebox)
            return

        hora_selecionada = combobox_hora_global.get()
        minuto_selecionado = combobox_minuto_global.get()

        if not hora_selecionada or not minuto_selecionado:
            messagebox.showerror("Erro de Agendamento", "Por favor, selecione a hora e o minuto.", parent=root_para_messagebox)
            return
        
        hora_agendamento_str = f"{hora_selecionada}:{minuto_selecionado}"

        try:
            hora_obj = datetime.strptime(hora_agendamento_str, '%H:%M').time()
            datetime_agendamento = datetime.combine(data_agendamento_dt_obj, hora_obj)
        except ValueError:
            messagebox.showerror("Erro de Agendamento", "Hora inválida para combinação.", parent=root_para_messagebox)
            return

        agora = datetime.now()

        if datetime_agendamento < agora:
            messagebox.showerror("Erro de Agendamento", "Não é possível agendar para uma data ou hora no passado.", parent=root_para_messagebox)
            return
        
        if not nome_servico_selecionado or nome_servico_selecionado not in mapa_servicos_todos:
            messagebox.showerror("Erro de Agendamento", "Serviço inválido ou não selecionado.", parent=root_para_messagebox)
            return
        if not nome_barbeiro_selecionado or nome_barbeiro_selecionado not in mapa_funcionarios:
            messagebox.showerror("Erro de Agendamento", "Barbeiro inválido ou não selecionado.", parent=root_para_messagebox)
            return

        id_servico = mapa_servicos_todos[nome_servico_selecionado]["id"]
        id_funcionario = mapa_funcionarios[nome_barbeiro_selecionado]

        if verificar_conflito_horario(id_funcionario, data_agendamento_str, hora_agendamento_str, id_servico):
            messagebox.showerror("Conflito de Horário", f"{nome_barbeiro_selecionado} já possui um agendamento conflitante para {data_agendamento_dt_obj.strftime('%d/%m/%Y')} às {hora_agendamento_str}.", parent=root_para_messagebox)
            return

        if inserir_agendamento(id_cliente_logado_na_agenda, id_funcionario, id_servico, data_agendamento_str, hora_agendamento_str):
            messagebox.showinfo("Sucesso", "Agendamento realizado com sucesso!", parent=root_para_messagebox)
            combobox_servico_global.set('')
            combobox_hora_global.set(combobox_hora_global['values'][0] if combobox_hora_global['values'] else '')
            combobox_minuto_global.set(combobox_minuto_global['values'][0] if combobox_minuto_global['values'] else '')
            atualizar_tabela_agendamentos()
        else:
            messagebox.showerror("Erro de Agendamento", "Não foi possível realizar o agendamento.", parent=root_para_messagebox)
    finally:
        if btn_agendar_global:
            btn_agendar_global.config(state=tk.NORMAL)

def atualizar_tabela_agendamentos():
    global tree_agendamentos, id_cliente_logado_na_agenda
    if not tree_agendamentos: return
    if id_cliente_logado_na_agenda is None: return
    for item in tree_agendamentos.get_children():
        tree_agendamentos.delete(item)
    agendamentos_db = listar_agendamentos_para_display(id_cliente_logado_na_agenda)
    for ag_idx, ag in enumerate(agendamentos_db):
        tag = 'evenrow' if ag_idx % 2 == 0 else 'oddrow'
        tree_agendamentos.insert('', tk.END, values=(
            ag["id_agendamento"], ag["nome_cliente"], ag["nome_servico"],
            ag["nome_funcionario"], ag["data_formatada"], ag["hora_formatada"]
        ), tags=(tag,))

def excluir_agendamento_selecionado(root_para_messagebox):
    global tree_agendamentos
    if not tree_agendamentos: return
    selected_items = tree_agendamentos.selection()
    if not selected_items:
        messagebox.showwarning("Atenção", "Selecione um agendamento para excluir.", parent=root_para_messagebox)
        return
    item_selecionado = selected_items[0]
    valores_item = tree_agendamentos.item(item_selecionado, "values")
    if not valores_item:
        messagebox.showerror("Erro", "Não foi possível obter os dados do agendamento selecionado.", parent=root_para_messagebox)
        return
    try:
        ag_id = int(valores_item[0])
    except (IndexError, ValueError):
        messagebox.showerror("Erro", "ID do agendamento inválido ou não encontrado na seleção.", parent=root_para_messagebox)
        return
    confirmar = messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir o agendamento ID {ag_id}?", parent=root_para_messagebox)
    if confirmar:
        if deletar_agendamento(ag_id):
            messagebox.showinfo("Sucesso", "Agendamento excluído com sucesso.", parent=root_para_messagebox)
            atualizar_tabela_agendamentos()
        else:
            messagebox.showerror("Erro", "Não foi possível excluir o agendamento.", parent=root_para_messagebox)

def criar_interface(root_agenda, id_cliente_logado_param: int):
    global tree_agendamentos, combobox_servico_global, combobox_barbeiro_global, data_entry_global
    global combobox_hora_global, combobox_minuto_global, btn_agendar_global, id_cliente_logado_na_agenda

    id_cliente_logado_na_agenda = id_cliente_logado_param
    
    root_agenda.configure(bg=COR_FUNDO_JANELA)
    largura_agenda, altura_agenda = 850, 650
    centralizar_janela(root_agenda, largura_agenda, altura_agenda)

    style = ttk.Style(root_agenda)
    # Tente usar 'clam' ou 'alt' se 'default' não aplicar bem os estilos de fundo em botões/comboboxes
    # style.theme_use('clam') 

    style.configure('Light.TLabelframe', background=COR_FUNDO_JANELA, bordercolor="#B0B0B0") # Borda cinza claro
    style.configure('Light.TLabelframe.Label', foreground=COR_TEXTO_LABEL_DESTAQUE, background=COR_FUNDO_JANELA, font=FONTE_LABEL)

    style.configure('Light.TCombobox', font=FONTE_PADRAO, padding=2)
    style.map('Light.TCombobox', 
              fieldbackground=[('readonly', COR_FUNDO_WIDGETS)], 
              foreground=[('readonly', COR_TEXTO_WIDGETS)],
              selectbackground=[('readonly', COR_FUNDO_WIDGETS)], 
              selectforeground=[('readonly', COR_TEXTO_WIDGETS)],
              bordercolor=[('readonly', "#B0B0B0")], 
              arrowcolor=[('readonly', COR_TEXTO_GERAL)])
    
    root_agenda.option_add('*TCombobox*Listbox*Background', COR_FUNDO_WIDGETS)
    root_agenda.option_add('*TCombobox*Listbox*Foreground', COR_TEXTO_WIDGETS)
    root_agenda.option_add('*TCombobox*Listbox*font', FONTE_PADRAO)
    root_agenda.option_add('*TCombobox*Listbox*selectBackground', COR_BOTAO_PRIMARIO_BG) 
    root_agenda.option_add('*TCombobox*Listbox*selectForeground', COR_BOTAO_PRIMARIO_FG)

    style.configure('Agenda.TButton', font=FONTE_BOTAO, padding=(10,6))
    style.map('Agenda.TButton', 
              foreground=[('!disabled', COR_BOTAO_PRIMARIO_FG)],
              background=[('!disabled', COR_BOTAO_PRIMARIO_BG), ('active', COR_BOTAO_PRIMARIO_ACTIVE_BG)])
    
    style.configure('AgendaSec.TButton', font=FONTE_BOTAO, padding=(10,6))
    style.map('AgendaSec.TButton', 
            foreground=[('!disabled', COR_BOTAO_SECUNDARIO_FG)],
            background=[('!disabled', COR_BOTAO_SECUNDARIO_BG), ('active', COR_BOTAO_SECUNDARIO_ACTIVE_BG)])

    style.configure("Light.Treeview", 
                    background=COR_FUNDO_WIDGETS, 
                    foreground=COR_TEXTO_WIDGETS, 
                    fieldbackground=COR_FUNDO_WIDGETS,
                    font=FONTE_TREEVIEW_TEXT,
                    rowheight=25) 
    style.map("Light.Treeview",
              background=[('selected', COR_DESTAQUE_SELECAO_TREEVIEW_BG)],
              foreground=[('selected', COR_DESTAQUE_SELECAO_TREEVIEW_FG)])

    style.configure("Light.Treeview.Heading", 
                    font=FONTE_TREEVIEW_HEADING, 
                    background=COR_BOTAO_SECUNDARIO_BG, 
                    foreground=COR_BOTAO_SECUNDARIO_FG,
                    relief=tk.FLAT, 
                    padding=(5,5))
    
    style.configure('Light.Vertical.TScrollbar', 
                    background=COR_BOTAO_SECUNDARIO_BG,
                    troughcolor=COR_FUNDO_WIDGETS,
                    bordercolor=COR_FUNDO_JANELA,
                    arrowcolor=COR_TEXTO_GERAL)
    
    tree_agendamentos_tag_even_bg = COR_FUNDO_WIDGETS 
    tree_agendamentos_tag_odd_bg = "#E8E8E8" 

    nome_do_cliente_logado = buscar_nome_cliente_por_id(id_cliente_logado_na_agenda) or "Cliente"
    titulo = tk.Label(root_agenda, text=f"Agenda de Cortes - Cliente: {nome_do_cliente_logado}", font=FONTE_TITULO_JANELA, bg=COR_FUNDO_JANELA, fg=COR_TEXTO_LABEL_DESTAQUE)
    titulo.pack(pady=(20,15))

    frame_inputs = ttk.LabelFrame(root_agenda, text="Novo Agendamento", style='Light.TLabelframe')
    frame_inputs.pack(padx=20, pady=10, fill=tk.X)

    tk.Label(frame_inputs, text="Barbeiro:", font=FONTE_LABEL, bg=COR_FUNDO_JANELA, fg=COR_TEXTO_GERAL).grid(row=0, column=0, padx=10, pady=8, sticky=tk.W)
    combobox_barbeiro_global = ttk.Combobox(frame_inputs, state="readonly", width=25, font=FONTE_PADRAO, style='Light.TCombobox')
    combobox_barbeiro_global.grid(row=0, column=1, padx=5, pady=8, sticky=tk.EW)
    combobox_barbeiro_global.bind("<<ComboboxSelected>>", on_barbeiro_selecionado)

    tk.Label(frame_inputs, text="Serviço:", font=FONTE_LABEL, bg=COR_FUNDO_JANELA, fg=COR_TEXTO_GERAL).grid(row=0, column=2, padx=10, pady=8, sticky=tk.W)
    combobox_servico_global = ttk.Combobox(frame_inputs, state="readonly", width=25, font=FONTE_PADRAO, style='Light.TCombobox')
    combobox_servico_global.grid(row=0, column=3, columnspan=3, padx=5, pady=8, sticky=tk.EW)
    
    carregar_dados_iniciais()

    tk.Label(frame_inputs, text="Data:", font=FONTE_LABEL, bg=COR_FUNDO_JANELA, fg=COR_TEXTO_GERAL).grid(row=1, column=0, padx=10, pady=8, sticky=tk.W)
    data_entry_global = DateEntry(frame_inputs, width=15, font=FONTE_PADRAO,
                                  date_pattern='dd/mm/yyyy', locale='pt_BR',
                                  # Cores para o botão do DateEntry
                                  background=COR_AZUL_CLARINHO_DESTAQUE, 
                                  foreground=COR_AZUL_CLARINHO_TEXTO,    
                                  borderwidth=0, 
                                  relief=tk.FLAT,
                                  # Cores do calendário pop-up (tema claro)
                                  headersbackground=COR_FUNDO_JANELA, 
                                  headersforeground=COR_TEXTO_GERAL,
                                  selectbackground=COR_BOTAO_PRIMARIO_BG, 
                                  selectforeground=COR_BOTAO_PRIMARIO_FG,
                                  normalbackground=COR_FUNDO_WIDGETS, 
                                  normalforeground=COR_TEXTO_WIDGETS,
                                  weekendbackground=COR_FUNDO_WIDGETS, 
                                  weekendforeground=COR_TEXTO_WIDGETS,
                                  othermonthbackground="#E0E0E0", # Um pouco diferente para outros meses
                                  othermonthforeground="#757575"
                                 )
    data_entry_global.grid(row=1, column=1, padx=5, pady=8, sticky=tk.EW)
    
    try:
        data_entry_global._entry.config(bg=COR_FUNDO_WIDGETS, fg=COR_TEXTO_WIDGETS, 
                                    insertbackground=COR_CURSOR_ENTRY, relief=tk.FLAT,
                                    font=FONTE_PADRAO, borderwidth=1,
                                    disabledbackground=COR_FUNDO_WIDGETS, # Para quando estiver desabilitado
                                    readonlybackground=COR_FUNDO_WIDGETS # Para quando estiver readonly
                                    )
    except AttributeError:
        print("Aviso: Não foi possível estilizar o Entry interno do DateEntry diretamente via _entry.config.")

    tk.Label(frame_inputs, text="Hora:", font=FONTE_LABEL, bg=COR_FUNDO_JANELA, fg=COR_TEXTO_GERAL).grid(row=1, column=2, padx=10, pady=8, sticky=tk.W)
    horas_disponiveis = [f"{h:02d}" for h in range(8, 21)]
    combobox_hora_global = ttk.Combobox(frame_inputs, values=horas_disponiveis, state="readonly", width=5, font=FONTE_PADRAO, style='Light.TCombobox')
    combobox_hora_global.grid(row=1, column=3, padx=(0,0), pady=8, sticky=tk.W)
    if horas_disponiveis: combobox_hora_global.set(horas_disponiveis[0])

    tk.Label(frame_inputs, text="Min:", font=FONTE_LABEL, bg=COR_FUNDO_JANELA, fg=COR_TEXTO_GERAL).grid(row=1, column=4, padx=(5,0), pady=8, sticky=tk.W)
    minutos_disponiveis = [f"{m:02d}" for m in range(0, 60, 15)]
    combobox_minuto_global = ttk.Combobox(frame_inputs, values=minutos_disponiveis, state="readonly", width=5, font=FONTE_PADRAO, style='Light.TCombobox')
    combobox_minuto_global.grid(row=1, column=5, padx=(0,5), pady=8, sticky=tk.W)
    if minutos_disponiveis: combobox_minuto_global.set(minutos_disponiveis[0])

    frame_inputs.grid_columnconfigure(1, weight=1)
    frame_inputs.grid_columnconfigure(3, weight=1)

    btn_agendar_global = ttk.Button(root_agenda, text="Agendar Horário", style='Agenda.TButton', width=25,
                             command=lambda: agendar_novo_horario(root_agenda))
    btn_agendar_global.pack(pady=(10,10))

    frame_tabela = ttk.LabelFrame(root_agenda, text="Meus Agendamentos", style='Light.TLabelframe')
    frame_tabela.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

    colunas = ("ID", "Cliente", "Serviço", "Barbeiro", "Data", "Hora")
    tree_agendamentos = ttk.Treeview(frame_tabela, columns=colunas, show='headings', height=10, style="Light.Treeview")
    
    for col in colunas:
        tree_agendamentos.heading(col, text=col)
        if col == "ID": tree_agendamentos.column(col, width=40, minwidth=30, anchor=tk.CENTER, stretch=tk.NO)
        elif col == "Cliente": tree_agendamentos.column(col, width=200, minwidth=150, anchor=tk.W)
        elif col == "Serviço" or col == "Barbeiro": tree_agendamentos.column(col, width=180, minwidth=120, anchor=tk.W)
        else: tree_agendamentos.column(col, width=100, minwidth=80, anchor=tk.CENTER)
            
    tree_agendamentos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

    scrollbar = ttk.Scrollbar(frame_tabela, orient=tk.VERTICAL, command=tree_agendamentos.yview, style='Light.Vertical.TScrollbar')
    tree_agendamentos.configure(yscroll=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0,5), pady=5)
    
    tree_agendamentos.tag_configure('evenrow', background=tree_agendamentos_tag_even_bg, foreground=COR_TEXTO_WIDGETS)
    tree_agendamentos.tag_configure('oddrow', background=tree_agendamentos_tag_odd_bg, foreground=COR_TEXTO_WIDGETS)

    btn_excluir = ttk.Button(root_agenda, text="Excluir Agendamento", style='AgendaSec.TButton', width=25,
                             command=lambda: excluir_agendamento_selecionado(root_agenda))
    btn_excluir.pack(pady=(0,20))

    atualizar_tabela_agendamentos()

if __name__ == '__main__':
    root_teste = tk.Tk()
    root_teste.title("Teste Direto - Sistema de Agendamento")
    
    test_id_cliente_global_para_teste = 1 
    try:
        nome_cliente_teste = buscar_nome_cliente_por_id(test_id_cliente_global_para_teste)
        if nome_cliente_teste is None :
             from .database import inserir_cliente
             if not inserir_cliente("Cliente de Teste Agenda", "testeagenda@example.com", "11000000000", "testesenha"):
                 print("Falha ao criar cliente de teste.")
             else:
                 print(f"Cliente de teste para agenda.py pode ter sido criado. Verifique o ID no banco.")
                 print("Você pode precisar ajustar test_id_cliente_global_para_teste para um ID válido existente.")
        
        cliente_existente_para_teste = buscar_nome_cliente_por_id(test_id_cliente_global_para_teste)
        if cliente_existente_para_teste:
            criar_interface(root_teste, test_id_cliente_global_para_teste)
        else:
            tk.Label(root_teste, text=f"Cliente de teste com ID {test_id_cliente_global_para_teste} não encontrado ou não pôde ser criado.\nVerifique o banco e ajuste o teste.").pack(padx=20, pady=20)

    except ImportError as e:
        print(f"Erro de importação no teste de agenda.py: {e}")
        tk.Label(root_teste, text=f"Erro de importação: {e}.\nCertifique-se que database.py está na mesma pasta 'app'.").pack(padx=20, pady=20)
    except Exception as e:
        import traceback
        print(f"Erro ao iniciar teste de agenda.py: {e}")
        traceback.print_exc()
        tk.Label(root_teste, text=f"Erro ao iniciar teste: {e}").pack(padx=20, pady=20)
    
    root_teste.mainloop()