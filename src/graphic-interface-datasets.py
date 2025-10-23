import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import sqlite3
import os


# Función para cargar archivos

def load_data(file_path):
    try:
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        elif file_path.endswith((".xls", ".xlsx")):
            df = pd.read_excel(file_path)
        elif file_path.endswith((".sqlite", ".db")):
            conn = sqlite3.connect(file_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            if not tables:
                raise ValueError("No se encontraron tablas en la base de datos SQLite.")
            table_name = tables[0][0]
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
            conn.close()
        else:
            raise ValueError("Formato de archivo no válido.")
        return df

    except FileNotFoundError:
        messagebox.showerror("Error", "Archivo no encontrado.")
    except pd.errors.EmptyDataError:
        messagebox.showerror("Error", "El archivo está vacío.")
    except sqlite3.OperationalError:
        messagebox.showerror("Error", "No se pudo leer la base de datos SQLite.")
    except ValueError as e:
        messagebox.showerror("Error", str(e))
    except Exception as e:
        messagebox.showerror("Error inesperado", f"Ocurrió un problema:\n{e}")
    return None



# Interfaz gráfica (Tkinter)

def abrir_archivo():
    ruta = filedialog.askopenfilename(
        title="Seleccionar archivo",
        filetypes=[
            ("Archivos soportados", "*.csv *.xls *.xlsx *.sqlite *.db"),
            ("Todos los archivos", "*.*")
        ]
    )
    if not ruta:
        return

    entrada_texto.config(state="normal")
    entrada_texto.delete(0, tk.END)
    entrada_texto.insert(0, ruta)
    entrada_texto.config(state="readonly")

    df = load_data(ruta)
    if df is not None:
        mostrar_tabla(df)
        messagebox.showinfo("Éxito", "Datos cargados correctamente.")

def mostrar_tabla(df):
    # Limpiar tabla anterior
    for col in tree["columns"]:
        tree.heading(col, text="")
    tree.delete(*tree.get_children())

    # Configurar nuevas columnas
    columnas = list(df.columns)
    tree["columns"] = columnas
    for col in columnas:
        tree.heading(col, text=col)
        tree.column(col, width=120, anchor="w")

    # Insertar hasta 1000 filas para mantener fluidez
    for _, fila in df.head(1000).iterrows():
        tree.insert("", "end", values=list(fila))


# Crear ventana principal
ventana = tk.Tk()
ventana.title("Visor de Archivos de Datos")
ventana.geometry("900x600")

# Botón superior
boton = tk.Button(ventana, text="Abrir archivo", command=lambda: [abrir_archivo()])
boton.pack(pady=10)

# Cuadro de texto (ruta del archivo)
entrada_texto = tk.Entry(ventana, width=80, state="readonly")
entrada_texto.pack(pady=10)

# Marco para tabla
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
