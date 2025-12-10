import tkinter as tk
from tkinter import ttk, messagebox
import math
import pandas as pd


def lanzar_selector(
    df, parent_frame, on_confirm_callback, on_selection_change_callback=None
):
    for w in parent_frame.winfo_children():
        w.destroy()

    columns = list(df.columns)
    salida_var = tk.StringVar(value="")

    def actualizar_seleccion(*args):
        """Callback que se ejecuta cada vez que cambia una selección"""
        if on_selection_change_callback:
            entradas = [c for c, v in check_vars_inputs.items() if v.get()]
            salida = salida_var.get()
            on_selection_change_callback(entradas, salida if salida else None)

    def confirmar_seleccion():
        entradas = [c for c, v in check_vars_inputs.items() if v.get()]
        salida = salida_var.get()

        if not entradas:
            messagebox.showerror(
                "Error", "Selecciona al menos una columna de entrada."
            )
            return
        if salida == "":
            messagebox.showerror("Error", "Selecciona una columna de salida.")
            return
        if salida in entradas:
            messagebox.showerror(
                "Error", "La salida no puede ser una entrada."
            )
            return

        # Validar que todas las columnas seleccionadas solo contengan valores numéricos o vacíos
        columnas_no_numericas = []
        todas_columnas = entradas + [salida]

        for col in todas_columnas:
            # Obtener valores no nulos de la columna
            valores_no_nulos = df[col].dropna()

            # Intentar convertir a numérico
            try:
                # Si no se puede convertir, pandas lanzará un error
                pd.to_numeric(valores_no_nulos, errors="raise")
            except (ValueError, TypeError):
                columnas_no_numericas.append(col)

        if columnas_no_numericas:
            mensaje_error = (
                "Las siguientes columnas contienen valores no numéricos:\n\n"
            )
            mensaje_error += "\n".join(
                f"• {col}" for col in columnas_no_numericas
            )
            mensaje_error += "\n\nPor favor, selecciona solo columnas con valores numéricos o vacíos."
            messagebox.showerror("Error de validación", mensaje_error)
            return

        df_sel = df[entradas + [salida]].copy()
        on_confirm_callback(df_sel, entradas, salida)

    ttk.Label(
        parent_frame, text="Selecciona columnas", font=("Arial", 12, "bold")
    ).pack(pady=5)

    contenedor = ttk.Frame(parent_frame)
    contenedor.pack(fill="both", expand=True, padx=10, pady=10)

    frame_inputs = ttk.LabelFrame(
        contenedor, text="Columnas de entrada", padding=8
    )
    frame_outputs = ttk.LabelFrame(
        contenedor, text="Columna de salida", padding=8
    )

    frame_inputs.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
    frame_outputs.grid(row=0, column=1, sticky="nsew")

    contenedor.columnconfigure(0, weight=1)
    contenedor.columnconfigure(1, weight=1)

    check_vars_inputs = {}
    check_vars_output = {}

    def distribuir_checkboxes():
        # Limpiar frames
        for w in frame_inputs.winfo_children():
            w.destroy()
        for w in frame_outputs.winfo_children():
            w.destroy()

        # Ancho disponible
        ancho_inputs = frame_inputs.winfo_width()
        # Si aún no existe tamaño, poner un valor base
        ancho_inputs = max(ancho_inputs, 400)

        # Tamaño estimado de un checkbox
        check_width = 150

        cols_inputs = max(1, ancho_inputs // check_width)

        rows_inputs = math.ceil(len(columns) / cols_inputs)

        # Crear checkboxes entrada
        # Distribuir por columnas calculadas: llenamos por columnas para equilibrar
        for idx, cname in enumerate(columns):
            row = idx % rows_inputs
            col = idx // rows_inputs
            var = check_vars_inputs[cname]
            # Usar ttk.Checkbutton para estilo consistente
            chk = ttk.Checkbutton(frame_inputs, text=cname, variable=var)
            # Expandir en ambas direcciones para ocupar el espacio disponible
            chk.grid(row=row, column=col, padx=5, pady=3, sticky="nsew")

        # Hacer que cada columna y fila se expanda igual
        for i in range(cols_inputs):
            frame_inputs.columnconfigure(i, weight=1)
        for i in range(rows_inputs):
            frame_inputs.rowconfigure(i, weight=1)

        # Label
        ttk.Label(frame_outputs, text="Selecciona la columna de salida:").pack(
            anchor="w", pady=(0, 5)
        )

        # Combobox con todas las columnas
        combo_salida = ttk.Combobox(
            frame_outputs,
            textvariable=salida_var,
            values=columns,
            state="readonly",
        )
        combo_salida.pack(fill="x", pady=5)

    # Inicializar check_vars
    for cname in columns:
        check_vars_inputs[cname] = tk.BooleanVar()
        # Agregar trace para detectar cambios
        check_vars_inputs[cname].trace_add("write", actualizar_seleccion)
        check_vars_output[cname] = tk.BooleanVar()

    # Agregar trace a la variable de salida
    salida_var.trace_add("write", actualizar_seleccion)

    # Llamar a la distribución cuando se cambie tamaño
    frame_inputs.bind("<Configure>", lambda e: distribuir_checkboxes())
    frame_outputs.bind("<Configure>", lambda e: distribuir_checkboxes())

    # Botón confirmar
    ttk.Button(
        parent_frame, text="Confirmar y continuar", command=confirmar_seleccion
    ).pack(pady=15)
