import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pandas as pd
import numpy as np


def manejo_datos_inexistentes(df, parent_frame, on_apply_callback):
    """
    Construye la UI para manejar datos inexistentes DENTRO
    del parent_frame dado.

    Args:
        df (pd.DataFrame): El DataFrame seleccionado (solo las columnas elegidas).
        parent_frame (tk.Widget): El marco donde se dibujará esta UI.
        on_apply_callback (function): La función a llamar cuando se confirme,
                                      pasando el df_procesado.
    """

    # 1. Limpiar el marco por si había algo antes
    for widget in parent_frame.winfo_children():
        widget.destroy()
    parent_frame.config(text="Paso 2: Manejar Datos Inexistentes")

    # --- Detección automática ---
    missing_info = df.isnull().sum()
    missing_cols = missing_info[missing_info > 0]

    if missing_cols.empty:
        messagebox.showinfo("Sin datos faltantes", "No se detectaron valores inexistentes en el dataset seleccionado.")
        # Si no hay nada que hacer, simplemente llamamos al callback
        # con el dataframe tal cual
        on_apply_callback(df)
        return

    # --- Construir la UI ---
    tk.Label(parent_frame, text="Columnas con valores inexistentes:", font=("Arial", 11, "bold")).pack(pady=5)

    tree_frame = ttk.Frame(parent_frame)
    tree_frame.pack(fill="x", expand=True, padx=10)
    tree_missing = ttk.Treeview(tree_frame, columns=("columna", "faltantes"), show="headings", height=4)
    tree_missing.heading("columna", text="Columna")
    tree_missing.heading("faltantes", text="Cantidad Faltante")
    for col, val in missing_cols.items():
        tree_missing.insert("", "end", values=(col, val))
    tree_missing.pack(pady=5, fill="x")

    tk.Label(parent_frame, text="Selecciona una opción para manejar los datos:", font=("Arial", 11)).pack(pady=10)

    opcion = tk.StringVar(value="media")
    opciones = {
        "Eliminar filas con valores inexistentes": "eliminar",
        "Rellenar con la media (solo numéricas)": "media",
        "Rellenar con la mediana (solo numéricas)": "mediana",
        "Rellenar con un valor constante": "constante"
    }

    for texto, valor in opciones.items():
        ttk.Radiobutton(parent_frame, text=texto, variable=opcion, value=valor).pack(anchor="w", padx=40)

    def aplicar_opcion():
        try:
            seleccion = opcion.get()
            df_result = df.copy()  # Trabajar sobre una copia

            if seleccion == "eliminar":
                df_result.dropna(inplace=True)
            elif seleccion == "media":
                # Rellenar solo columnas numéricas que están en este DF
                cols_numericas = df_result.select_dtypes(include=np.number).columns
                df_result[cols_numericas] = df_result[cols_numericas].fillna(df_result[cols_numericas].mean())
            elif seleccion == "mediana":
                cols_numericas = df_result.select_dtypes(include=np.number).columns
                df_result[cols_numericas] = df_result[cols_numericas].fillna(df_result[cols_numericas].median())
            elif seleccion == "constante":
                valor = simpledialog.askstring("Valor constante", "Introduce el valor con el que deseas rellenar:")
                if valor is None:
                    return  # El usuario canceló
                df_result.fillna(valor, inplace=True)

            # Llama a la función 'callback' final que nos pasó la ventana principal
            on_apply_callback(df_result)

        except Exception as e:
            messagebox.showerror("Error en preprocesado", f"Ocurrió un problema: {e}")

    ttk.Button(parent_frame, text="Aplicar y Finalizar", command=aplicar_opcion).pack(pady=15)