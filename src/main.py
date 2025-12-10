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
from graphic_interface_model import dibujar_ui_model_creation
from graphic_interface_predictions import dibujar_grafico_predicciones

# Variables globales
df_original = None
df_original_sin_filtrar = None
df_seleccionado = None
df_procesado = None
df_train = None
df_test = None
tree = None
tabla_canvas = None
canvas_pasos = None
frame_pasos_container = None
frame_pasos_wrapper = None
notebook_visor = None
progress_bar = None
entrada_texto = None
tab_modelo = None

# Variables para trackear columnas seleccionadas
columnas_entrada_seleccionadas = []
columna_salida_seleccionada = None

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

def mostrar_tabla(df, columnas_entrada=None, columna_salida=None):
    """Muestra el DataFrame en la tabla con columnas coloreadas individualmente"""
    if df is None:
        return
    
    # Si no se pasan parámetros, usar las globales
    if columnas_entrada is None:
        columnas_entrada = columnas_entrada_seleccionadas
    if columna_salida is None:
        columna_salida = columna_salida_seleccionada
    
    # Limpiar canvas si existe
    if tabla_canvas:
        tabla_canvas.delete("all")
    
    columnas = list(df.columns)
    num_filas = min(1000, len(df))
    
    # Configuración dinámica de ancho de columnas
    try:
        canvas_width = tabla_canvas.winfo_width()
        if canvas_width > 1:  # Asegurarse de que el canvas ya tiene tamaño
            num_cols = len(columnas)
            col_width = max(120, canvas_width // num_cols) if num_cols > 0 else 150
        else:
            col_width = 150
    except:
        col_width = 150
    
    row_height = 25
    header_height = 30
    
    # Colores
    color_entrada = '#CCFFCC'  # Verde claro
    color_salida = '#FFCCCC'   # Rojo claro
    color_normal = 'white'
    color_border = '#CCCCCC'
    
    # Dibujar encabezados
    x_offset = 0
    for col_idx, col in enumerate(columnas):
        # Determinar color de fondo
        if columnas_entrada and col in columnas_entrada:
            bg_color = color_entrada
        elif columna_salida and col == columna_salida:
            bg_color = color_salida
        else:
            bg_color = '#F0F0F0'
        
        # Dibujar rectángulo del encabezado
        tabla_canvas.create_rectangle(
            x_offset, 0, x_offset + col_width, header_height,
            fill=bg_color, outline=color_border, width=1
        )
        
        # Dibujar texto del encabezado
        tabla_canvas.create_text(
            x_offset + col_width/2, header_height/2,
            text=col, font=('Arial', 9, 'bold')
        )
        
        x_offset += col_width
    
    # Dibujar filas de datos
    for row_idx, (_, fila) in enumerate(df.head(num_filas).iterrows()):
        x_offset = 0
        y_pos = header_height + (row_idx * row_height)
        
        for col_idx, col in enumerate(columnas):
            value = fila[col]
            
            # Determinar color de fondo según la columna
            if columnas_entrada and col in columnas_entrada:
                bg_color = color_entrada
            elif columna_salida and col == columna_salida:
                bg_color = color_salida
            else:
                bg_color = color_normal if row_idx % 2 == 0 else '#F9F9F9'
            
            # Dibujar rectángulo de celda
            tabla_canvas.create_rectangle(
                x_offset, y_pos, x_offset + col_width, y_pos + row_height,
                fill=bg_color, outline=color_border, width=1
            )
            
            # Dibujar texto de la celda
            text = str(value)
            if len(text) > 18:
                text = text[:15] + '...'
            
            tabla_canvas.create_text(
                x_offset + 5, y_pos + row_height/2,
                text=text, font=('Arial', 8), anchor='w'
            )
            
            x_offset += col_width
    
    # Actualizar región de scroll
    tabla_canvas.configure(scrollregion=tabla_canvas.bbox("all"))

# Flujo de pasos
def iniciar_flujo_paso_1(df):
    """Inicia el flujo de preprocesamiento desde el paso 1: selección de columnas"""
    global df_seleccionado, columnas_entrada_seleccionadas, columna_salida_seleccionada, tab_modelo
    
    # Borrar la pestaña del modelo si existe
    try:
        if tab_modelo is not None:
            # Buscar el índice de la pestaña del modelo
            for i in range(notebook_visor.index('end')):
                if notebook_visor.tab(i, 'text') == 'Modelo':
                    notebook_visor.forget(i)
                    break
            tab_modelo = None
    except Exception as e:
        print(f"Error al borrar pestaña del modelo: {e}")
    
    # Reiniciar secciones de pasos 2 y 3 si existían
    try:
        for child in list(frame_pasos_container.winfo_children()):
            if isinstance(child, ttk.LabelFrame) and child.cget("text") in ("Paso 2: Manejo de Datos Inexistentes", "Paso 3: Separación de Datos"):
                child.destroy()
    except Exception:
        pass
    # Limpiar contenedor y preparar Paso 1
    for widget in frame_pasos_container.winfo_children():
        widget.destroy()
    frame_paso_1 = ttk.LabelFrame(frame_pasos_container, text="Paso 1: Selección de Columnas", padding=10)
    frame_paso_1.pack(fill="x", padx=10, pady=10)

    def on_selection_change(entradas, salida):
        """Callback que se ejecuta cada vez que cambia la selección de columnas"""
        global columnas_entrada_seleccionadas, columna_salida_seleccionada
        columnas_entrada_seleccionadas = entradas
        columna_salida_seleccionada = salida
        # Actualizar tabla con las columnas coloreadas
        mostrar_tabla(df_original, entradas, salida)

    def callback(df_resultante, columnas_entrada, columna_salida):
        """Callback para manejar el resultado de la selección de columnas"""
        global df_seleccionado, columnas_entrada_seleccionadas, columna_salida_seleccionada, tab_modelo
        
        # Borrar la pestaña del modelo si existe (ya que se van a seleccionar nuevas columnas)
        try:
            if tab_modelo is not None:
                # Buscar el índice de la pestaña del modelo
                for i in range(notebook_visor.index('end')):
                    if notebook_visor.tab(i, 'text') == 'Modelo':
                        notebook_visor.forget(i)
                        break
                tab_modelo = None
        except Exception as e:
            print(f"Error al borrar pestaña del modelo: {e}")
        
        df_seleccionado = df_resultante
        columnas_entrada_seleccionadas = columnas_entrada
        columna_salida_seleccionada = columna_salida
        # Mostrar tabla con columnas coloreadas
        mostrar_tabla(df_original, columnas_entrada, columna_salida)
        messagebox.showinfo("Paso 1 completado", "Columnas seleccionadas correctamente. Procediendo al siguiente paso.")
        iniciar_paso_2(df_seleccionado)

    lanzar_selector(df, frame_paso_1, callback, on_selection_change)
    frame_pasos_container.update_idletasks()
    canvas_pasos.configure(scrollregion=canvas_pasos.bbox("all"))

def iniciar_paso_2(df):
    """Inicia el paso 2: manejo de datos inexistentes"""
    # Reiniciar secciones de pasos 2 y 3 si ya existen
    try:
        for child in list(frame_pasos_container.winfo_children()):
            if isinstance(child, ttk.LabelFrame) and child.cget("text") in ("Paso 2: Manejo de Datos Inexistentes", "Paso 3: Separación de Datos"):
                child.destroy()
    except Exception:
        pass
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
    # Reiniciar ventana/sección de separación de datos si ya existe para evitar duplicados
    try:
        for child in list(frame_pasos_container.winfo_children()):
            if isinstance(child, ttk.LabelFrame) and child.cget("text") == "Paso 3: Separación de Datos":
                child.destroy()
    except Exception:
        pass
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
        """Crea la interfaz de creación de modelo y la pestaña de predicciones en un hilo separado"""
        # Reiniciar pestañas: mantener solo la pestaña de datos
        try:
            for i in range(notebook_visor.index("end") - 1, -1, -1):
                if notebook_visor.tab(i, "text") != "Datos Originales/Procesados":
                    notebook_visor.forget(i)
            # Seleccionar pestaña de datos
            for i in range(notebook_visor.index("end")):
                if notebook_visor.tab(i, "text") == "Datos Originales/Procesados":
                    notebook_visor.select(i)
                    break
        except Exception:
            pass
        # Crear pestaña de modelo
        global tab_modelo
        tab_modelo = ttk.Frame(notebook_visor)
        notebook_visor.add(tab_modelo, text="Modelo")
        # Entrenar el modelo y construir su interfaz (la pestaña Predicciones se añadirá solo cuando se pulse el botón)
        dibujar_ui_model_creation(
            tab_modelo,
            notebook_visor,
            df_train,
            df_test,
            guardar_callback=guardar_modelo
        )
        # Obtener nombres de columna de entrada y salida
        columnas = list(df_train.columns)
        columnas_numericas = [col for col in columnas if df_train[col].dtype.kind in 'fi']
        # El gráfico se dibuja en on_model_ready; no repetir aquí
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

# Crear Canvas personalizado para la tabla con soporte de scroll
tabla_canvas = tk.Canvas(frame_tabla, bg='white', highlightthickness=0)
scroll_y = ttk.Scrollbar(frame_tabla, orient="vertical", command=tabla_canvas.yview)
scroll_x = ttk.Scrollbar(frame_tabla, orient="horizontal", command=tabla_canvas.xview)
tabla_canvas.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

tabla_canvas.grid(row=0, column=0, sticky="nsew")
scroll_y.grid(row=0, column=1, sticky="ns")
scroll_x.grid(row=1, column=0, sticky="ew")

frame_tabla.rowconfigure(0, weight=1)
frame_tabla.columnconfigure(0, weight=1)

# Mantener tree como None para compatibilidad pero no lo usamos
tree = None

# Soporte para scroll con rueda del ratón
def _on_canvas_mousewheel(event):
    tabla_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

def _on_canvas_shift_mousewheel(event):
    tabla_canvas.xview_scroll(int(-1*(event.delta/120)), "units")

tabla_canvas.bind("<Enter>", lambda e: tabla_canvas.bind_all("<MouseWheel>", _on_canvas_mousewheel))
tabla_canvas.bind("<Leave>", lambda e: tabla_canvas.unbind_all("<MouseWheel>"))
tabla_canvas.bind("<Shift-MouseWheel>", _on_canvas_shift_mousewheel)

# Redibujar tabla cuando cambie el tamaño del canvas
def _on_canvas_resize(event):
    """Redibuja la tabla cuando cambia el tamaño de la ventana"""
    global df_original
    if df_original is not None:
        # Esperar un poco para evitar múltiples llamadas durante el resize
        tabla_canvas.after(100, lambda: mostrar_tabla(df_original))

tabla_canvas.bind("<Configure>", _on_canvas_resize)

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
def _abrir_archivo_reset():
    """Reinicia la interfaz y carga datos nuevos en la primera pestaña."""
    def hacer_reset():
        """Ejecuta la limpieza solo después de confirmar selección de archivo."""
        global columnas_entrada_seleccionadas, columna_salida_seleccionada
        # Resetear columnas seleccionadas
        columnas_entrada_seleccionadas = []
        columna_salida_seleccionada = None
        try:
            # Eliminar todas las pestañas excepto "Datos Originales/Procesados"
            for i in range(notebook_visor.index("end") - 1, -1, -1):
                if notebook_visor.tab(i, "text") != "Datos Originales/Procesados":
                    notebook_visor.forget(i)
            # Seleccionar la pestaña principal
            for i in range(notebook_visor.index("end")):
                if notebook_visor.tab(i, "text") == "Datos Originales/Procesados":
                    notebook_visor.select(i)
                    break
            # Limpiar tabla
            try:
                tree.delete(*tree.get_children())
            except Exception:
                pass
            # Limpiar panel de pasos
            for w in frame_pasos_container.winfo_children():
                w.destroy()
        except Exception:
            pass
    
    # Abrir archivo y pasar callback de reset
    abrir_archivo(entrada_texto, start_progress, stop_progress, mostrar_tabla, iniciar_flujo_paso_1, ventana, set_dataframes, reset_callback=hacer_reset)

def _cargar_modelo_reset():
    """Vacía completamente la tabla de datos antes de cargar el modelo."""
    global df_original, df_original_sin_filtrar, df_seleccionado, df_procesado
    global df_train, df_test, columnas_entrada_seleccionadas, columna_salida_seleccionada
    
    # Limpiar Canvas
    try:
        if tabla_canvas:
            tabla_canvas.delete("all")
    except Exception as e:
        print(f"Error limpiando tabla_canvas: {e}")
    
    # Limpiar texto de entrada
    try:
        entrada_texto.delete(0, tk.END)
        entrada_texto.insert(0, "Seleccione el archivo a cargar")
        entrada_texto.config(fg="gray")
    except Exception as e:
        print(f"Error limpiando entrada_texto: {e}")
    
    # Limpiar dataframes globales
    df_original = None
    df_original_sin_filtrar = None
    df_seleccionado = None
    df_procesado = None
    df_train = None
    df_test = None
    
    # Limpiar columnas seleccionadas
    columnas_entrada_seleccionadas = []
    columna_salida_seleccionada = None
    
    cargar_modelo(notebook_visor, frame_pasos_container)

boton_abrir.config(command=_abrir_archivo_reset)
boton_cargar_modelo.config(command=_cargar_modelo_reset)

# Mensaje de bienvenida al iniciar
ventana.after(200, lambda: messagebox.showinfo("Visor y preprocesador de datos", 
    "Bienvenido! Para comenzar, haga clic en 'Abrir archivo' y seleccione un archivo de datos compatible (CSV, Excel, SQLite) o cargue un modelo existente."))

ventana.mainloop()