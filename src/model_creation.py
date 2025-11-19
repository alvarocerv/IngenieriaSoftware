import tkinter as tk
from tkinter import ttk, messagebox
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Para evitar múltiples binds del mouse cuando se abre varias veces la pestaña,
# mantendremos una marca global (por módulo) para el bind.
_mousebind_installed = False

def dibujar_ui_model_creation(notebook_visor, train_df, test_df, guardar_callback=None):
    """
    Crea una nueva pestaña en notebook_visor para la creación del modelo,
    con descripción, botón Crear Modelo, área de resultados y PREDICCIÓN.
    """

    global _mousebind_installed

    # Eliminar la pestaña si ya existía para no acumularlas
    for i in range(notebook_visor.index("end")):
        if notebook_visor.tab(i, "text") == "Modelo":
            notebook_visor.forget(i)
            break

    tab_modelo = ttk.Frame(notebook_visor)
    notebook_visor.add(tab_modelo, text="Modelo")
    notebook_visor.select(tab_modelo)

    # -------------------------------------------------
    # Scrollable Frame que ocupa toda la pestaña
    # -------------------------------------------------
    canvas = tk.Canvas(tab_modelo)
    scrollbar_v = ttk.Scrollbar(tab_modelo, orient="vertical", command=canvas.yview)
    scrollbar_h = ttk.Scrollbar(tab_modelo, orient="horizontal", command=canvas.xview)
    canvas.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)

    scrollbar_v.pack(side="right", fill="y")
    scrollbar_h.pack(side="bottom", fill="x")
    canvas.pack(side="left", fill="both", expand=True)

    frame_content = ttk.Frame(canvas)
    frame_id = canvas.create_window((0, 0), window=frame_content, anchor="nw")

    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def on_canvas_resize(event):
        canvas.itemconfig(frame_id, width=event.width)

    frame_content.bind("<Configure>", on_frame_configure)
    canvas.bind("<Configure>", on_canvas_resize)

    # -------------------------------------------------
    # Scroll con rueda del ratón y trackpad
    # -------------------------------------------------
    def _on_mousewheel(event):
        # Detectar sistema (Windows/Mac vs Linux manejan eventos diferente)
        if hasattr(event, 'delta'):
            if event.state & 0x1:  # Shift presionado -> scroll horizontal
                canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")
            else:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # Bindings (protegemos contra bind duplicado)
    if not _mousebind_installed:
        try:
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
            canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
            canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
            _mousebind_installed = True
        except Exception:
            pass

    # -------------------------------------------------
    # Interfaz: Descripción
    # -------------------------------------------------
    ttk.Label(frame_content, text="Descripción del Modelo:", font=("Arial", 11, "bold")).pack(pady=(10, 5))
    txt_descripcion = tk.Text(frame_content, height=4, width=70)
    txt_descripcion.pack(padx=10, pady=5)

    # Variable para guardar la referencia al frame de predicción actual (y poder borrarlo al reentrenar)
    prediction_frame_ref = [None]

    # -------------------------------------------------
    # Lógica y Botón Crear Modelo
    # -------------------------------------------------
    def crear_modelo_callback():
        descripcion = txt_descripcion.get("1.0", tk.END).strip()
        if not descripcion:
            messagebox.showwarning("Aviso", "La descripción está vacía. Se continuará sin descripción.")

        try:
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

            # -------------------------------------------------
            # Mostrar resultados (Fórmula y Métricas)
            # -------------------------------------------------
            ttk.Label(frame_content, text="Resultados del Modelo", font=("Arial", 12, "bold")).pack(pady=(15, 5))

            formula_str = f"{output_col} = " + " + ".join(
                [f"({model.coef_[i]:.4f} * {col})" for i, col in enumerate(input_cols)]
            ) + f" + ({model.intercept_:.4f})"

            lbl_formula = ttk.Label(frame_content, text=f"Fórmula: {formula_str}", font=("Courier", 10), wraplength=700)
            lbl_formula.pack(pady=5)

            # Tabla de métricas
            cols = ("Métrica", "Entrenamiento", "Test")
            tree_metrics = ttk.Treeview(frame_content, columns=cols, show="headings", height=2)
            for col in cols:
                tree_metrics.heading(col, text=col)
                tree_metrics.column(col, width=200, anchor="center")
            tree_metrics.insert("", "end", values=("R²", f"{r2_train:.4f}", f"{r2_test:.4f}"))
            tree_metrics.insert("", "end", values=("ECM", f"{ecm_train:.4f}", f"{ecm_test:.4f}"))
            tree_metrics.pack(pady=5, padx=10, fill="x")

            # Gráfico
            if len(input_cols) == 1:
                fig = plt.Figure(figsize=(6, 4), dpi=100)
                ax = fig.add_subplot(111)
                ax.scatter(X_train, y_train, label='Entrenamiento', alpha=0.7)
                ax.scatter(X_test, y_test, marker='x', label='Test')
                ax.plot(X_train.values, y_pred_train, linewidth=2, label='Ajuste')
                ax.set_xlabel(input_cols[0])
                ax.set_ylabel(output_col)
                ax.legend()
                fig.tight_layout()

                canvas_fig = FigureCanvasTkAgg(fig, master=frame_content)
                canvas_fig.draw()
                canvas_fig.get_tk_widget().pack(side="top", fill="both", expand=True, padx=10, pady=5)
            else:
                ttk.Label(frame_content,
                          text="Nota: No se puede graficar porque hay múltiples variables de entrada.").pack(pady=10)

            # Botón Guardar
            if guardar_callback:
                metricas = {"r2_train": r2_train, "r2_test": r2_test,
                            "ecm_train": ecm_train, "ecm_test": ecm_test}
                ttk.Button(frame_content, text="Guardar Modelo",
                           command=lambda: guardar_callback(model, input_cols, output_col, descripcion, metricas)
                           ).pack(pady=10)

            # -------------------------------------------------
            # REALIZAR PREDICCIÓN
            # -------------------------------------------------

            # 1. Limpiar área de predicción anterior si existe (por si reentrenamos)
            if prediction_frame_ref[0] is not None:
                prediction_frame_ref[0].destroy()

            # 2. Crear contenedor nuevo
            frame_pred = ttk.LabelFrame(frame_content, text="Realizar Predicción Interactiva", padding="10")
            frame_pred.pack(fill="x", padx=10, pady=20)
            prediction_frame_ref[0] = frame_pred  # Guardar referencia

            # 3. Generar campos dinámicos
            input_entries = {}

            for col in input_cols:
                row_frame = ttk.Frame(frame_pred)
                row_frame.pack(fill="x", pady=2)

                lbl = ttk.Label(row_frame, text=f"{col}:", width=20, anchor="w")
                lbl.pack(side="left")

                # Campo de entrada
                ent = ttk.Entry(row_frame)
                ent.pack(side="right", expand=True, fill="x")
                input_entries[col] = ent

            # Etiqueta para el resultado
            lbl_resultado_pred = ttk.Label(frame_pred, text="Resultado: -", font=("Arial", 11, "bold"),
                                           foreground="#333")
            lbl_resultado_pred.pack(pady=10)

            # 4. Función interna para ejecutar la predicción
            def ejecutar_prediccion():
                try:
                    valores = []
                    for col in input_cols:
                        val_txt = input_entries[col].get()
                        if not val_txt.strip():
                            messagebox.showerror("Error", f"Falta valor para la variable: {col}")
                            return
                        valores.append(float(val_txt))

                    # Predecir
                    pred = model.predict([valores])[0]
                    lbl_resultado_pred.config(text=f"Resultado Predicción: {pred:.4f}", foreground="green")

                except ValueError:
                    messagebox.showerror("Error", "Asegúrate de ingresar solo valores numéricos válidos.")
                except Exception as ex:
                    messagebox.showerror("Error", f"Error al predecir: {ex}")

            # Botón Predecir
            ttk.Button(frame_pred, text="Calcular Predicción", command=ejecutar_prediccion).pack(pady=5)

            # Hacer scroll hasta abajo para ver la nueva sección
            frame_content.update_idletasks()
            canvas.yview_moveto(1.0)

        except Exception as e:
            messagebox.showerror("Error en Modelo", f"Ocurrió un error crítico:\n{e}")

    # Botón Principal para iniciar todo el proceso
    ttk.Button(frame_content, text="Crear Modelo", command=crear_modelo_callback).pack(pady=10)
