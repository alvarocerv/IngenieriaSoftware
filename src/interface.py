import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import sqlite3
import json
import threading
import math

# Funciones externas
from column_selection import lanzar_selector
from nonexistent_data import manejo_datos_inexistentes
from data_separation import iniciar_separacion
from model_creation import dibujar_ui_model_creation

# Variables globales
df_original = None
df_seleccionado = None
df_procesado = None
df_train = None
df_test = None
tree = None
canvas_pasos = None
frame_pasos_container = None
frame_pasos_wrapper = None
notebook_visor = None
progress_bar = None
entrada_texto = None

# Barra animada tipo onda
progress_running = False
progress_angle = 0

def animate_wave_progress():
    global progress_angle
    if not progress_running:
        progress_bar['value'] = 0
        return
    progress_value = (math.sin(progress_angle) + 1) / 2 * 100
    progress_bar['value'] = progress_value
    progress_angle += 0.1
    ventana.after(30, animate_wave_progress)

def start_progress():
    global progress_running, progress_angle
    progress_running = True
    progress_angle = 0
    animate_wave_progress()

def stop_progress():
    global progress_running
    progress_running = False
    progress_bar['value'] = 0

# Scroll global con trackpad/dedos
def enable_global_scroll(canvas):
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
    canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

# Funciones de carga y visualización
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
    if df is None:
        return
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

# Flujo de pasos
def iniciar_flujo_paso_1(df):
    global df_seleccionado
    for widget in frame_pasos_container.winfo_children():
        widget.destroy()
    frame_paso_1 = ttk.LabelFrame(frame_pasos_container, text="Paso 1: Selección de Columnas", padding=10)
    frame_paso_1.pack(fill="x", padx=10, pady=10)

    def callback(df_resultante):
        global df_seleccionado
        df_seleccionado = df_resultante
        mostrar_tabla(df_original)
        messagebox.showinfo("Paso 1 completado", "Columnas seleccionadas correctamente. Procediendo al siguiente paso.")
        iniciar_paso_2(df_seleccionado)

    lanzar_selector(df, frame_paso_1, callback)
    frame_pasos_container.update_idletasks()
    canvas_pasos.configure(scrollregion=canvas_pasos.bbox("all"))

def iniciar_paso_2(df):
    frame_paso_2 = ttk.LabelFrame(frame_pasos_container, text="Paso 2: Manejo de Datos Inexistentes", padding=10)
    frame_paso_2.pack(fill="x", padx=10, pady=10)
    manejo_datos_inexistentes(df, frame_paso_2, iniciar_paso_3)
    frame_pasos_container.update_idletasks()
    canvas_pasos.configure(scrollregion=canvas_pasos.bbox("all"))

def iniciar_paso_3(df_procesado_local):
    global df_procesado
    df_procesado = df_procesado_local
    mostrar_tabla(df_original)
    messagebox.showinfo("Paso 2 completado", "Preprocesado de datos inexistentes completado exitosamente.")
    frame_paso_3 = ttk.LabelFrame(frame_pasos_container, text="Paso 3: Separación de Datos", padding=10)
    frame_paso_3.pack(fill="x", padx=10, pady=10)
    iniciar_separacion(df_procesado, frame_paso_3, mostrar_tabla, iniciar_paso_4)
    frame_pasos_container.update_idletasks()
    canvas_pasos.configure(scrollregion=canvas_pasos.bbox("all"))

def iniciar_paso_4(train_df_local, test_df_local):
    global df_train, df_test
    df_train = train_df_local
    df_test = test_df_local
    messagebox.showinfo("Paso 3 completado", "Datos separados en entrenamiento y prueba. Procediendo a creación de modelo.")

    # Inicia la animación de progreso
    start_progress()

    # Ejecuta la creación del modelo en un hilo para no bloquear la interfaz
    def crear_modelo_hilo():
        dibujar_ui_model_creation(notebook_visor, df_train, df_test, guardar_modelo)
        # Una vez terminado, detiene la animación en el hilo principal
        ventana.after(0, stop_progress)

    threading.Thread(target=crear_modelo_hilo, daemon=True).start()

# Funciones de UI para abrir archivo, guardar modelo y cargar modelo
def abrir_archivo():
    global df_original
    ruta = filedialog.askopenfilename(title="Seleccionar archivo de datos", filetypes=[("Archivos soportados", "*.csv *.xls *.xlsx *.sqlite *.db"), ("Todos los archivos", "*.*")])
    if not ruta:
        messagebox.showinfo("Carga cancelada", "La carga de archivo fue cancelada.")
        return
    entrada_texto.config(state="normal")
    entrada_texto.delete(0, tk.END)
    entrada_texto.insert(0, ruta)
    entrada_texto.config(state="readonly", disabledforeground="black")
    start_progress()
    def hilo_carga():
        global df_original
        df = load_data(ruta)
        def fin():
            stop_progress()
            if df is not None:
                df_original = df.copy()
                mostrar_tabla(df_original)
                messagebox.showinfo("Datos cargados", "Archivo cargado exitosamente. Iniciando flujo de preprocesamiento.")
                iniciar_flujo_paso_1(df_original)
            else:
                messagebox.showerror("Error en carga", "No se pudo cargar el archivo.")
        ventana.after(0, fin)
    threading.Thread(target=hilo_carga, daemon=True).start()

def guardar_modelo(modelo, input_cols, output_col, descripcion, metricas):
    file_path = filedialog.asksaveasfilename(title="Guardar Modelo", defaultextension=".json", filetypes=[("Archivo JSON", "*.json"), ("Todos los archivos", "*.*")])
    if not file_path:
        messagebox.showinfo("Guardado cancelado", "El guardado fue cancelado.")
        return
    start_progress()
    def hilo_guardar():
        try:
            formula = f"{output_col} = " + " + ".join([f"({coef:.6f} * {col})" for coef, col in zip(modelo.coef_, input_cols)]) + f" + ({modelo.intercept_:.6f})"
            info_modelo = {"descripcion": descripcion, "entradas": input_cols, "salida": output_col, "formula": formula, "coeficientes": [float(c) for c in modelo.coef_], "intercepto": float(modelo.intercept_), "metricas": metricas}
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(info_modelo, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Modelo guardado", f"Modelo guardado correctamente en:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error al guardar", f"Ocurrió un error al guardar el modelo:\n{e}")
        finally:
            stop_progress()
    threading.Thread(target=hilo_guardar, daemon=True).start()

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
            filetypes=[("Archivo JSON", ".json"), ("Todos los archivos", ".*")]
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
    global notebook_visor, frame_pasos_container, df_original

    ruta = filedialog.askopenfilename(
        title="Cargar Modelo",
        filetypes=[("Modelo JSON", ".json"), ("Todos los archivos", ".*")]
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

    # Ocultar flujo inferior
    for widget in frame_pasos_container.winfo_children():
        widget.destroy()

    # Eliminar pestañas que no sean la de datos ni la de modelo (si existen)
    for tab_id in notebook_visor.tabs():
        text = notebook_visor.tab(tab_id, "text")
        if text not in ("Datos Originales/Procesados", "Modelo"):
            notebook_visor.forget(tab_id)

    # Reutilizar pestaña "Modelo" si existe, sino crearla
    model_tab = None
    for tab_id in notebook_visor.tabs():
        if notebook_visor.tab(tab_id, "text") == "Modelo":
            try:
                model_tab = notebook_visor.nametowidget(tab_id)
            except Exception:
                model_tab = None
            break

    if model_tab is None:
        model_tab = ttk.Frame(notebook_visor)
        notebook_visor.add(model_tab, text="Modelo")

    # Limpiar contenido de la pestaña de modelo antes de rellenarla
    for w in model_tab.winfo_children():
        w.destroy()

    notebook_visor.select(model_tab)

    # Contenedor
    frame = ttk.Frame(model_tab, padding=15)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Modelo Recuperado", font=("Arial", 14, "bold")).pack(pady=10)

    # Descripción
    ttk.Label(frame, text="Descripción opcional:", font=("Arial", 11, "bold")).pack(anchor="w")
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

# Ventana principal
ventana = tk.Tk()
ventana.title("Visor y Preprocesador de Datos")
ventana.geometry("900x800")

frame_superior = ttk.Frame(ventana)
frame_superior.pack(pady=10, fill="x", padx=10)

left_frame = ttk.Frame(frame_superior)
left_frame.pack(side="left", fill="x", expand=True)

etiqueta_ruta = ttk.Label(left_frame, text="Ruta:")
etiqueta_ruta.pack(side="left", padx=(0,5))

entrada_texto = tk.Entry(left_frame, fg="gray")
entrada_texto.insert(0, "Seleccione el archivo a cargar")
entrada_texto.pack(side="left", fill="x", expand=True, padx=5)

right_frame = ttk.Frame(frame_superior)
right_frame.pack(side="right")

boton_abrir = ttk.Button(right_frame, text="Abrir archivo", command=abrir_archivo)
boton_abrir.pack(side="left", padx=5)

boton_cargar_modelo = ttk.Button(right_frame, text="Cargar Modelo", command=cargar_modelo)
boton_cargar_modelo.pack(side="left", padx=5)

progress_bar = ttk.Progressbar(right_frame, mode='determinate', length=150, maximum=100)
progress_bar.pack(side="left", padx=5, pady=(5,0))

frame_tabla_notebook = ttk.Frame(ventana)
frame_tabla_notebook.pack(fill="x", expand=True, padx=10, pady=10)  


notebook_visor = ttk.Notebook(frame_tabla_notebook)
notebook_visor.pack(fill="both", expand=True)

tab_visor = ttk.Frame(notebook_visor)
notebook_visor.add(tab_visor, text="Datos Originales/Procesados")

frame_tabla = ttk.Frame(tab_visor)
# Usamos grid en la pestaña para controlar proporciones.
# La fila 0 (tabla) tendrá peso 1 y la fila 1 (panel de pasos) peso 2 -> tabla ocupa 1/3
tab_visor.rowconfigure(0, weight=1)
tab_visor.rowconfigure(1, weight=2)
tab_visor.columnconfigure(0, weight=1)
frame_tabla.grid(row=0, column=0, sticky="nsew")


# Función que oculta o muestra paneles según la pestaña seleccionada
def on_tab_change(event):
    tab_id = notebook_visor.select()
    tab_text = notebook_visor.tab(tab_id, "text")
    
    if tab_text == "Datos Originales/Procesados":
        # Mostrar tabla y pasos
        frame_tabla.grid()
        # restaurar panel de pasos si estaba oculto
        try:
            frame_pasos_wrapper.grid()
        except Exception:
            pass
    else:
        # Ocultar tabla y pasos
        frame_tabla.grid_remove()
        try:
            frame_pasos_wrapper.grid_remove()
        except Exception:
            pass

notebook_visor.bind("<<NotebookTabChanged>>", on_tab_change)


tree = ttk.Treeview(frame_tabla, show="headings")
scroll_y = ttk.Scrollbar(frame_tabla, orient="vertical", command=tree.yview)
scroll_x = ttk.Scrollbar(frame_tabla, orient="horizontal", command=tree.xview)
tree.configure(yscroll=scroll_y.set, xscroll=scroll_x.set)
tree.grid(row=0, column=0, sticky="nsew")
scroll_y.grid(row=0, column=1, sticky="ns")
scroll_x.grid(row=1, column=0, sticky="ew")
frame_tabla.rowconfigure(0, weight=1)
frame_tabla.columnconfigure(0, weight=1)

# Panel de pasos scrollable dentro de la pestaña para poder dimensionarlo junto a la tabla
frame_pasos_wrapper = ttk.Frame(tab_visor)
frame_pasos_wrapper.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

canvas_pasos = tk.Canvas(frame_pasos_wrapper, bd=0, highlightthickness=0)
scrollbar_pasos = ttk.Scrollbar(frame_pasos_wrapper, orient="vertical", command=canvas_pasos.yview)
scroll_x_pasos = ttk.Scrollbar(frame_pasos_wrapper, orient="horizontal", command=canvas_pasos.xview)
scrollbar_pasos.pack(side="right", fill="y")
scroll_x_pasos.pack(side="bottom", fill="x")
canvas_pasos.pack(side="left", fill="both", expand=True)
canvas_pasos.configure(yscrollcommand=scrollbar_pasos.set, xscrollcommand=scroll_x_pasos.set)

frame_pasos_container = ttk.Frame(canvas_pasos)
frame_pasos_container_id = canvas_pasos.create_window((0, 0), window=frame_pasos_container, anchor="nw", width=900)
frame_pasos_container.bind("<Configure>", lambda e: canvas_pasos.configure(scrollregion=canvas_pasos.bbox("all")))
canvas_pasos.bind("<Configure>", lambda e: canvas_pasos.itemconfig(frame_pasos_container_id, width=e.width))

# Asegurar empaquetado de los elementos superiores
frame_superior.pack(pady=5, fill="x", padx=10)
frame_tabla_notebook.pack(fill="both", expand=True, padx=10, pady=5)


# Habilitar scroll global en pasos
enable_global_scroll(canvas_pasos)

# Mensaje de bienvenida al iniciar
ventana.after(200, lambda: messagebox.showinfo("Visor y preprocesador de datos", "Bienvenido! Para comenzar, haga clic en 'Abrir archivo' y seleccione un archivo de datos compatible (CSV, Excel, SQLite) o cargue un modelo existente."))

ventana.mainloop()