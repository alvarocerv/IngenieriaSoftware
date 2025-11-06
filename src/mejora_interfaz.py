import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import sqlite3
import os
from sklearn.model_selection import train_test_split

# Importamos las funciones de los otros archivos
from gui_column_selection import lanzar_selector
from manejo_inexistentes import manejo_datos_inexistentes
from data_separation import iniciar_separacion, train_df, test_df
from model_creation import iniciar_creacion_modelo
# --- Variables Globales ---
# Necesitamos que el DF original y el visor de la tabla
# sean accesibles por las funciones de control.
df_original = None
tree = None
frame_pasos_container = None


# --- Funciones de Carga y Visualización ---

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
    except Exception as e:
        messagebox.showerror("Error al cargar", f"Ocurrió un problema:\n{e}")
        return None


def mostrar_tabla(df):
    global tree
    # Limpiar tabla anterior
    tree.delete(*tree.get_children())

    # Configurar nuevas columnas
    columnas = list(df.columns)
    tree["columns"] = columnas
    tree.heading("#0", text="", anchor="w")
    tree.column("#0", width=0, stretch=tk.NO)

    for col in columnas:
        tree.heading(col, text=col)
        tree.column(col, width=120, anchor="w")

    # Insertar hasta 1000 filas
    for i, fila in df.head(1000).iterrows():
        tree.insert("", "end", values=list(fila))


# --- Funciones de Control (El "Pegamento") ---

def iniciar_paso_1():
    """Llama al módulo de selección de columnas."""
    global df_original, frame_pasos_container
    if df_original is not None:
        # Llama a la función del otro archivo, pasándole:
        # 1. El DataFrame
        # 2. El marco donde dibujar
        # 3. La función a la que debe llamar cuando termine (el callback)
        lanzar_selector(df_original, frame_pasos_container, iniciar_paso_2)


def iniciar_paso_2(df_seleccionado):
    """Llama al módulo de manejo de inexistentes."""
    global frame_pasos_container
    # Llama a la función del otro archivo, pasándole:
    # 1. El DataFrame seleccionado
    # 2. El marco donde dibujar
    # 3. La función a la que debe llamar cuando termine (el callback final)
    manejo_datos_inexistentes(df_seleccionado, frame_pasos_container, finalizar_pasos)


def finalizar_pasos(df_procesado):
    """Actualiza la tabla y llama al paso de separación de datos."""
    # 1. Actualiza la tabla de arriba con los datos procesados
    mostrar_tabla(df_procesado)
    messagebox.showinfo("Éxito", "Preprocesado completado. La tabla ha sido actualizada.")

    # 2. Define la función que se ejecutará DESPUÉS de la separación (Paso 4)
    #    Usamos una lambda para pasar los argumentos correctos
    callback_paso_4 = lambda train_df, test_df: iniciar_creacion_modelo(
        train_df,
        test_df,
        frame_pasos_container
    )

    # 3. Llama al paso de separación (Paso 3) y le pasa el 'callback_paso_4'
    iniciar_separacion(df_procesado, frame_pasos_container, mostrar_tabla, callback=callback_paso_4)
def abrir_archivo():
    global df_original

    ruta = filedialog.askopenfilename(
        title="Seleccionar archivo",
        filetypes=[
            ("Archivos soportados", "*.csv *.xls *.xlsx *.sqlite *.db"),
            ("Todos los archivos", ".")
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
        df_original = df.copy()
        mostrar_tabla(df_original)
        messagebox.showinfo("Éxito", "Datos cargados. Por favor, seleccione las columnas abajo.")

        # Inicia el flujo de preprocesado
        iniciar_paso_1()


# --- Creación de la Ventana Principal ---
ventana = tk.Tk()
ventana.title("Visor y Preprocesador de Datos")
ventana.geometry("900x800")

# --- 1. Marco superior (Carga de archivo) ---
frame_superior = ttk.Frame(ventana)
frame_superior.pack(pady=10, fill="x", padx=10)

etiqueta_ruta = ttk.Label(frame_superior, text="Ruta:")
etiqueta_ruta.pack(side=tk.LEFT, padx=5)

entrada_texto = tk.Entry(frame_superior, state="normal", fg="gray")
entrada_texto.insert(0, "Seleccione el archivo a cargar")
entrada_texto.config(state="readonly")
entrada_texto.pack(side=tk.LEFT, fill="x", expand=True, padx=5)

boton = ttk.Button(frame_superior, text="Abrir archivo", command=abrir_archivo)
boton.pack(side=tk.LEFT, padx=5)

# --- 2. Marco para la tabla (Visor) ---
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

# --- 3. Marco inferior (Pasos de preprocesado) ---
frame_pasos_container = ttk.LabelFrame(ventana, text="Pasos de Preprocesado", height=300)
frame_pasos_container.pack(fill="x", expand=False, padx=10, pady=10)


# --- Iniciar la App ---
ventana.mainloop()