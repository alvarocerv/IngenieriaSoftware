import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from sklearn.model_selection import train_test_split

#variables globales
train_df = None
test_df = None


def iniciar_separacion(df_procesado, frame_pasos_container, callback=None):
    """
    Dibuja la interfaz para separación de datos y realiza la separación
    """
    global train_df, test_df

    # Limpiar el contenedor de pasos
    for widget in frame_pasos_container.winfo_children():
        widget.destroy()

    # Etiqueta de título
    ttk.Label(frame_pasos_container, text="Separación de Datos en Entrenamiento y Test", font=("Arial", 12, "bold")).pack(pady=10)

    # Frame para inputs
    frame_inputs = ttk.Frame(frame_pasos_container)
    frame_inputs.pack(pady=5)

    # Porcentaje de entrenamiento
    ttk.Label(frame_inputs, text="Porcentaje de Entrenamiento:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    entry_train_pct = ttk.Entry(frame_inputs, width=10)
    entry_train_pct.insert(0, "%")  # Valor por defecto
    entry_train_pct.grid(row=0, column=1, padx=5, pady=5)

    # Semilla para reproducibilidad
    ttk.Label(frame_inputs, text="Porcentaje de test :").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    entry_seed = ttk.Entry(frame_inputs, width=10)
    entry_seed.insert(0, "%")  # Valor por defecto
    entry_seed.grid(row=1, column=1, padx=5, pady=5)

    # Función para realizar la separación
    def separar_datos():
        global train_df, test_df
        try:
            train_pct = float(entry_train_pct.get())
            if not (0 < train_pct < 100):
                raise ValueError("El porcentaje debe estar entre 0 y 100.")
            test_pct = 100 - train_pct
            seed = int(entry_seed.get())
            
            if len(df_procesado) < 5:
                messagebox.showerror("Error", "No hay suficientes datos para realizar la separación (mínimo 5 filas).")
                return
            
            # Realizar la separación
            train_df, test_df = train_test_split(df_procesado, test_size=test_pct/100, random_state=seed)
            
            # Mostrar confirmación
            messagebox.showinfo("Separación Completada", 
                                f"Datos separados correctamente.\n\n"
                                f"Conjunto de Entrenamiento: {len(train_df)} filas\n"
                                f"Conjunto de Test: {len(test_df)} filas")
            
            # Llamar al callback si se proporciona (por ejemplo, para el siguiente paso)
            if callback:
                callback(train_df, test_df)
            
        except ValueError as e:
            messagebox.showerror("Error", f"Entrada inválida: {e}")

    # Botón para separar
    ttk.Button(frame_pasos_container, text="Separar Datos", command=separar_datos).pack(pady=10)