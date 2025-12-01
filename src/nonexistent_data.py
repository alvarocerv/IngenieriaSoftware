import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import numpy as np


def manejo_datos_inexistentes(df, parent_frame, on_apply_callback):
    """Maneja los datos inexistentes en el DataFrame según la opción seleccionada por el usuario"""
    
    # Detección automática
    missing_info = df.isnull().sum()
    missing_cols = missing_info[missing_info > 0]

    if missing_cols.empty:
        messagebox.showinfo("Sen datos faltantes", "Non se detectaron valores inexistentes no dataset seleccionado.")
        # Llama al callback para guardar el DF y dibujar el Paso 3
        on_apply_callback(df)
        return

    # Construir la UI
    tk.Label(parent_frame, text="Columnas con valores inexistentes:", font=("Arial", 11, "bold")).pack(pady=5)

    tree_frame = ttk.Frame(parent_frame)
    tree_frame.pack(fill="x", expand=True, padx=10)
    tree_missing = ttk.Treeview(tree_frame, columns=("columna", "faltantes"), show="headings", height=4)
    tree_missing.heading("columna", text="Columna")
    tree_missing.heading("faltantes", text="Cantidade Faltante")
    for col, val in missing_cols.items():
        tree_missing.insert("", "end", values=(col, val))
    tree_missing.pack(pady=5, fill="x")

    tk.Label(parent_frame, text="Selecciona unha opción para manexar os datos:", font=("Arial", 11)).pack(pady=10)

    opcion = tk.StringVar(value="media")
    opciones = {
        "Eliminar filas con valores inexistentes": "eliminar",
        "Encher ca media (só numéricas)": "media",
        "Encher ca mediana (só numéricas)": "mediana",
        "Encher cun valor constante": "constante"
    }

    for texto, valor in opciones.items():
        ttk.Radiobutton(parent_frame, text=texto, variable=opcion, value=valor).pack(anchor="w", padx=40)

    def aplicar_opcion():
        """Aplica la opción seleccionada para manejar los datos inexistentes"""
        try:
            seleccion = opcion.get()
            df_result = df.copy()

            if seleccion == "eliminar":
                df_result.dropna(inplace=True)
            elif seleccion == "media":
                cols_numericas = df_result.select_dtypes(include=np.number).columns
                df_result[cols_numericas] = df_result[cols_numericas].fillna(df_result[cols_numericas].mean())
            elif seleccion == "mediana":
                cols_numericas = df_result.select_dtypes(include=np.number).columns
                df_result[cols_numericas] = df_result[cols_numericas].fillna(df_result[cols_numericas].median())
            elif seleccion == "constante":
                valor = simpledialog.askstring("Valor constante", "Introduce o valor co que desexas encher:")
                if valor is None:
                    return
                df_result.fillna(valor, inplace=True)

            # Llama a la función 'callback' que guarda el DF y dibuja el Paso 3
            on_apply_callback(df_result)

        except Exception as e:
            messagebox.showerror("Erro no preprocesado", f"Produciuse un problema: {e}")

    # Botón de Aplicar y Finalizar
    ttk.Button(parent_frame, text="Aplicar e Finalizar", command=aplicar_opcion).pack(pady=15)