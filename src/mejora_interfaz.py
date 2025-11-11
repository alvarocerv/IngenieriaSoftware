import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import sqlite3
import os
from sklearn.model_selection import train_test_split

# Importamos las funciones de los otros archivos
from gui_column_selection import lanzar_selector
from manejo_inexistentes import manejo_datos_inexistentes
from data_separation import iniciar_separacion
from model_creation import crear_y_mostrar_modelo, dibujar_ui_model_creation

# --- Variables Globales ---
df_original = None
tree = None
frame_pasos_container = None
canvas_pasos = None
df_seleccionado = None
df_procesado = None
df_train = None
df_test = None
notebook_visor = None


# --- Funciones de Carga y Visualización (SIN CAMBIOS) ---

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
    tree.delete(*tree.get_children())
    columnas = list(df.columns)
    tree["columns"] = columnas
    tree.heading("#0", text="", anchor="w")
    tree.column("#0", width=0, stretch=tk.NO)

    for col in columnas:
        tree.heading(col, text=col)
        tree.column(col, width=120, anchor="w")

    for i, fila in df.head(1000).iterrows():
        tree.insert("", "end", values=list(fila))


# --- Funciones de Scroll y Auxiliares (SIN CAMBIOS) ---

def on_frame_configure(event=None):
    """Ajusta la región de scroll cuando el contenido cambia."""
    global canvas_pasos
    if canvas_pasos and frame_pasos_container.winfo_children():
        canvas_pasos.configure(scrollregion=canvas_pasos.bbox("all"))


def on_canvas_resize(event):
    """Asegura que el frame_pasos_container tenga el mismo ancho que el canvas."""
    global frame_pasos_container
    if frame_pasos_container:
        event.widget.itemconfig(event.widget.winfo_children()[0], width=event.width)


# --- Funciones de Flujo (Llamada Secuencial) ---

def iniciar_paso_2():
    """Crea y dibuja la UI del Paso 2. Mantiene la tabla superior con el DF original."""
    global df_original, df_seleccionado, canvas_pasos

    # Mantenemos la tabla superior mostrando el DF original
    mostrar_tabla(df_original.copy())

    frame_paso_2 = ttk.LabelFrame(frame_pasos_container, text="Manejo de Datos Inexistentes", padding="10")
    frame_paso_2.pack(fill="x", padx=10, pady=10)

    manejo_datos_inexistentes(df_seleccionado, frame_paso_2, iniciar_paso_3)

    frame_pasos_container.update_idletasks()
    on_frame_configure()
    canvas_pasos.yview_moveto(1.0)


def iniciar_paso_3(df_procesado_local):
    """Crea y dibuja la UI del Paso 3. CORREGIDO: Vuelve a mostrar el DF original en la tabla."""
    global canvas_pasos, df_procesado

    df_procesado = df_procesado_local

    # CORRECCIÓN CLAVE: Aunque el procesamiento se hizo sobre las columnas seleccionadas,
    # la tabla superior debe mostrar el df_original para cumplir con el requerimiento.
    mostrar_tabla(df_original.copy())

    messagebox.showinfo("Éxito", "Preprocesado completado. La tabla ha sido actualizada.")

    frame_paso_3 = ttk.LabelFrame(frame_pasos_container, text="Separación de Datos", padding="10")
    frame_paso_3.pack(fill="x", padx=10, pady=10)

    # El df_procesado_local (con menos columnas, pero limpio) se pasa a la separación.
    iniciar_separacion(df_procesado, frame_paso_3, mostrar_tabla, iniciar_paso_4)

    frame_pasos_container.update_idletasks()
    on_frame_configure()
    canvas_pasos.yview_moveto(1.0)


def iniciar_paso_4(train_df_local, test_df_local):
    """Crea y dibuja la UI del Paso 4 (Descripción del Modelo)."""
    global canvas_pasos, df_train, df_test, notebook_visor

    df_train = train_df_local
    df_test = test_df_local

    frame_paso_4 = ttk.LabelFrame(frame_pasos_container, text="Creación y Evaluación del Modelo", padding="10")
    frame_paso_4.pack(fill="x", padx=10, pady=10)

    dibujar_ui_model_creation(frame_paso_4, df_train, df_test, notebook_visor)

    frame_pasos_container.update_idletasks()
    on_frame_configure()
    canvas_pasos.yview_moveto(1.0)


def iniciar_flujo_paso_1(df):
    """Inicia el dibujo del Paso 1, punto de entrada después de cargar los datos."""
    global df_original, frame_pasos_container, canvas_pasos

    for widget in frame_pasos_container.winfo_children():
        widget.destroy()

    frame_paso_1 = ttk.LabelFrame(frame_pasos_container, text="Selección de Columnas", padding="10")
    frame_paso_1.pack(fill="x", padx=10, pady=10)

    # El callback guarda el DF seleccionado y llama al siguiente paso (Paso 2)
    def callback_paso_1(df_resultante):
        global df_seleccionado
        df_seleccionado = df_resultante

        # Mantenemos la tabla mostrando el DF ORIGINAL
        mostrar_tabla(df_original.copy())

        iniciar_paso_2()

    lanzar_selector(df, frame_paso_1, callback_paso_1)

    frame_pasos_container.update_idletasks()
    on_frame_configure()


def abrir_archivo():
    global df_original

    global notebook_visor
    for i in range(notebook_visor.index("end") - 1, 0, -1):
        notebook_visor.forget(i)

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
        # Usamos .copy() para asegurarnos de que el df_original se mantenga inmutable.
        df_original = df.copy()
        mostrar_tabla(df_original)
        messagebox.showinfo("Éxito", "Datos cargados.")

        iniciar_flujo_paso_1(df_original)


# --- Creación de la Ventana Principal (RESTO DEL CÓDIGO SIN CAMBIOS) ---
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

# -----------------------------------------------------------------
# --- 2. Marco para la tabla (Notebook/Pestañas) ---
# -----------------------------------------------------------------
frame_tabla_notebook = ttk.Frame(ventana)
frame_tabla_notebook.pack(fill="both", expand=True, padx=10, pady=10)

notebook_visor = ttk.Notebook(frame_tabla_notebook)
notebook_visor.pack(fill="both", expand=True)

# --- Pestaña 1: Visor de Datos ---
tab_visor = ttk.Frame(notebook_visor)
notebook_visor.add(tab_visor, text="Datos Originales/Procesados")

frame_tabla = ttk.Frame(tab_visor)
frame_tabla.pack(fill="both", expand=True)

tree = ttk.Treeview(frame_tabla, show="headings")
scroll_y = ttk.Scrollbar(frame_tabla, orient="vertical", command=tree.yview)
scroll_x = ttk.Scrollbar(frame_tabla, orient="horizontal", command=tree.xview)
tree.configure(yscroll=scroll_y.set, xscroll=scroll_x.set)

tree.grid(row=0, column=0, sticky="nsew")
scroll_y.grid(row=0, column=1, sticky="ns")
scroll_x.grid(row=1, column=0, sticky="ew")

frame_tabla.rowconfigure(0, weight=1)
frame_tabla.columnconfigure(0, weight=1)

# -------------------------------------------------------------
# --- 3. Marco inferior (Pasos de preprocesado con SCROLL) ---
# -------------------------------------------------------------

frame_pasos_wrapper = ttk.Frame(ventana, height=300)
frame_pasos_wrapper.pack(fill="x", expand=False, padx=10, pady=10)

canvas_pasos = tk.Canvas(frame_pasos_wrapper, bd=0, highlightthickness=0)
scrollbar_pasos = ttk.Scrollbar(frame_pasos_wrapper, orient="vertical", command=canvas_pasos.yview)
scroll_x_pasos = ttk.Scrollbar(frame_pasos_wrapper, orient="horizontal", command=canvas_pasos.xview)

scrollbar_pasos.pack(side="right", fill="y")
scroll_x_pasos.pack(side="bottom", fill="x")
canvas_pasos.pack(side="left", fill="both", expand=True)

canvas_pasos.configure(yscrollcommand=scrollbar_pasos.set, xscrollcommand=scroll_x_pasos.set)

frame_pasos_container = ttk.Frame(canvas_pasos)


def inicializar_canvas_content():
    canvas_width = canvas_pasos.winfo_width() if canvas_pasos.winfo_width() > 1 else 900
    canvas_pasos.create_window((0, 0), window=frame_pasos_container, anchor="nw", width=canvas_width)
    frame_pasos_container.bind("<Configure>", on_frame_configure)
    canvas_pasos.bind("<Configure>", on_canvas_resize)


ventana.after(100, inicializar_canvas_content)

# --- Iniciar la App ---
ventana.mainloop()