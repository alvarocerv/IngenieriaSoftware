import tkinter as tk
from tkinter import ttk, messagebox
import math

def lanzar_selector(df, parent_frame, on_confirm_callback):
    """
    Selector de columnas con distribución automática según el ancho disponible.
    Aprovecha toda la pantalla sin dejar huecos.
    """

    for w in parent_frame.winfo_children():
        w.destroy()

    columns = list(df.columns)
    salida_var = tk.StringVar(value="")

    # --------------------------------------------------------
    # FUNCIONES
    # --------------------------------------------------------

    def confirmar_seleccion():
        entradas = [c for c, v in check_vars_inputs.items() if v.get()]
        salida = salida_var.get()

        if not entradas:
            messagebox.showerror("Error", "Selecciona al menos una columna de entrada.")
            return
        if salida == "":
            messagebox.showerror("Error", "Selecciona una columna de salida.")
            return
        if salida in entradas:
            messagebox.showerror("Error", "La salida no puede ser una entrada.")
            return

        df_sel = df[entradas + [salida]].copy()
        on_confirm_callback(df_sel)

    def seleccionar_salida(cname, var):
        """Solo una salida permitida."""
        if var.get():
            salida_var.set(cname)
            for name, v in check_vars_output.items():
                if name != cname:
                    v.set(False)
        else:
            salida_var.set("")

    # --------------------------------------------------------
    # TÍTULO
    # --------------------------------------------------------

    ttk.Label(parent_frame, text="Selecciona columnas", font=("Arial", 12, "bold")).pack(pady=5)

    contenedor = ttk.Frame(parent_frame)
    contenedor.pack(fill="both", expand=True, padx=10, pady=10)

    frame_inputs = ttk.LabelFrame(contenedor, text="Columnas de entrada", padding=8)
    frame_outputs = ttk.LabelFrame(contenedor, text="Columna de salida", padding=8)

    frame_inputs.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
    frame_outputs.grid(row=0, column=1, sticky="nsew")

    contenedor.columnconfigure(0, weight=1)
    contenedor.columnconfigure(1, weight=1)

    # Variables
    check_vars_inputs = {}
    check_vars_output = {}

    # --------------------------------------------------------
    # DISTRIBUCIÓN AUTOMÁTICA SEGÚN ANCHO
    # --------------------------------------------------------

    def distribuir_checkboxes():
        """Reorganiza los checkboxes aprovechando todo el ancho."""

        # Limpiar frames
        for w in frame_inputs.winfo_children():
            w.destroy()
        for w in frame_outputs.winfo_children():
            w.destroy()

        # Ancho disponible
        ancho_inputs = frame_inputs.winfo_width()
        ancho_outputs = frame_outputs.winfo_width()

        # Si aún no existe tamaño, poner un valor base
        ancho_inputs = max(ancho_inputs, 400)
        ancho_outputs = max(ancho_outputs, 400)

        # Tamaño estimado de un checkbox
        check_width = 150

        cols_inputs = max(1, ancho_inputs // check_width)
        cols_outputs = max(1, ancho_outputs // check_width)

        rows_inputs = math.ceil(len(columns) / cols_inputs)
        rows_outputs = math.ceil(len(columns) / cols_outputs)

        # Crear checkboxes entrada
        r, c = 0, 0
        for cname in columns:
            var = check_vars_inputs[cname]
            chk = tk.Checkbutton(frame_inputs, text=cname, variable=var)
            chk.grid(row=r, column=c, padx=5, pady=3, sticky="w")

            r += 1
            if r >= rows_inputs:
                r = 0
                c += 1

        # Crear checkboxes salida
        r, c = 0, 0
        for cname in columns:
            var = check_vars_output[cname]
            chk = tk.Checkbutton(
                frame_outputs,
                text=cname,
                variable=var,
                command=lambda n=cname, v=var: seleccionar_salida(n, v)
            )
            chk.grid(row=r, column=c, padx=5, pady=3, sticky="w")

            r += 1
            if r >= rows_outputs:
                r = 0
                c += 1

    # Inicializar check_vars
    for cname in columns:
        check_vars_inputs[cname] = tk.BooleanVar()
        check_vars_output[cname] = tk.BooleanVar()

    # Llamar a la distribución cuando se cambie tamaño
    frame_inputs.bind("<Configure>", lambda e: distribuir_checkboxes())
    frame_outputs.bind("<Configure>", lambda e: distribuir_checkboxes())

    # --------------------------------------------------------
    # BOTÓN CONFIRMAR
    # --------------------------------------------------------
    ttk.Button(parent_frame, text="Confirmar y continuar", command=confirmar_seleccion)\
        .pack(pady=15)
