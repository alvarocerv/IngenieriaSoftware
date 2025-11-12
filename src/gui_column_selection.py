import tkinter as tk
from tkinter import ttk, messagebox


def lanzar_selector(df, parent_frame, on_confirm_callback):
    """
    Construye la UI para seleccionar columnas DENTRO del parent_frame dado.

    Args:
        df (pd.DataFrame): El DataFrame del que leer las columnas.
        parent_frame (tk.Widget): El marco donde se dibujará esta UI.
        on_confirm_callback (function): La función a llamar cuando se confirme,
                                        pasando el df_seleccionado.
    """

    # El LabelFrame fue creado en mejora_interfaz.py, solo dibujamos el contenido.

    columns = list(df.columns)
    regression_type = "multiple"

    def confirmar_seleccion():
        entradas = []
        if regression_type == "multiple":
            for col, var in check_vars.items():
                if var.get():
                    entradas.append(col)
        else:
            entrada = entrada_var.get()
            if entrada:
                entradas.append(entrada)

        salida = salida_var.get()

        if not entradas or not salida or salida == "Seleccionar...":
            messagebox.showerror("Error", "Selecciona al menos una columna de entrada y una columna de salida")
            return

        if salida in entradas:
            messagebox.showerror("Error", "La columna de salida no puede ser la misma que una de entrada.")
            return

        columnas_usadas = entradas + [salida]
        df_seleccionado = df[columnas_usadas].copy()

        # Llama a la función 'callback' que dibuja el Paso 2
        on_confirm_callback(df_seleccionado)

        # Contenedor para Checkbuttons con scroll

    tk.Label(parent_frame, text="Selecciona columnas de entrada:", font=("Arial", 11, "bold")).pack(pady=(10, 0))

    frame_canvas = ttk.Frame(parent_frame, height=100)
    canvas = tk.Canvas(frame_canvas, height=100)
    scrollbar = ttk.Scrollbar(frame_canvas, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    frame_canvas.pack(fill="x", padx=10, pady=5)
    canvas.pack(side="left", fill="x", expand=True)
    scrollbar.pack(side="right", fill="y")

    check_vars = {}
    if regression_type == "multiple":
        for col in columns:
            var = tk.BooleanVar()
            chk = tk.Checkbutton(scrollable_frame, text=col, variable=var)
            chk.pack(anchor='w', padx=10)
            check_vars[col] = var
    else:
        entrada_var = tk.StringVar()
        entrada_menu = tk.OptionMenu(scrollable_frame, entrada_var, *columns)
        entrada_menu.pack()

    # Sección de salida
    tk.Label(parent_frame, text="Selecciona columna de salida:", font=("Arial", 11, "bold")).pack(pady=(10, 0))
    salida_var = tk.StringVar(value="Seleccionar...")
    salida_menu = ttk.OptionMenu(parent_frame, salida_var, "Seleccionar...", *columns)
    salida_menu.pack(pady=5)

    # Botón de confirmación (MANTENER)
    confirm_btn = ttk.Button(parent_frame, text="Confirmar y continuar", command=confirmar_seleccion)
    confirm_btn.pack(pady=10)