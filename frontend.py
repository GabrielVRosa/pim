import os
import json
import ctypes
from tkinter import *
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt

#caminho do arquivo de dados
json_path = os.path.join(os.path.dirname(__file__), "dados_alunos.json")

#função: carregar dados do JSON (ou criar novo)
def carregar_dados_json():
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {"alunos": []}  # Estrutura inicial

#função: salvar dados no JSON
def salvar_dados_json(dados):
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

#carrega dados atuais
dados_json = carregar_dados_json()


#caminho completo da DLL (backend.dll)
dll = os.path.join(os.path.dirname(__file__), "backend.dll")
if not os.path.exists(dll):
    messagebox.showerror("Erro", f"DLL não encontrada: {dll}")
    raise SystemExit(1)

backend = ctypes.CDLL(dll)
backend.init_backend()

#define tipos de argumentos da DLL
backend.add_user.argtypes = [ctypes.c_char_p]*4
backend.add_student.argtypes = [ctypes.c_char_p]*4
backend.register_grade.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_double]
backend.check_user.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
backend.get_student_grades.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
backend.get_student_name.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
backend.get_professor_subject.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
backend.check_student.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
backend.get_class_grades.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]


#funções de Placeholder e GUI
def placeholder(entry, txt):
    entry.insert(0, txt)
    entry.config(fg="gray")

    def foco_in(e):
        if entry.get() == txt:
            entry.delete(0, END)
            entry.config(fg="black")

    def foco_out(e):
        if not entry.get():
            entry.insert(0, txt)
            entry.config(fg="gray")

    entry.bind("<FocusIn>", foco_in)
    entry.bind("<FocusOut>", foco_out)


root = Tk()
root.title("Sistema de Notas")
root.geometry("900x600")

tabs = ttk.Notebook(root)
tabs.pack(fill=BOTH, expand=True)

tab_login = Frame(tabs)
tabs.add(tab_login, text="Login")

login = Entry(tab_login)
login.pack(pady=5)
placeholder(login, "Login ou RA")

senha = Entry(tab_login, show="*")
senha.pack(pady=5)
placeholder(senha, "Senha")

admin_tab = None
prof_tab = None
aluno_tab = None

def sair(tab):
    global admin_tab, prof_tab, aluno_tab
    tabs.forget(tab)
    if tab == admin_tab: admin_tab = None
    elif tab == prof_tab: prof_tab = None
    elif tab == aluno_tab: aluno_tab = None


#ala admin - salva alunos no JSON
def aba_admin():
    global admin_tab
    if admin_tab: return

    admin_tab = Frame(tabs)
    tabs.add(admin_tab, text="Admin")
    tabs.select(admin_tab)

    Button(admin_tab, text="Sair", command=lambda: sair(admin_tab)).pack(pady=5)

    Label(admin_tab, text="Cadastrar Professor").pack()
    user = Entry(admin_tab); user.pack(); placeholder(user, "Login do professor")
    pw = Entry(admin_tab, show="*"); pw.pack(); placeholder(pw, "Senha do professor")
    mat = Entry(admin_tab); mat.pack(); placeholder(mat, "Matéria")

    def add_prof():
        backend.add_user(user.get().encode(), pw.get().encode(), b"teacher", mat.get().encode())
        messagebox.showinfo("OK", "Professor cadastrado")

    Button(admin_tab, text="Salvar", command=add_prof).pack(pady=5)

    Label(admin_tab, text="Cadastrar Aluno").pack()
    ra = Entry(admin_tab); ra.pack(); placeholder(ra, "RA")
    nome = Entry(admin_tab); nome.pack(); placeholder(nome, "Nome")
    spw = Entry(admin_tab, show="*"); spw.pack(); placeholder(spw, "Senha")
    turma = Entry(admin_tab); turma.pack(); placeholder(turma, "Turma")

    def add_aluno():
        backend.add_student(ra.get().encode(), nome.get().encode(), spw.get().encode(), turma.get().encode())

        #atualizador do JSON
        dados_json["alunos"].append({
            "ra": ra.get(),
            "nome": nome.get(),
            "senha": spw.get(),
            "turma": turma.get(),
            "notas": {}
        })
        salvar_dados_json(dados_json)
        messagebox.showinfo("OK", f"Aluno {nome.get()} cadastrado e salvo em JSON")

    Button(admin_tab, text="Salvar", command=add_aluno).pack(pady=5)


#ala prof - salva notas no JSON
def aba_prof(materia):
    global prof_tab
    if prof_tab: return

    prof_tab = Frame(tabs)
    tabs.add(prof_tab, text="Professor")
    tabs.select(prof_tab)

    Button(prof_tab, text="Sair", command=lambda: sair(prof_tab)).pack(pady=5)
    Label(prof_tab, text=f"Matéria: {materia}", font=("Arial", 12, "bold")).pack(pady=5)
    Label(prof_tab, text="Registrar Nota").pack()

    ra = Entry(prof_tab); ra.pack(); placeholder(ra, "RA do aluno")
    nome_lbl = Label(prof_tab, text=""); nome_lbl.pack()

    def atualiza_nome(e=None):
        buf = ctypes.create_string_buffer(50)
        backend.get_student_name(ra.get().encode(), buf, 50)
        nome = buf.value.decode()
        nome_lbl.config(text=f"Aluno: {nome}" if nome else "Aluno não encontrado")

    ra.bind("<FocusOut>", atualiza_nome)

    nota = Entry(prof_tab); nota.pack(); placeholder(nota, "Nota (ex: 8.5)")
    turma_prof = Entry(prof_tab); turma_prof.pack(pady=5)
    placeholder(turma_prof, "Digite a turma (ex: TurmaA)")

    def salvar():
        try:
            val = float(nota.get())
            backend.register_grade(ra.get().encode(), materia.encode(), val)

            #atualizador do json
            for aluno in dados_json["alunos"]:
                if aluno["ra"] == ra.get():
                    aluno["notas"][materia] = val
                    break
            salvar_dados_json(dados_json)

            messagebox.showinfo("OK", "Nota registrada e salva no JSON")
        except ValueError:
            messagebox.showwarning("Erro", "Digite uma nota válida")

    Button(prof_tab, text="Salvar Nota", command=salvar).pack(pady=5)


    def gerar_grafico():
        turma = turma_prof.get().strip().encode()
        buf = ctypes.create_string_buffer(5000)
        backend.get_class_grades(turma, buf, 5000)
        dados = buf.value.decode()

        if not dados:
            messagebox.showwarning("Aviso", "Nenhuma nota registrada para essa turma!")
            return

        medias = {}
        for linha in dados.strip(";").split(";"):
            if not linha.strip(): continue
            ra_aluno, notas = linha.split(":", 1)
            notas_split = notas.strip(";").split(";")
            soma = 0; cont = 0
            for n in notas_split:
                if ":" in n:
                    mat, val = n.split(":")
                    soma += float(val)
                    cont += 1
            if cont > 0:
                medias[ra_aluno] = soma / cont

        if not medias:
            messagebox.showwarning("Aviso", "Nenhuma média encontrada!")
            return

        plt.bar(medias.keys(), medias.values())
        plt.title(f"Média dos Alunos ({turma_prof.get()})")
        plt.xlabel("RA dos Alunos")
        plt.ylabel("Média")
        plt.show()

    Button(prof_tab, text="Gerar Gráfico da Turma",
           command=gerar_grafico, bg="#4CAF50", fg="white").pack(pady=10)


#ala do aluno - mostra notas salvas no json
def aba_aluno(ra):
    global aluno_tab
    if aluno_tab: return

    aluno_tab = Frame(tabs)
    tabs.add(aluno_tab, text="Minhas Notas")
    tabs.select(aluno_tab)
    Button(aluno_tab, text="Sair", command=lambda: sair(aluno_tab)).pack(pady=5)

    aluno_dados = next((a for a in dados_json["alunos"] if a["ra"] == ra), None)
    if aluno_dados:
        Label(aluno_tab, text=f"Aluno: {aluno_dados['nome']}", font=("Arial", 14)).pack(pady=10)

        if aluno_dados["notas"]:
            soma = sum(aluno_dados["notas"].values())
            cont = len(aluno_dados["notas"])
            for mat, val in aluno_dados["notas"].items():
                Label(aluno_tab, text=f"{mat}: {val}").pack()
            Label(aluno_tab, text=f"Média: {soma/cont:.2f}", font=("Arial", 12, "bold")).pack(pady=10)
        else:
            Label(aluno_tab, text="Sem notas").pack()
    else:
        Label(aluno_tab, text="Aluno não encontrado").pack()


#func login
def login_sistema():
    user = login.get().strip()
    pw = senha.get().strip()
    buf = ctypes.create_string_buffer(50)

    backend.check_user(user.encode(), pw.encode(), buf, 50)
    tipo = buf.value.decode()

    if tipo == "admin":
        aba_admin()
    elif tipo == "teacher":
        mat_buf = ctypes.create_string_buffer(50)
        backend.get_professor_subject(user.encode(), mat_buf, 50)
        aba_prof(mat_buf.value.decode())
    elif backend.check_student(user.encode(), pw.encode()):
        aba_aluno(user)
    else:
        messagebox.showerror("Erro", "Login inválido")


Button(tab_login, text="Entrar", command=login_sistema).pack(pady=10)
root.mainloop()