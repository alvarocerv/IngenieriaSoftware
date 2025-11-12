import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
import os


def crear_y_mostrar_modelo(train_df, test_df, parent_frame, txt_descripcion, notebook_visor, guardar_callback=None):
    """
    Función que ejecuta el cálculo del modelo y crea una nueva pestaña de resultados.
    """
    descripcion = txt_descripcion.get("1.0", tk.END).strip()

    if not descripcion:
        messagebox.showwarning("Advertencia", "La descripción está vacía. Se continuará sin descripción.")

    try:
        # --- Lógica de cálculo (sin cambios) ---
        output_col = train_df.columns[-1]
        input_cols = list(train_df.columns[:-1])

        X_train = train_df[input_cols]
        y_train = train_df[output_col]
        X_test = test_df[input_cols]
        y_test = test_df[output_col]

        model = LinearRegression()
        model.fit(X_train, y_train)

        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)

        r2_train = r2_score(y_train, y_pred_train)
        ecm_train = mean_squared_error(y_train, y_pred_train)
        r2_test = r2_score(y_test, y_pred_test)
        ecm_test = mean_squared_error(y_test, y_pred_test)

        formula_str = f"{output_col} = "
        for i, col in enumerate(input_cols):
            formula_str += f"({model.coef_[i]:.4f} * {col}) + "
        formula_str += f"({model.intercept_:.4f})"

        # ------------------------------------------------------------------
        # --- IMPLEMENTACIÓN DE NUEVA PESTAÑA ---
        # ------------------------------------------------------------------

        # 1. Crear el Frame que será la nueva pestaña
        tab_resultado = ttk.Frame(notebook_visor)

        # Intentar eliminar pestañas anteriores con el mismo nombre si existen
        try:
            tab_index = notebook_visor.tab("Resultado del Modelo", "text")
            notebook_visor.forget(tab_index)
        except tk.TclError:
            pass  # No existe, no hay problema

        notebook_visor.add(tab_resultado, text="Resultado del Modelo")
        notebook_visor.select(tab_resultado)  # Cambiar a la nueva pestaña

        # 2. Frame contenedor de contenido (con scroll si fuera necesario, pero simplificamos)
        frame_resultado = ttk.Frame(tab_resultado, padding="10")
        frame_resultado.pack(fill="both", expand=True)

        # 3. Mostrar resultados en el frame_resultado
        ttk.Label(frame_resultado, text="Modelo Creado con Éxito", font=("Arial", 14, "bold")).pack(pady=10)
        ttk.Label(frame_resultado, text=f"Descripción: {descripcion}", wraplength=750, justify="center").pack(pady=5)
        ttk.Label(frame_resultado, text=f"Fórmula: {formula_str}", wraplength=750, justify="center",
                  font=("Courier", 10)).pack(pady=10)

        # Tabla de métricas
        ttk.Label(frame_resultado, text="Métricas del Modelo:", font=("Arial", 12, "bold")).pack(pady=(10, 5))
        cols = ("Métrica", "Entrenamiento", "Test")
        tree_metrics = ttk.Treeview(frame_resultado, columns=cols, show="headings", height=2)
        for col in cols:
            tree_metrics.heading(col, text=col)
            tree_metrics.column(col, anchor="center", width=200)
        tree_metrics.insert("", "end", values=("R²", f"{r2_train:.4f}", f"{r2_test:.4f}"))
        tree_metrics.insert("", "end", values=("ECM", f"{ecm_train:.4f}", f"{ecm_test:.4f}"))
        tree_metrics.pack(pady=5, padx=10, fill="x")

        # --- Gráfico ---
        ttk.Label(frame_resultado, text="Gráfico de Ajuste:", font=("Arial", 12, "bold")).pack(pady=(10, 5))
        if len(input_cols) == 1:
            fig = plt.Figure(figsize=(6, 4), dpi=100)
            ax = fig.add_subplot(111)

            ax.scatter(X_train, y_train, color='blue', label='Entrenamiento', alpha=0.7)
            ax.scatter(X_test, y_test, color='red', marker='x', label='Test')
            ax.plot(X_train.values, y_pred_train, color='green', linewidth=2, label='Ajuste')

            ax.set_xlabel(input_cols[0])
            ax.set_ylabel(output_col)
            ax.legend()
            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=frame_resultado)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)

        else:
            ttk.Label(frame_resultado,
                      text="No se puede graficar porque el modelo tiene múltiples variables de entrada.").pack(pady=20)

        # --- Botón para guardar modelo ---
        if guardar_callback:
            metricas = {
                "r2_train": r2_train,
                "r2_test": r2_test,
                "ecm_train": ecm_train,
                "ecm_test": ecm_test
            }

            ttk.Button(
                parent_frame,
                text="Guardar Modelo",
                command=lambda: guardar_callback(model, input_cols, output_col, descripcion, metricas)
            ).pack(pady=15)

        
        # Feedback
        messagebox.showinfo("Proceso Completado", "El modelo fue creado correctamente. Usa el botón 'Guardar Modelo' para almacenarlo.")

    except Exception as e:
        messagebox.showerror("Error en Creación de Modelo", f"Ocurrió un error:\n{e}")


# Esta función se llama desde mejora_interfaz.py para DIBUJAR la UI en el scroll
def dibujar_ui_model_creation(parent_frame, train_df, test_df, notebook_visor, guardar_callback=None):
    """
    Dibuja la interfaz de descripción y el botón 'Crear Modelo' en el área de scroll.
    """

    # 1. Campo de descripción
    ttk.Label(parent_frame, text="Descripción del Modelo:", font=("Arial", 11, "bold")).pack(pady=(10, 5))
    txt_descripcion = tk.Text(parent_frame, height=4, width=70)
    txt_descripcion.pack(padx=10, pady=5)

    # 2. Botón para crear modelo (ESTE ES EL BOTÓN DE ACCIÓN FINAL)
    ttk.Button(
        parent_frame,
        text="Crear Modelo",
        # Al presionar, llama a la función de cálculo y le pasa el notebook
        command=lambda: crear_y_mostrar_modelo(
            train_df, test_df, parent_frame, txt_descripcion, notebook_visor, guardar_callback)
            ).pack(pady=10)