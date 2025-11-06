import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def iniciar_creacion_modelo(train_df, test_df, parent_frame):
    """
    Paso 4: Crea, evalúa y muestra los resultados del modelo de regresión lineal.
    """
    # 1. Limpiar el marco
    for widget in parent_frame.winfo_children():
        widget.destroy()
    parent_frame.config(text="Paso 4: Creación y Evaluación del Modelo")

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

        # --- Construcción de la GUI en el parent_frame ---

        # 1. Mostrar Fórmula
        ttk.Label(parent_frame, text="Fórmula del Modelo:", font=("Arial", 11, "bold")).pack(pady=(10, 2))
        ttk.Label(parent_frame, text=formula_str, wraplength=parent_frame.winfo_width() - 40, justify="center").pack(
            pady=(0, 10))

        # 2. Mostrar Métricas (usamos una tabla/Treeview para claridad)
        ttk.Label(parent_frame, text="Métricas de Error:", font=("Arial", 11, "bold")).pack(pady=(10, 5))

        cols_metricas = ("Métrica", "Conjunto de Entrenamiento", "Conjunto de Test")
        tree_metricas = ttk.Treeview(parent_frame, columns=cols_metricas, show="headings", height=2)

        for col in cols_metricas:
            tree_metricas.heading(col, text=col)
            tree_metricas.column(col, anchor="center", width=150)

        tree_metricas.insert("", "end", values=(f"R² (Coef. Determinación)", f"{r2_train:.4f}", f"{r2_test:.4f}"))
        tree_metricas.insert("", "end", values=(f"ECM (Error Cuadrático Medio)", f"{ecm_train:.4f}", f"{ecm_test:.4f}"))

        tree_metricas.pack(pady=5, padx=10, fill="x")

        # --- Criterios Aceptación 3 y 4: Gráfico ---
        ttk.Label(parent_frame, text="Gráfico de Ajuste:", font=("Arial", 11, "bold")).pack(pady=(10, 5))

        if len(input_cols) == 1:
            # Si solo hay 1 entrada, SÍ podemos graficar
            fig = plt.Figure(figsize=(6, 4), dpi=100)
            ax = fig.add_subplot(111)

            # Puntos de entrenamiento
            ax.scatter(X_train, y_train, color='blue', label='Entrenamiento', alpha=0.7)
            # Puntos de test (estilo diferenciable)
            ax.scatter(X_test, y_test, color='red', marker='x', label='Test')
            # Recta de ajuste
            ax.plot(X_train.values, y_pred_train, color='green', linewidth=2, label='Recta de Ajuste')

            ax.set_xlabel(input_cols[0])
            ax.set_ylabel(output_col)
            ax.legend()
            fig.tight_layout()

            # Incrustar el gráfico en Tkinter
            canvas = FigureCanvasTkAgg(fig, master=parent_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)

        else:
            # Si hay múltiples entradas, notificamos
            ttk.Label(parent_frame,
                      text="No es posible generar la gráfica: El modelo tiene múltiples variables de entrada.").pack(
                pady=20)

        # --- Criterio Aceptación 7: Feedback ---
        messagebox.showinfo("Proceso Completado", "Modelo creado y evaluado con éxito.")

    except Exception as e:
        # --- Criterio Aceptación 7: Feedback de Error ---
        messagebox.showerror("Error en Creación de Modelo", f"Ocurrió un error: {e}")