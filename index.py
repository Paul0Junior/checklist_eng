import streamlit as st
import sqlite3
from datetime import datetime
import hashlib

# Classe para representar uma tarefa individual
class Task:
    def __init__(self, description, theme_id):
        self.description = description
        self.theme_id = theme_id
        self.completed = None  # None: Não marcado, True: Realizado, False: Não realizado
        self.observation = ""
        self.question_id = self.get_question_id()

    def get_question_id(self):
        conn = sqlite3.connect('checklist.db')
        cursor = conn.cursor()
        cursor.execute("SELECT question_id FROM questions WHERE question_description = ? AND theme_id = ?", (self.description, self.theme_id))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    def mark_realized(self):
        self.completed = True

    def mark_not_realized(self):
        self.completed = False

    def reset_completion(self):
        self.completed = None

    def __str__(self):
        status = 'Realizado' if self.completed else 'Não realizado' if self.completed is not None else 'Pendente'
        return f"{self.description} - {status} - {self.observation}"

# Classe para representar uma seção do checklist
class Section:
    def __init__(self, title, theme_id):
        self.title = title
        self.theme_id = theme_id
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)

# Classe para representar o checklist completo
class Checklist:
    def __init__(self, title):
        self.title = title
        self.sections = []

    def add_section(self, section):
        self.sections.append(section)

# Função para criar as tabelas no banco de dados
def create_tables(conn):
    with conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS checklist_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                theme_id INTEGER,
                question_id INTEGER,
                datetime TEXT,
                username TEXT,
                observation TEXT,
                completed BOOLEAN,
                FOREIGN KEY (theme_id) REFERENCES themes(theme_id),
                FOREIGN KEY (question_id) REFERENCES questions(question_id)
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                question_id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_description TEXT,
                theme_id INTEGER,
                FOREIGN KEY (theme_id) REFERENCES themes(theme_id)
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS themes (
                theme_id INTEGER PRIMARY KEY AUTOINCREMENT,
                theme_title TEXT
            )
        ''')

# Função para popular a tabela de perguntas
def populate_questions(conn):
    with conn:
        themes = [
            (1, "Validação de Jobs"),
            (2, "Validação de Tabelas"),
            (3, "Espaço em Disco de Servidores de Coleta e Banco de Dados"),
            (4, "Reinicialização de Serviços")
        ]
        conn.executemany("INSERT OR IGNORE INTO themes (theme_id, theme_title) VALUES (?, ?)", themes)

        questions = [
            ("Confirmar a execução bem-sucedida de todos os jobs agendados.", 1),
            ("Identificar e documentar qualquer job que falhou.", 1),
            ("Reexecutar jobs falhados, se necessário.", 1),
            ("Analisar logs em busca de erros ou avisos.", 1),
            ("Documentar qualquer anomalia encontrada nos logs.", 1),

            ("Realizar consultas de verificação para assegurar a integridade dos dados.", 2),
            ("Comparar contagens de registros com benchmarks esperados.", 2),
            ("Confirmar se as tabelas foram atualizadas conforme esperado.", 2),
            ("Documentar qualquer discrepância nas atualizações.", 2),
            ("Garantir que os índices e chaves primárias/estrangeiras estejam intactos.", 2),
            ("Reindexar tabelas, se necessário.", 2),

            ("Verificar o espaço em disco disponível em servidores de coleta.", 3),
            ("Verificar o espaço em disco disponível em servidores de banco de dados.", 3),
            ("Registrar o uso atual de espaço em disco.", 3),
            ("Identificar diretórios ou arquivos que ocupam mais espaço.", 3),
            ("Limpar logs antigos ou arquivos temporários.", 3),
            ("Arquivar ou mover dados antigos para armazenamento externo.", 3),

            ("Confirmar se todos os serviços críticos estão operacionais.", 4),
            ("Identificar qualquer serviço que necessite de reinicialização.", 4),
            ("Reinicializar serviços de coleta de dados.", 4),
            ("Reinicializar serviços de banco de dados.", 4),
            ("Reinicializar serviços de aplicação.", 4),
            ("Confirmar que os serviços reiniciados estão operacionais.", 4),
            ("Verificar logs de inicialização para possíveis erros.", 4)
        ]
        conn.executemany("INSERT OR IGNORE INTO questions (question_description, theme_id) VALUES (?, ?)", questions)

# Função para hashear a senha
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Função para verificar o login
def login_user(conn, username, password):
    hashed_password = hash_password(password)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_password))
    return cursor.fetchone()

# Função para registrar um novo usuário
def register_user(conn, username, password):
    hashed_password = hash_password(password)
    with conn:
        try:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            return True
        except sqlite3.IntegrityError:
            return False

# Função principal para configurar o checklist e iniciar a aplicação
def main():
    st.title("Modelo de Check-list Diário para Processos de Engenharia")

    conn = sqlite3.connect('checklist.db')  # Conecta ao banco de dados
    create_tables(conn)  # Cria as tabelas no banco de dados se não existirem
    populate_questions(conn)  # Popula a tabela de perguntas com dados fictícios

    # Sistema de login
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = ""

    if st.session_state.logged_in:
        checklist = Checklist("Modelo de Check-list Diário para Processos de Engenharia")

        # Validação de Jobs
        section_jobs = Section("1. Validação de Jobs", 1)
        section_jobs.add_task(Task("Confirmar a execução bem-sucedida de todos os jobs agendados.", section_jobs.theme_id))
        section_jobs.add_task(Task("Identificar e documentar qualquer job que falhou.", section_jobs.theme_id))
        section_jobs.add_task(Task("Reexecutar jobs falhados, se necessário.", section_jobs.theme_id))
        section_jobs.add_task(Task("Analisar logs em busca de erros ou avisos.", section_jobs.theme_id))
        section_jobs.add_task(Task("Documentar qualquer anomalia encontrada nos logs.", section_jobs.theme_id))
        checklist.add_section(section_jobs)

        # Validação de Tabelas
        section_tables = Section("2. Validação de Tabelas", 2)
        section_tables.add_task(Task("Realizar consultas de verificação para assegurar a integridade dos dados.", section_tables.theme_id))
        section_tables.add_task(Task("Comparar contagens de registros com benchmarks esperados.", section_tables.theme_id))
        section_tables.add_task(Task("Confirmar se as tabelas foram atualizadas conforme esperado.", section_tables.theme_id))
        section_tables.add_task(Task("Documentar qualquer discrepância nas atualizações.", section_tables.theme_id))
        section_tables.add_task(Task("Garantir que os índices e chaves primárias/estrangeiras estejam intactos.", section_tables.theme_id))
        section_tables.add_task(Task("Reindexar tabelas, se necessário.", section_tables.theme_id))
        checklist.add_section(section_tables)

        # Espaço em Disco
        section_disk = Section("3. Espaço em Disco de Servidores de Coleta e Banco de Dados", 3)
        section_disk.add_task(Task("Verificar o espaço em disco disponível em servidores de coleta.", section_disk.theme_id))
        section_disk.add_task(Task("Verificar o espaço em disco disponível em servidores de banco de dados.", section_disk.theme_id))
        section_disk.add_task(Task("Registrar o uso atual de espaço em disco.", section_disk.theme_id))
        section_disk.add_task(Task("Identificar diretórios ou arquivos que ocupam mais espaço.", section_disk.theme_id))
        section_disk.add_task(Task("Limpar logs antigos ou arquivos temporários.", section_disk.theme_id))
        section_disk.add_task(Task("Arquivar ou mover dados antigos para armazenamento externo.", section_disk.theme_id))
        checklist.add_section(section_disk)

        # Reinicialização de Serviços
        section_services = Section("4. Reinicialização de Serviços", 4)
        section_services.add_task(Task("Confirmar se todos os serviços críticos estão operacionais.", section_services.theme_id))
        section_services.add_task(Task("Identificar qualquer serviço que necessite de reinicialização.", section_services.theme_id))
        section_services.add_task(Task("Reinicializar serviços de coleta de dados.", section_services.theme_id))
        section_services.add_task(Task("Reinicializar serviços de banco de dados.", section_services.theme_id))
        section_services.add_task(Task("Reinicializar serviços de aplicação.", section_services.theme_id))
        section_services.add_task(Task("Confirmar que os serviços reiniciados estão operacionais.", section_services.theme_id))
        section_services.add_task(Task("Verificar logs de inicialização para possíveis erros.", section_services.theme_id))
        checklist.add_section(section_services)

        tasks = []
        for section in checklist.sections:
            st.header(section.title)
            for task in section.tasks:
                task_status = st.radio(f"{task.description}", ("Pendente", "Realizado", "Não realizado"), index=0)
                if task_status == "Realizado":
                    task.mark_realized()
                elif task_status == "Não realizado":
                    task.mark_not_realized()
                else:
                    task.reset_completion()

                task.observation = st.text_input(f"Observação para '{task.description}'", key=f"obs_{task.description}")
                if st.button(f"Enviar", key=f"btn_{task.description}"):
                    if task.completed is None:
                        st.warning("Por favor, marque se a tarefa foi realizada ou não realizada.")
                    elif task.completed is False and not task.observation:
                        st.warning("Por favor, adicione uma observação para as tarefas não realizadas.")
                    else:
                        with conn:
                            conn.execute('''
                                INSERT INTO checklist_responses (theme_id, question_id, datetime, username, observation, completed)
                                VALUES (?, ?, ?, ?, ?, ?)
                            ''', (task.theme_id, task.question_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), st.session_state.username, task.observation, task.completed))
                        st.success(f"Tarefa '{task.description}' enviada com sucesso!")
                tasks.append(task)

        if st.button("Finalizar Checklist"):
            with conn:
                for section in checklist.sections:
                    for task in section.tasks:
                        conn.execute('''
                            INSERT INTO checklist_responses (theme_id, question_id, datetime, username, observation, completed)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (task.theme_id, task.question_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), st.session_state.username, task.observation, task.completed))
            summary = [f"Usuário: {st.session_state.username}\n"]
            for section in checklist.sections:
                summary.append(f"\n{section.title}\n" + '-' * len(section.title))
                for task in section.tasks:
                    summary.append(str(task))
            st.info("\n".join(summary))
            st.success("Checklist finalizado com sucesso!")
    else:
        st.sidebar.title("Login")
        username = st.sidebar.text_input("Usuário")
        password = st.sidebar.text_input("Senha", type="password")
        if st.sidebar.button("Entrar"):
            user = login_user(conn, username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Login realizado com sucesso!")
            else:
                st.error("Usuário ou senha incorretos.")

        st.sidebar.title("Registrar")
        new_username = st.sidebar.text_input("Novo usuário")
        new_password = st.sidebar.text_input("Nova senha", type="password")
        if st.sidebar.button("Registrar"):
            if register_user(conn, new_username, new_password):
                st.success("Usuário registrado com sucesso! Agora você pode fazer login.")
            else:
                st.error("Usuário já existe. Tente outro nome de usuário.")

if __name__ == "__main__":
    main()
