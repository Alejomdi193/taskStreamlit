import json
import sqlite3
from typing import List
import streamlit as st


DB_NAME = "tasks.db"

def initializeDatabase():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'pendiente'
            )
        """)

def addTask(title: str, description: str):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (title, description) VALUES (?, ?)", (title, description))
        conn.commit()

def listTask() -> List[dict]:
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, description, status FROM tasks")
        rows = cursor.fetchall()
    return [
        {"id": row[0], "title": row[1], "description": row[2], "status": row[3]} for row in rows
    ]

def taskComplete(task_id: int):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET status = 'completada' WHERE id = ?", (task_id,))
        conn.commit()

def deleteTask():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE status = 'completada'")
        conn.commit()

def saveTask(file_name: str):
    tasks = listTask()
    with open(file_name, "w") as file:
        json.dump(tasks, file, indent=4)

def loadTask(file_name: str):
    with open(file_name, "r") as file:
        tasks = json.load(file)
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        for task in tasks:
            cursor.execute(
                "INSERT INTO tasks (id, title, description, status) VALUES (?, ?, ?, ?) ON CONFLICT(id) DO NOTHING",
                (task["id"], task["title"], task["description"], task["status"]),
            )
        conn.commit()


initializeDatabase()
st.title("Gestion de Tareas")

menu = st.sidebar.selectbox("Menú", ["Agregar Tarea", "Listar Tareas", "Exportar Tareas", "Importar Tareas"])

if menu == "Agregar Tarea":
    st.header("Agregar Nueva Tarea")
    title = st.text_input("Titulo")
    description = st.text_area("Descripcion")
    if st.button("Agregar Tarea"):
        try:
            addTask(title, description)
            st.success("Tarea agregada correctamente.")
        except Exception as e:
            st.error(f"Error al agregar la tarea: {e}")

elif menu == "Listar Tareas":
    st.header("Lista de Tareas")
    tasks = listTask()
    for task in tasks:
        st.write(f"**{task['title']}** ({task['status']})")
        st.write(f"Descripción: {task['description']}")
        if task['status'] == 'pendiente':
            if st.button("Marcar como completada", key=f"complete_{task['id']}"):
                taskComplete(task['id'])
                st.experimental_set_query_params(dummy_param="1")
                st.experimental_rerun()
    if st.button("Eliminar tareas completadas"):
        deleteTask()
        st.experimental_rerun()

elif menu == "Exportar Tareas":
    st.header("Exportar Tareas")
    file_name = st.text_input("Nombre del archivo", "tareas.json")
    if st.button("Exportar"):
        try:
            saveTask(file_name)
            st.success(f"Tareas exportadas a {file_name}.")
        except Exception as e:
            st.error(f"Error al exportar las tareas: {e}")

elif menu == "Importar Tareas":
    st.header("Importar Tareas")
    uploaded_file = st.file_uploader("Selecciona un archivo JSON", type="json")
    if uploaded_file is not None:
        try:
            loadTask(uploaded_file.name)
            st.success("Tareas importadas correctamente")
        except Exception as e:
            st.error(f"Error al importar las tareas: {e}")
