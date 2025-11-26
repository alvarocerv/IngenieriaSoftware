import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import json


def guardar_modelo(modelo, input_cols, output_col, descripcion, metricas):
    try:
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.asksaveasfilename(
            parent=root,
            title="Guardar Modelo",
            initialdir=".",
            defaultextension=".json",
            filetypes=[("Archivo JSON", ".json"), ("Todos los archivos", ".*")]
        )
        root.destroy()
        if not file_path:
            messagebox.showinfo("Guardado cancelado", "El guardado fue cancelado.")
            return

        formula = f"{output_col} = " + " + ".join(
            [f"({coef:.6f} * {col})" for coef, col in zip(modelo.coef_, input_cols)]
        ) + f" + ({modelo.intercept_:.6f})"

        info_modelo = {
            "descripcion": descripcion,
            "entradas": input_cols,
            "salida": output_col,
            "formula": formula,
            "coeficientes": [float(c) for c in modelo.coef_],
            "intercepto": float(modelo.intercept_),
            "metricas": metricas
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(info_modelo, f, indent=4, ensure_ascii=False)

        messagebox.showinfo("Modelo guardado", f"Guardado correctamente en:\n{file_path}")

    except Exception as e:
        messagebox.showerror("Error al guardar", f"Ocurrió un error:\n{e}")


def cargar_modelo(notebook_visor, frame_pasos_container):
    ruta = filedialog.askopenfilename(
        title="Cargar Modelo",
        filetypes=[("Modelo JSON", ".json"), ("Todos los archivos", ".*")]
    )
    if not ruta:
        return

    try:
        with open(ruta, "r", encoding="utf-8") as f:
            info = json.load(f)
    except Exception as e:
        messagebox.showerror("Error", f"El archivo no es válido o está corrupto:\n{e}")
        return

    # Validación mínima
    campos_requeridos = ["descripcion", "entradas", "salida", "formula",
                         "coeficientes", "intercepto", "metricas"]

    if not all(c in info for c in campos_requeridos):
        messagebox.showerror("Modelo inválido",
                             "El archivo no contiene los datos requeridos para un modelo válido.")
        return

    # Ocultar flujo inferior
    for widget in frame_pasos_container.winfo_children():
        widget.destroy()

    # Eliminar pestañas que no sean la de datos ni la de modelo (si existen)
    for tab_id in notebook_visor.tabs():
        text = notebook_visor.tab(tab_id, "text")
        if text not in ("Datos Originales/Procesados", "Modelo"):
            notebook_visor.forget(tab_id)

    # Reutilizar pestaña "Modelo" si existe, sino crearla
    model_tab = None
    for tab_id in notebook_visor.tabs():
        if notebook_visor.tab(tab_id, "text") == "Modelo":
            try:
                model_tab = notebook_visor.nametowidget(tab_id)
            except Exception:
                model_tab = None
            break

    if model_tab is None:
        model_tab = ttk.Frame(notebook_visor)
        notebook_visor.add(model_tab, text="Modelo")

    # Limpiar contenido de la pestaña de modelo antes de rellenarla
    for w in model_tab.winfo_children():
        w.destroy()

    notebook_visor.select(model_tab)

    # Contenedor
    frame = ttk.Frame(model_tab, padding=15)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Modelo Recuperado", font=("Arial", 14, "bold")).pack(pady=10)

    # Descripción
    ttk.Label(frame, text="Descripción:", font=("Arial", 11, "bold")).pack(anchor="w")
    ttk.Label(frame, text=info["descripcion"], wraplength=800).pack(anchor="w", pady=(0,10))

    # Fórmula
    ttk.Label(frame, text="Fórmula:", font=("Arial", 11, "bold")).pack(anchor="w")
    ttk.Label(frame, text=info["formula"], wraplength=800).pack(anchor="w", pady=(0,10))

    # Coeficientes
    ttk.Label(frame, text="Coeficientes:", font=("Arial", 11, "bold")).pack(anchor="w")
    for col, c in zip(info["entradas"], info["coeficientes"]):
        ttk.Label(frame, text=f"{col}: {c:.6f}").pack(anchor="w")

    ttk.Label(frame, text=f"Intercepto: {info['intercepto']:.6f}").pack(anchor="w", pady=(0,10))

    # Métricas
    ttk.Label(frame, text="Métricas:", font=("Arial", 11, "bold")).pack(anchor="w")

    metricas = info["metricas"]
    cols = ("Métrica", "Entrenamiento", "Test")

    tree_metrics = ttk.Treeview(frame, columns=cols, show="headings", height=2)
    for col in cols:
        tree_metrics.heading(col, text=col)
        tree_metrics.column(col, width=200, anchor="center")

    tree_metrics.insert("", "end", values=("R²",
                                           f"{metricas['r2_train']:.4f}",
                                           f"{metricas['r2_test']:.4f}"))
    tree_metrics.insert("", "end", values=("ECM",
                                           f"{metricas['ecm_train']:.4f}",
                                           f"{metricas['ecm_test']:.4f}"))
    tree_metrics.pack(pady=10)

    # Confirmación
    messagebox.showinfo("Modelo cargado", "El modelo fue recuperado exitosamente.")
