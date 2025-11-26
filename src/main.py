import tkinter as tk
from tkinter import ttk, messagebox
import threading
import math

# Funciones externas
from dataset_loading import abrir_archivo
from model_manager import guardar_modelo, cargar_modelo
from column_selection import lanzar_selector
from nonexistent_data import manejo_datos_inexistentes
from data_separation import iniciar_separacion
from model_creation import dibujar_ui_model_creation

# Variables globales
df_original = None
df_original_sin_filtrar = None
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
    """Animación de barra de progreso tipo onda"""
    global progress_angle
    if not progress_running:
        progress_bar['value'] = 0
        return
    progress_value = (math.sin(progress_angle) + 1) / 2 * 100
    progress_bar['value'] = progress_value
    progress_angle += 0.1
    ventana.after(30, animate_wave_progress)

def start_progress():
    """Inicia la animación de la barra de progreso"""
    global progress_running, progress_angle
    progress_running = True
    progress_angle = 0
    animate_wave_progress()

def stop_progress():
    """Detiene la animación de la barra de progreso"""
    global progress_running
    progress_running = False
    progress_bar['value'] = 0

def set_dataframes(df_orig, df_sin_filtrar):
    """Establece los dataframes originales globales"""
    global df_original, df_original_sin_filtrar
    df_original = df_orig
    df_original_sin_filtrar = df_sin_filtrar

def enable_global_scroll(canvas):
    """Habilita el scroll global con trackpad en el canvas dado"""
    def _on_mousewheel(event):
        """Maneja el scroll del mouse"""
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
    canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

def mostrar_tabla(df):
    """Muestra el DataFrame en la tabla de la interfaz"""
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
    """Inicia el flujo de preprocesamiento desde el paso 1: selección de columnas"""
    global df_seleccionado
    for widget in frame_pasos_container.winfo_children():
        widget.destroy()
    frame_paso_1 = ttk.LabelFrame(frame_pasos_container, text="Paso 1: Selección de Columnas", padding=10)
    frame_paso_1.pack(fill="x", padx=10, pady=10)

    def callback(df_resultante):
        """Callback para manejar el resultado de la selección de columnas"""
        global df_seleccionado
        df_seleccionado = df_resultante
        mostrar_tabla(df_original)
        messagebox.showinfo("Paso 1 completado", "Columnas seleccionadas correctamente. Procediendo al siguiente paso.")
        iniciar_paso_2(df_seleccionado)

    lanzar_selector(df, frame_paso_1, callback)
    frame_pasos_container.update_idletasks()
    canvas_pasos.configure(scrollregion=canvas_pasos.bbox("all"))

def iniciar_paso_2(df):
    """Inicia el paso 2: manejo de datos inexistentes"""
    frame_paso_2 = ttk.LabelFrame(frame_pasos_container, text="Paso 2: Manejo de Datos Inexistentes", padding=10)
    frame_paso_2.pack(fill="x", padx=10, pady=10)
    manejo_datos_inexistentes(df, frame_paso_2, iniciar_paso_3)
    frame_pasos_container.update_idletasks()
    canvas_pasos.configure(scrollregion=canvas_pasos.bbox("all"))

def iniciar_paso_3(df_procesado_local):
    """Inicia el paso 3: separación de datos"""
    global df_procesado, df_original_sin_filtrar
    df_procesado = df_procesado_local
    mostrar_tabla(df_original)
    messagebox.showinfo("Paso 2 completado", "Preprocesado de datos inexistentes completado exitosamente.")
    frame_paso_3 = ttk.LabelFrame(frame_pasos_container, text="Paso 3: Separación de Datos", padding=10)
    frame_paso_3.pack(fill="x", padx=10, pady=10)
    iniciar_separacion(df_procesado, frame_paso_3, mostrar_tabla, iniciar_paso_4, df_original=df_original_sin_filtrar)
    frame_pasos_container.update_idletasks()
    canvas_pasos.configure(scrollregion=canvas_pasos.bbox("all"))

def iniciar_paso_4(train_df_local, test_df_local):
    """Inicia el paso 4: creación de modelo"""
    global df_train, df_test
    df_train = train_df_local
    df_test = test_df_local
    messagebox.showinfo("Paso 3 completado", "Datos separados en entrenamiento y prueba. Procediendo a creación de modelo.")

    # Inicia la animación de progreso
    start_progress()

    def crear_modelo_hilo():
        """Crea la interfaz de creación de modelo en un hilo separado"""
        dibujar_ui_model_creation(notebook_visor, df_train, df_test, guardar_modelo)
        # Una vez terminado, detiene la animación en el hilo principal
        ventana.after(0, stop_progress)

    threading.Thread(target=crear_modelo_hilo, daemon=True).start()

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

boton_abrir = ttk.Button(right_frame, text="Abrir archivo")
boton_abrir.pack(side="left", padx=5)

boton_cargar_modelo = ttk.Button(right_frame, text="Cargar Modelo")
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

def on_tab_change(event):
    """Maneja el cambio de pestañas en el notebook para mostrar u ocultar paneles"""
    tab_id = notebook_visor.select()
    tab_text = notebook_visor.tab(tab_id, "text")
    
    if tab_text == "Datos Originales/Procesados":
        # Mostrar tabla y pasos
        frame_tabla.grid()
        # Restaurar panel de pasos si estaba oculto
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

# Configurar comandos de botones después de que se hayan definido todos los widgets
boton_abrir.config(command=lambda: abrir_archivo(entrada_texto, start_progress, stop_progress, mostrar_tabla, iniciar_flujo_paso_1, ventana, set_dataframes))
boton_cargar_modelo.config(command=lambda: cargar_modelo(notebook_visor, frame_pasos_container))

# Mensaje de bienvenida al iniciar
ventana.after(200, lambda: messagebox.showinfo("Visor y preprocesador de datos", 
    "Bienvenido! Para comenzar, haga clic en 'Abrir archivo' y seleccione un archivo de datos compatible (CSV, Excel, SQLite) o cargue un modelo existente."))

ventana.mainloop()