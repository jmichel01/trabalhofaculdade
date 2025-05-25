import mysql.connector
from mysql.connector import errorcode
from datetime import date, time, datetime, timedelta

DB_CONFIG = {
    'host': "localhost",
    'user': "root",
    'password': "Michel@123",
    'database': "projetobarbearia"
}

def conectar():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Erro: Usuário ou senha do MySQL inválidos.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print(f"Erro: Banco de dados '{DB_CONFIG['database']}' não existe.")
        else:
            print(f"Erro ao conectar ao MySQL: {err}")
        return None

def inserir_cliente(nome: str, email: str, telefone: str, senha: str) -> bool:
    conn = None
    cursor = None
    try:
        conn = conectar()
        if not conn:
            return False
        cursor = conn.cursor()
        sql = "INSERT INTO tbl_clientes (nome_cliente, email_cliente, telefone_cliente, senha_cliente) VALUES (%s, %s, %s, %s)"
        val = (nome, email, telefone, senha)
        cursor.execute(sql, val)
        conn.commit()
        print(f"Cliente '{nome}' inserido com ID: {cursor.lastrowid}")
        return True
    except mysql.connector.Error as err:
        print(f"Erro ao inserir cliente: {err}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn and conn.is_connected():
            if cursor:
                cursor.close()
            conn.close()

def buscar_cliente_por_email(email: str):
    conn = None
    cursor = None
    try:
        conn = conectar()
        if not conn:
            return None
        cursor = conn.cursor(dictionary=True)
        sql = "SELECT id_cliente, nome_cliente, email_cliente, senha_cliente, telefone_cliente FROM tbl_clientes WHERE email_cliente = %s"
        cursor.execute(sql, (email,))
        cliente = cursor.fetchone()
        return cliente
    except mysql.connector.Error as err:
        print(f"Erro ao buscar cliente por email: {err}")
        return None
    finally:
        if conn and conn.is_connected():
            if cursor:
                cursor.close()
            conn.close()

def buscar_cliente_por_nome(nome_cliente: str):
    conn = None
    cursor = None
    try:
        conn = conectar()
        if not conn:
            return None
        cursor = conn.cursor(dictionary=True)
        sql = "SELECT id_cliente, nome_cliente, email_cliente, senha_cliente, telefone_cliente FROM tbl_clientes WHERE nome_cliente = %s"
        cursor.execute(sql, (nome_cliente,))
        cliente = cursor.fetchone()
        return cliente
    except mysql.connector.Error as err:
        print(f"Erro ao buscar cliente por nome: {err}")
        return None
    finally:
        if conn and conn.is_connected():
            if cursor:
                cursor.close()
            conn.close()

def buscar_nome_cliente_por_id(id_cliente: int) -> str | None:
    conn = None
    cursor = None
    try:
        conn = conectar()
        if not conn:
            return None
        cursor = conn.cursor(dictionary=True)
        sql = "SELECT nome_cliente FROM tbl_clientes WHERE id_cliente = %s"
        cursor.execute(sql, (id_cliente,))
        resultado = cursor.fetchone()
        if resultado:
            return resultado['nome_cliente']
        return None
    except mysql.connector.Error as err:
        print(f"Erro ao buscar nome do cliente por ID: {err}")
        return None
    finally:
        if conn and conn.is_connected():
            if cursor: 
                 cursor.close()
            conn.close()

def listar_funcionarios():
    conn = None
    cursor = None
    try:
        conn = conectar()
        if not conn:
            return []
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id_funcionario, nome_funcionario FROM tbl_funcionarios ORDER BY nome_funcionario")
        funcionarios = cursor.fetchall()
        return funcionarios
    except mysql.connector.Error as err:
        print(f"Erro ao listar funcionários: {err}")
        return []
    finally:
        if conn and conn.is_connected():
            if cursor:
                cursor.close()
            conn.close()

def listar_servicos():
    conn = None
    cursor = None
    try:
        conn = conectar()
        if not conn:
            return []
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id_servico, nome_servico, duracao_estimada_minutos, preco FROM tbl_servicos ORDER BY nome_servico")
        servicos = cursor.fetchall()
        return servicos
    except mysql.connector.Error as err:
        print(f"Erro ao listar serviços: {err}")
        return []
    finally:
        if conn and conn.is_connected():
            if cursor:
                cursor.close()
            conn.close()

def listar_servicos_por_funcionario(id_funcionario: int):
    conn = None
    cursor = None
    try:
        conn = conectar()
        if not conn:
            return []
        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT s.id_servico, s.nome_servico, s.duracao_estimada_minutos, s.preco
            FROM tbl_servicos s
            JOIN tbl_funcionario_especialidades fe ON s.id_servico = fe.id_servico
            WHERE fe.id_funcionario = %s
            ORDER BY s.nome_servico
        """
        cursor.execute(sql, (id_funcionario,))
        servicos_do_funcionario = cursor.fetchall()
        return servicos_do_funcionario
    except mysql.connector.Error as err:
        print(f"Erro ao listar serviços do funcionário: {err}")
        return []
    finally:
        if conn and conn.is_connected():
            if cursor:
                cursor.close()
            conn.close()

def listar_funcionarios_por_servico(id_servico: int):
    conn = None
    cursor = None
    try:
        conn = conectar()
        if not conn:
            return []
        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT f.id_funcionario, f.nome_funcionario
            FROM tbl_funcionarios f
            JOIN tbl_funcionario_especialidades fe ON f.id_funcionario = fe.id_funcionario
            WHERE fe.id_servico = %s
            ORDER BY f.nome_funcionario
        """
        cursor.execute(sql, (id_servico,))
        funcionarios_do_servico = cursor.fetchall()
        return funcionarios_do_servico
    except mysql.connector.Error as err:
        print(f"Erro ao listar funcionários para o serviço: {err}")
        return []
    finally:
        if conn and conn.is_connected():
            if cursor:
                cursor.close()
            conn.close()

def inserir_agendamento(id_cliente: int, id_funcionario: int, id_servico: int, data_ag: str, hora_ag: str, observacoes: str = None) -> bool:
    conn = None
    cursor = None
    try:
        conn = conectar()
        if not conn:
            return False
        cursor = conn.cursor()
        sql = """
            INSERT INTO tbl_agendamentos 
            (id_cliente, id_funcionario, id_servico, data_agendamento, hora_agendamento, observacoes) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        val = (id_cliente, id_funcionario, id_servico, data_ag, hora_ag, observacoes)
        cursor.execute(sql, val)
        conn.commit()
        print(f"Agendamento inserido com ID: {cursor.lastrowid}")
        return True
    except mysql.connector.Error as err:
        print(f"Erro ao inserir agendamento: {err}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn and conn.is_connected():
            if cursor:
                cursor.close()
            conn.close()

def listar_agendamentos_para_display(id_cliente_filtrar: int = None):
    conn = None
    cursor = None
    try:
        conn = conectar()
        if not conn:
            return []
        cursor = conn.cursor(dictionary=True)
        
        params = []
        sql = """
            SELECT 
                a.id_agendamento, 
                c.nome_cliente, 
                s.nome_servico, 
                f.nome_funcionario, 
                DATE_FORMAT(a.data_agendamento, '%d/%m/%Y') AS data_formatada,
                TIME_FORMAT(a.hora_agendamento, '%H:%i') AS hora_formatada
            FROM tbl_agendamentos a
            JOIN tbl_clientes c ON a.id_cliente = c.id_cliente
            JOIN tbl_funcionarios f ON a.id_funcionario = f.id_funcionario
            JOIN tbl_servicos s ON a.id_servico = s.id_servico
        """
        if id_cliente_filtrar is not None:
            sql += " WHERE a.id_cliente = %s"
            params.append(id_cliente_filtrar)
        
        sql += " ORDER BY a.data_agendamento, a.hora_agendamento"
        
        cursor.execute(sql, tuple(params))
        agendamentos = cursor.fetchall()
        return agendamentos
    except mysql.connector.Error as err:
        print(f"Erro ao listar agendamentos para display: {err}")
        return []
    finally:
        if conn and conn.is_connected():
            if cursor:
                cursor.close()
            conn.close()

def deletar_agendamento(id_agendamento: int) -> bool:
    conn = None
    cursor = None
    try:
        conn = conectar()
        if not conn:
            return False
        cursor = conn.cursor()
        sql = "DELETE FROM tbl_agendamentos WHERE id_agendamento = %s"
        cursor.execute(sql, (id_agendamento,))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Agendamento ID {id_agendamento} deletado.")
            return True
        else:
            print(f"Nenhum agendamento encontrado com ID {id_agendamento} para deletar.")
            return False
    except mysql.connector.Error as err:
        print(f"Erro ao deletar agendamento: {err}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn and conn.is_connected():
            if cursor:
                cursor.close()
            conn.close()

def verificar_conflito_horario(id_funcionario: int, data_ag_str: str, hora_inicio_novo_str: str, id_servico_novo: int) -> bool:
    conn = None
    cursor_servico = None
    cursor_existentes_local = None 
    
    print(f"\n--- Iniciando verificar_conflito_horario (LÓGICA PYTHON DETALHADA) ---")
    print(f"DEBUG: Params Entrada: id_func={id_funcionario}, data='{data_ag_str}', hora_novo='{hora_inicio_novo_str}', id_serv_novo={id_servico_novo}")

    try:
        conn = conectar()
        if not conn:
            print("DEBUG: Falha ao conectar.")
            return True 

        cursor_servico = conn.cursor(dictionary=True)
        cursor_servico.execute("SELECT nome_servico, duracao_estimada_minutos FROM tbl_servicos WHERE id_servico = %s", (id_servico_novo,))
        servico_info_novo = cursor_servico.fetchone()
        cursor_servico.close() 
        
        if not servico_info_novo:
            print(f"DEBUG: Serviço NOVO (ID {id_servico_novo}) não encontrado.")
            return True 

        duracao_novo_minutos = servico_info_novo['duracao_estimada_minutos']
        print(f"DEBUG: Serviço NOVO: Nome='{servico_info_novo['nome_servico']}', Duração={duracao_novo_minutos} min.")

        if duracao_novo_minutos is None or duracao_novo_minutos <= 0:
            print(f"DEBUG: Duração INVÁLIDA ({duracao_novo_minutos} min) para o serviço novo ID {id_servico_novo}.")
            return True
        
        try:
            data_novo_obj = datetime.strptime(data_ag_str, '%Y-%m-%d').date()
            hora_novo_obj = datetime.strptime(hora_inicio_novo_str, '%H:%M').time()
            n_start_dt = datetime.combine(data_novo_obj, hora_novo_obj)
            n_end_dt = n_start_dt + timedelta(minutes=duracao_novo_minutos)
            print(f"DEBUG: NOVO Agendamento: Início={n_start_dt}, Fim={n_end_dt}")
        except ValueError as e:
            print(f"DEBUG: Erro ao converter data/hora do NOVO agendamento: {e}")
            return True

        if cursor_existentes_local: 
            cursor_existentes_local.close()
        cursor_existentes_local = conn.cursor(dictionary=True)

        sql_existentes = """
            SELECT 
                a.id_agendamento, 
                a.data_agendamento, 
                a.hora_agendamento, 
                s.nome_servico as nome_servico_existente,
                s.duracao_estimada_minutos as duracao_existente_min
            FROM tbl_agendamentos a
            JOIN tbl_servicos s ON a.id_servico = s.id_servico 
            WHERE a.id_funcionario = %s AND a.data_agendamento = %s
        """
        params_existentes = tuple((id_funcionario, data_ag_str)) 
        
        print(f"DEBUG: Tipos de params_existentes: id_funcionario ({type(id_funcionario)}), data_ag_str ({type(data_ag_str)})")
        try:
            print(f"DEBUG: Query Ag. Existentes (mogrify): {cursor_existentes_local.mogrify(sql_existentes, params_existentes)}")
        except AttributeError:
             print(f"DEBUG: Query Ag. Existentes (template): {sql_existentes}")
             print(f"DEBUG: SQL Params para Ag. Existentes: {params_existentes}")

        cursor_existentes_local.execute(sql_existentes, params_existentes)
        agendamentos_existentes = cursor_existentes_local.fetchall()
        cursor_existentes_local.close()

        if not agendamentos_existentes:
            print("DEBUG: Nenhum agendamento existente para este funcionário neste dia. Nenhum conflito.")
            return False

        print(f"DEBUG: Agendamentos existentes encontrados ({len(agendamentos_existentes)}):")

        for ag_existente in agendamentos_existentes:
            print(f"  Checando contra Ag. ID existente: {ag_existente['id_agendamento']}")
            
            duracao_existente_min = ag_existente['duracao_existente_min']
            if duracao_existente_min is None or duracao_existente_min <= 0:
                print(f"  DEBUG: Ag. ID {ag_existente['id_agendamento']} existente (serviço '{ag_existente['nome_servico_existente']}') tem duração inválida ({duracao_existente_min} min). Pulando esta verificação.")
                continue

            try:
                data_existente_obj = ag_existente['data_agendamento']
                
                if isinstance(ag_existente['hora_agendamento'], timedelta):
                    total_seconds = int(ag_existente['hora_agendamento'].total_seconds())
                    h = total_seconds // 3600
                    m = (total_seconds % 3600) // 60
                    s = total_seconds % 60
                    hora_existente_obj = time(h, m, s)
                elif isinstance(ag_existente['hora_agendamento'], time):
                     hora_existente_obj = ag_existente['hora_agendamento']
                else: 
                    hora_existente_obj = datetime.strptime(str(ag_existente['hora_agendamento']), '%H:%M:%S').time()

                e_start_dt = datetime.combine(data_existente_obj, hora_existente_obj)
                e_end_dt = e_start_dt + timedelta(minutes=duracao_existente_min)
                print(f"  DEBUG: Ag. EXISTENTE ID {ag_existente['id_agendamento']}: Início={e_start_dt}, Fim={e_end_dt} (Serviço: '{ag_existente['nome_servico_existente']}', Duração: {duracao_existente_min} min)")
            except Exception as e_conv:
                print(f"  DEBUG: Erro ao converter data/hora do Ag. EXISTENTE ID {ag_existente['id_agendamento']}: {e_conv}")
                continue

            cond1_n_start_lt_e_end = n_start_dt < e_end_dt
            cond2_n_end_gt_e_start = n_end_dt > e_start_dt
            
            print(f"  DEBUG: Comparando NOVO ({n_start_dt} - {n_end_dt}) com EXISTENTE ({e_start_dt} - {e_end_dt})")
            print(f"    Cond1 (Novo_Início < Fim_Existente): {n_start_dt} < {e_end_dt}  => {cond1_n_start_lt_e_end}")
            print(f"    Cond2 (Novo_Fim    > Início_Existente): {n_end_dt} > {e_start_dt}  => {cond2_n_end_gt_e_start}")

            if cond1_n_start_lt_e_end and cond2_n_end_gt_e_start:
                print(f"  DEBUG: *** CONFLITO DETECTADO com Ag. ID {ag_existente['id_agendamento']} ***")
                return True
        
        print("DEBUG: NENHUM conflito detectado após checar todos os existentes com lógica Python.")
        return False 

    except mysql.connector.Error as err:
        print(f"ERRO SQL em verificar_conflito_horario (etapa de busca): {err}") 
        return True
    except Exception as e_geral:
        print(f"ERRO GERAL INESPERADO em verificar_conflito_horario: {e_geral}")
        return True
    finally:
        print("--- Finalizando verificar_conflito_horario (LÓGICA PYTHON) ---")
        # cursor_servico foi fechado
        # cursor_existentes_local foi fechado
        if conn and conn.is_connected():
            conn.close()

if __name__ == '__main__':
    print("Testando funções do database.py...")
    pass