import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
import os


def iniciar_creacion_modelo(train_df, test_df, parent_frame):
    """
    Paso 4: Crea, evalúa y muestra los resultados del modelo de regresión lineal.
    """
    # 1. Limpiar el marco
    for widget in parent_frame.winfo_children():
        widget.destroy()
    parent_frame.config(text="Paso 4: Creación y Evaluación del Modelo")

    # --- Campo de descripción ---
    ttk.Label(parent_frame, text="Descripción del Modelo:", font=("Arial", 11, "bold")).pack(pady=(10, 5))
    txt_descripcion = tk.Text(parent_frame, height=4, width=70)
    txt_descripcion.pack(padx=10, pady=5)

    # --- Botón para crear modelo ---
    ttk.Button(
        parent_frame,
        text="Crear Modelo",
        command=lambda: crear_y_mostrar_modelo(train_df, test_df, parent_frame, txt_descripcion)
    ).pack(pady=10)


def crear_y_mostrar_modelo(train_df, test_df, parent_frame, txt_descripcion):
    """Genera el modelo, calcula métricas y muestra resultados."""
    descripcion = txt_descripcion.get("1.0", tk.END).strip()

    if not descripcion:
        messagebox.showwarning("Advertencia", "La descripción está vacía. Se continuará sin descripción.")

    try:
        # --- Preparación de Datos ---
        # Asumimos que la última columna es 'y' (salida)
        # y todas las anteriores son 'X' (entrada)
        output_col = train_df.columns[-1]
        input_cols = list(train_df.columns[:-1])

        X_train = train_df[input_cols]
        y_train = train_df[output_col]
        X_test = test_df[input_cols]
        y_test = test_df[output_col]

        # --- Criterio Aceptación 2: Ajuste SÓLO con train ---
        model = LinearRegression()
        model.fit(X_train, y_train)

        # --- Criterio Aceptación 6: Métricas del Modelo ---
        # Calcular predicciones
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)

        # Calcular métricas
        r2_train = r2_score(y_train, y_pred_train)
        ecm_train = mean_squared_error(y_train, y_pred_train)
        r2_test = r2_score(y_test, y_pred_test)
        ecm_test = mean_squared_error(y_test, y_pred_test)

        # --- Criterio Aceptación 5: Fórmula del Modelo ---
        formula_str = f"{output_col} = "
        for i, col in enumerate(input_cols):
            formula_str += f"({model.coef_[i]:.4f} * {col}) + "
        formula_str += f"({model.intercept_:.4f})"

        # --- Guardar información del modelo ---
        info_modelo = {
            "descripcion": descripcion,
            "formula": formula_str,
            "r2_train": r2_train,
            "r2_test": r2_test,
            "ecm_train": ecm_train,
            "ecm_test": ecm_test
        }
        os.makedirs("modelos_guardados", exist_ok=True)
        ruta_guardado = os.path.join("modelos_guardados", "modelo_info.json")
        with open(ruta_guardado, "w", encoding="utf-8") as f:
            json.dump(info_modelo, f, indent=4, ensure_ascii=False)
        
        # --- Limpiar frame y mostrar resultados ---
        for widget in parent_frame.winfo_children():
            widget.destroy()

        ttk.Label(parent_frame, text="Modelo Creado con Éxito", font=("Arial", 12, "bold")).pack(pady=5)
        ttk.Label(parent_frame, text=f"Descripción: {descripcion}", wraplength=700, justify="center").pack(pady=5)
        ttk.Label(parent_frame, text=f"Fórmula: {formula_str}", wraplength=700, justify="center").pack(pady=10)

        # --- Construcción de la GUI en el parent_frame ---

        # Tabla de métricas
        ttk.Label(parent_frame, text="Métricas del Modelo:", font=("Arial", 11, "bold")).pack(pady=(10, 5))
        cols = ("Métrica", "Entrenamiento", "Test")
        tree = ttk.Treeview(parent_frame, columns=cols, show="headings", height=2)
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=180)
        tree.insert("", "end", values=("R²", f"{r2_train:.4f}", f"{r2_test:.4f}"))
        tree.insert("", "end", values=("ECM", f"{ecm_train:.4f}", f"{ecm_test:.4f}"))
        tree.pack(pady=5, padx=10, fill="x")

        # --- Gráfico si hay una sola variable ---
        ttk.Label(parent_frame, text="Gráfico de Ajuste:", font=("Arial", 11, "bold")).pack(pady=(10, 5))
        if len(input_cols) == 1:
            fig = plt.Figure(figsize=(6, 4), dpi=100)
            ax = fig.add_subplot(111)
            
            #Puntos de entrenamiento
            ax.scatter(X_train, y_train, color='blue', label='Entrenamiento', alpha=0.7)
            #puntos de test
            ax.scatter(X_test, y_test, color='red', marker='x', label='Test')
            #Recta de ajuste
            ax.plot(X_train.values, y_pred_train, color='green', linewidth=2, label='Ajuste')

            ax.set_xlabel(input_cols[0])
            ax.set_ylabel(output_col)
            ax.legend()
            fig.tight_layout()

            #Gráfico en Tkinter
            canvas = FigureCanvasTkAgg(fig, master=parent_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)

        else:
            #Avisamos en caso de múltiples entradas
            ttk.Label(parent_frame,
                      text="No se puede graficar porque el modelo tiene múltiples variables de entrada.").pack(pady=20)

        #Feedback
        messagebox.showinfo("Proceso Completado", f"Modelo guardado en:\n{ruta_guardado}")

    except Exception as e:
        #Feedback de error
        messagebox.showerror("Error en Creación de Modelo", f"Ocurrió un error:\n{e}")
