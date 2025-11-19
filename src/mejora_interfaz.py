import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import sqlite3
import json

# Importamos funciones externas (archivos provistos más abajo)
from gui_column_selection import lanzar_selector
from manejo_inexistentes import manejo_datos_inexistentes
from data_separation import iniciar_separacion
from model_creation import dibujar_ui_model_creation

# --- Variables globales ---
df_original = None
tree = None
frame_pasos_container = None
canvas_pasos = None
df_seleccionado = None
df_procesado = None
df_train = None
df_test = None
notebook_visor = None
frame_pasos_wrapper = None

# ================================================================
# Funciones de carga y visualización
# ================================================================
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
    tree.heading("#0", text="")
    tree.column("#0", width=0, stretch=tk.NO)
    for col in columnas:
        tree.heading(col, text=col)
        tree.column(col, width=120, anchor="w")
    for _, fila in df.head(1000).iterrows():
        tree.insert("", "end", values=list(fila))


# ================================================================
# Scroll del panel inferior (se mantiene para el canvas container)
# ================================================================
def on_frame_configure(event=None):
    global canvas_pasos, frame_pasos_container
    if canvas_pasos and frame_pasos_container.winfo_children():
        canvas_pasos.configure(scrollregion=canvas_pasos.bbox("all"))


def on_canvas_resize(event):
    global canvas_pasos, frame_pasos_container_id, frame_pasos_container
    if frame_pasos_container:
        canvas_pasos.itemconfig(frame_pasos_container_id, width=event.width)


def _on_mousewheel(event):
    # En el panel inferior, si está visible, se puede desplazar con la rueda
    if canvas_pasos and frame_pasos_container.winfo_ismapped():
        canvas_pasos.yview_scroll(int(-1*(event.delta/120)), "units")


# ================================================================
# Guardar modelo
# ================================================================
def guardar_modelo(modelo, input_cols, output_col, descripcion, metricas):
    try:
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.asksaveasfilename(
            parent=root,
            title="Guardar Modelo",
            initialdir=".",
            defaultextension=".json",
            filetypes=[("Archivo JSON", "*.json"), ("Todos los archivos", "*.*")]
        )
        root.destroy()
        if not file_path:
            messagebox.showinfo("Guardado cancelado", "El guardado fue cancelado.")
            return

        formula = f"{output_col} = " + " + ".join(
            [f"({coef:.6f} * {col})" for coef, col in zip(modelo.coef_, input_cols)]
        ) + f" + ({modelo.intercept_:.6f})"

        info_modelo = {
            "descripcion": descripcion,
            "entradas": input_cols,
            "salida": output_col,
            "formula": formula,
            "coeficientes": [float(c) for c in modelo.coef_],
            "intercepto": float(modelo.intercept_),
            "metricas": metricas
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(info_modelo, f, indent=4, ensure_ascii=False)

        messagebox.showinfo("Modelo guardado", f"Guardado correctamente en:\n{file_path}")

    except Exception as e:
        messagebox.showerror("Error al guardar", f"Ocurrió un error:\n{e}")


# ================================================================
# recuperar modelo
# ================================================================
def cargar_modelo():
    global notebook_visor, frame_pasos_container, df_original, frame_pasos_wrapper

    ruta = filedialog.askopenfilename(
        title="Cargar Modelo",
        filetypes=[("Modelo JSON", "*.json"), ("Todos los archivos", "*.*")]
    )
    if not ruta:
        return

    try:
        with open(ruta, "r", encoding="utf-8") as f:
            info = json.load(f)
    except Exception as e:
        messagebox.showerror("Error", f"El archivo no es válido o está corrupto:\n{e}")
        return

    # Validación mínima
    campos_requeridos = ["descripcion", "entradas", "salida", "formula",
                         "coeficientes", "intercepto", "metricas"]

    if not all(c in info for c in campos_requeridos):
        messagebox.showerror("Modelo inválido",
                             "El archivo no contiene los datos requeridos para un modelo válido.")
        return

    # Ocultar flujo inferior (para que no se vea debajo)
    try:
        frame_pasos_wrapper.pack_forget()
    except Exception:
        pass

    # Eliminar pestañas excepto Datos
    for i in range(notebook_visor.index("end") - 1, 0, -1):
        notebook_visor.forget(i)

    # Crear pestaña Modelo Cargado
    tab_modelo = ttk.Frame(notebook_visor)
    notebook_visor.add(tab_modelo, text="Modelo Cargado")
    notebook_visor.select(tab_modelo)

    # Contenedor
    frame = ttk.Frame(tab_modelo, padding=15)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Modelo Recuperado", font=("Arial", 14, "bold")).pack(pady=10)

    # Descripción
    ttk.Label(frame, text="Descripción:", font=("Arial", 11, "bold")).pack(anchor="w")
    ttk.Label(frame, text=info["descripcion"], wraplength=800).pack(anchor="w", pady=(0,10))

    # Fórmula
    ttk.Label(frame, text="Fórmula:", font=("Arial", 11, "bold")).pack(anchor="w")
    ttk.Label(frame, text=info["formula"], wraplength=800).pack(anchor="w", pady=(0,10))

    # Coeficientes
    ttk.Label(frame, text="Coeficientes:", font=("Arial", 11, "bold")).pack(anchor="w")
    for col, c in zip(info["entradas"], info["coeficientes"]):
        ttk.Label(frame, text=f"{col}: {c:.6f}").pack(anchor="w")

    ttk.Label(frame, text=f"Intercepto: {info['intercepto']:.6f}").pack(anchor="w", pady=(0,10))

    # Métricas
    ttk.Label(frame, text="Métricas:", font=("Arial", 11, "bold")).pack(anchor="w")

    metricas = info["metricas"]
    cols = ("Métrica", "Entrenamiento", "Test")

    tree_metrics = ttk.Treeview(frame, columns=cols, show="headings", height=2)
    for col in cols:
        tree_metrics.heading(col, text=col)
        tree_metrics.column(col, width=200, anchor="center")

    tree_metrics.insert("", "end", values=("R²",
                                           f"{metricas['r2_train']:.4f}",
                                           f"{metricas['r2_test']:.4f}"))
    tree_metrics.insert("", "end", values=("ECM",
                                           f"{metricas['ecm_train']:.4f}",
                                           f"{metricas['ecm_test']:.4f}"))
    tree_metrics.pack(pady=10)

    # Confirmación
    messagebox.showinfo("Modelo cargado", "El modelo fue recuperado exitosamente.")


# ================================================================
# Flujo de pasos
# ================================================================
def iniciar_flujo_paso_1(df):
    global df_seleccionado, frame_pasos_container
    for widget in frame_pasos_container.winfo_children():
        widget.destroy()

    frame_paso_1 = ttk.LabelFrame(frame_pasos_container, text="Selección de Columnas", padding=10)
    frame_paso_1.pack(fill="x", padx=10, pady=10)

    def callback(df_resultante):
        global df_seleccionado
        df_seleccionado = df_resultante
        mostrar_tabla(df_original.copy())
        iniciar_paso_2()

    lanzar_selector(df, frame_paso_1, callback)
    frame_pasos_container.update_idletasks()
    on_frame_configure()


def iniciar_paso_2():
    global df_seleccionado
    mostrar_tabla(df_original.copy())

    frame_paso_2 = ttk.LabelFrame(frame_pasos_container, text="Manejo de Datos Inexistentes", padding=10)
    frame_paso_2.pack(fill="x", padx=10, pady=10)

    manejo_datos_inexistentes(df_seleccionado, frame_paso_2, iniciar_paso_3)
    frame_pasos_container.update_idletasks()
    on_frame_configure()


def iniciar_paso_3(df_procesado_local):
    global df_procesado
    df_procesado = df_procesado_local

    mostrar_tabla(df_original.copy())
    messagebox.showinfo("Éxito", "Preprocesado completado.")

    frame_paso_3 = ttk.LabelFrame(frame_pasos_container, text="Separación de Datos", padding=10)
    frame_paso_3.pack(fill="x", padx=10, pady=10)

    iniciar_separacion(df_procesado, frame_paso_3, mostrar_tabla, iniciar_paso_4)
    frame_pasos_container.update_idletasks()
    on_frame_configure()


def iniciar_paso_4(train_df_local, test_df_local):
    global df_train, df_test, notebook_visor, frame_pasos_wrapper

    df_train = train_df_local
    df_test = test_df_local

    # OCULTAR EL PANEL INFERIOR para que no se vea por debajo de la pestaña Modelo
    try:
        frame_pasos_wrapper.pack_forget()
    except Exception:
        pass

    dibujar_ui_model_creation(notebook_visor, df_train, df_test, guardar_modelo)


# ================================================================
# Función para abrir archivo
# ================================================================
def abrir_archivo():
    global df_original, notebook_visor, entrada_texto, frame_pasos_wrapper

    # Asegurarse de que el panel inferior esté visible al empezar nuevo flujo
    try:
        frame_pasos_wrapper.pack(fill="x", expand=False, padx=10, pady=10)
    except Exception:
        pass

    for i in range(notebook_visor.index("end") - 1, 0, -1):
        notebook_visor.forget(i)

    ruta = filedialog.askopenfilename(
        title="Seleccionar archivo",
        filetypes=[("Archivos soportados", "*.csv *.xls *.xlsx *.sqlite *.db"), ("Todos los archivos", "*.*")]
    )
    if not ruta:
        return

    entrada_texto.config(state="normal")
    entrada_texto.delete(0, tk.END)
    entrada_texto.insert(0, ruta)
    entrada_texto.config(state="readonly", disabledforeground="black")

    df = load_data(ruta)
    if df is not None:
        df_original = df.copy()
        mostrar_tabla(df_original)
        messagebox.showinfo("Éxito", "Datos cargados.")
        iniciar_flujo_paso_1(df_original)


# ================================================================
# Ventana principal
# ================================================================
ventana = tk.Tk()
ventana.title("Visor y Preprocesador de Datos")
ventana.geometry("900x800")

# Carga de archivo
frame_superior = ttk.Frame(ventana)
frame_superior.pack(pady=10, fill="x", padx=10)

etiqueta_ruta = ttk.Label(frame_superior, text="Ruta:")
etiqueta_ruta.pack(side="left", padx=5)

# --- ENTRY con placeholder ---
entrada_texto = tk.Entry(frame_superior, fg="gray")
placeholder = "Seleccione el archivo a cargar"
entrada_texto.insert(0, placeholder)

def limpiar_placeholder(event):
    if entrada_texto.get() == placeholder:
        entrada_texto.delete(0, tk.END)
        entrada_texto.config(fg="black", state="normal")

def restaurar_placeholder(event):
    if entrada_texto.get().strip() == "":
        entrada_texto.config(state="normal")
        entrada_texto.delete(0, tk.END)
        entrada_texto.insert(0, placeholder)
        entrada_texto.config(fg="gray")

entrada_texto.bind("<FocusIn>", limpiar_placeholder)
entrada_texto.bind("<FocusOut>", restaurar_placeholder)
entrada_texto.pack(side="left", fill="x", expand=True, padx=5)

boton = ttk.Button(frame_superior, text="Abrir archivo", command=abrir_archivo)
boton.pack(side="left", padx=5)

boton_cargar_modelo = ttk.Button(frame_superior, text="Cargar Modelo", command=cargar_modelo)
boton_cargar_modelo.pack(side="left", padx=5)

# Notebook principal
frame_tabla_notebook = ttk.Frame(ventana)
frame_tabla_notebook.pack(fill="both", expand=True, padx=10, pady=10)

notebook_visor = ttk.Notebook(frame_tabla_notebook)
notebook_visor.pack(fill="both", expand=True)

# Pestaña de datos
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

# Panel inferior scrollable (contenedor global)
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
frame_pasos_container_id = canvas_pasos.create_window((0, 0), window=frame_pasos_container, anchor="nw", width=900)

frame_pasos_container.bind("<Configure>", on_frame_configure)
canvas_pasos.bind("<Configure>", on_canvas_resize)
canvas_pasos.bind_all("<MouseWheel>", _on_mousewheel)

ventana.mainloop()
