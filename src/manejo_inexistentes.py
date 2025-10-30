import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pandas as pd
import numpy as np

def manejo_datos_inexistentes(df):
    # --- Detección automática ---
    missing_info = df.isnull().sum()
    missing_cols = missing_info[missing_info > 0]

    if missing_cols.empty:
        messagebox.showinfo("Sin datos faltantes", "No se detectaron valores inexistentes en el dataset.")
        return df

    # Crear ventana
    root = tk.Toplevel()
    root.title("Manejo de Datos Inexistentes")
    root.geometry("450x400")

    tk.Label(root, text="Columnas con valores inexistentes:", font=("Arial", 11, "bold")).pack(pady=5)

    # Mostrar resumen de valores inexistentes
    frame = ttk.Frame(root)
    frame.pack(fill="both", expand=True)
    tree = ttk.Treeview(frame, columns=("columna", "faltantes"), show="headings", height=6)
    tree.heading("columna", text="Columna")
    tree.heading("faltantes", text="Cantidad de valores faltantes")
    for col, val in missing_cols.items():
        tree.insert("", "end", values=(col, val))
    tree.pack(pady=5, fill="x")

    tk.Label(root, text="Selecciona una opción para manejar los datos:", font=("Arial", 11)).pack(pady=10)

    opcion = tk.StringVar(value="media")

    opciones = {
        "Eliminar filas con valores inexistentes": "eliminar",
        "Rellenar con la media": "media",
        "Rellenar con la mediana": "mediana",
        "Rellenar con un valor constante": "constante"
    }

    for texto, valor in opciones.items():
        ttk.Radiobutton(root, text=texto, variable=opcion, value=valor).pack(anchor="w", padx=40)

    def aplicar_opcion():
        try:
            seleccion = opcion.get()

            if seleccion == "eliminar":
                df_result = df.dropna()
            elif seleccion == "media":
                df_result = df.fillna(df.mean(numeric_only=True))
            elif seleccion == "mediana":
                df_result = df.fillna(df.median(numeric_only=True))
            elif seleccion == "constante":
                valor = simpledialog.askstring("Valor constante", "Introduce el valor con el que deseas rellenar:")
                if valor is None or valor == "":
                    messagebox.showwarning("Sin valor", "Debes introducir un valor constante.")
                    return
                df_result = df.fillna(valor)
            else:
                messagebox.showerror("Error", "No se seleccionó una opción válida.")
                return

            messagebox.showinfo("Éxito", "El preprocesado se completó correctamente.")
            root.destroy()
            return df_result

        except Exception as e:
            messagebox.showerror("Error en preprocesado", f"Ocurrió un problema: {e}")
            return df

    ttk.Button(root, text="Aplicar", command=aplicar_opcion).pack(pady=15)
    root.mainloop()
