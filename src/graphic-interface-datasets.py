import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import sqlite3
import os

def cargar_archivo():
    # Abrir cuadro de diálogo para seleccionar archivo
    archivo = filedialog.askopenfilename(
        title="Seleccionar archivo",
        filetypes=[
            ("Archivos soportados", "*.csv *.xls *.xlsx *.sqlite *.db"),
            ("Todos los archivos", "*.*")
        ]
    )
    if not archivo:
        return

    lbl_ruta.config(text=archivo)
    try:
        # Detectar tipo de archivo y cargarlo
        if archivo.endswith(".csv"):
            df = pd.read_csv(archivo)
        elif archivo.endswith((".xls", ".xlsx")):
            df = pd.read_excel(archivo)
        elif archivo.endswith((".sqlite", ".db")):
            conn = sqlite3.connect(archivo)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tablas = [t[0] for t in cursor.fetchall()]
            if not tablas:
                raise ValueError("No se encontraron tablas en la base de datos.")
            tabla = tablas[0]
            df = pd.read_sql_query(f"SELECT * FROM {tabla}", conn)
            conn.close()
        else:
            raise ValueError("Formato de archivo no soportado.")

        mostrar_datos(df)
        messagebox.showinfo("Éxito", "Datos cargados correctamente.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo cargar el archivo:\n{e}")

def mostrar_datos(df):
    # Limpiar tabla previa
    for col in tree["columns"]:
        tree.heading(col, text="")
    tree.delete(*tree.get_children())

    # Configurar nuevas columnas
    columnas = list(df.columns)
    tree["columns"] = columnas
    for col in columnas:
        tree.heading(col, text=col)
        tree.column(col, width=120, anchor="w")

    # Insertar datos (máximo 1000 filas para mantener fluidez)
    for i, fila in df.head(1000).iterrows():
        tree.insert("", "end", values=list(fila))

# ---- Interfaz gráfica ----
ventana = tk.Tk()
ventana.title("Visor de Datasets")
ventana.geometry("900x600")

frame_top = ttk.Frame(ventana, padding=10)
frame_top.pack(fill="x")

btn_cargar = ttk.Button(frame_top, text="Abrir archivo", command=cargar_archivo)
btn_cargar.pack(side="left")

lbl_ruta = ttk.Label(frame_top, text="Ningún archivo seleccionado", width=100, anchor="w")
lbl_ruta.pack(side="left", padx=10)

# Tabla con scroll
frame_tabla = ttk.Frame(ventana)
frame_tabla.pack(fill="both", expand=True, padx=10, pady=10)

tree = ttk.Treeview(frame_tabla, show="headings")
scroll_y = ttk.Scrollbar(frame_tabla, orient="vertical", command=tree.yview)
scroll_x = ttk.Scrollbar(frame_tabla, orient="horizontal", command=tree.xview)
tree.configure(yscroll=scroll_y.set, xscroll=scroll_x.set)

tree.grid(row=0, column=0, sticky="nsew")
scroll_y.grid(row=0, column=1, sticky="ns")
scroll_x.grid(row=1, column=0, sticky="ew")

frame_tabla.rowconfigure(0, weight=1)
frame_tabla.columnconfigure(0, weight=1)

ventana.mainloop()
