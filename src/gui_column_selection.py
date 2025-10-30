import tkinter as tk
from tkinter import messagebox
from manejo_inexistentes import manejo_datos_inexistentes

def lanzar_selector(df):
    columns = list(df.columns)  #  columnas reales del DataFrame
    regression_type = "multiple"  # "simple" o "multiple"

    def confirmar_seleccion():
        entradas = []
        if regression_type == "multiple":
            # Recolectar columnas seleccionadas en checkbuttons
            for col, var in check_vars.items():
                if var.get():
                    entradas.append(col)
        else:
            entrada = entrada_var.get()
            if entrada:
                entradas.append(entrada)

        salida = salida_var.get()

        if not entradas or not salida:
            messagebox.showerror("Error", "Selecciona al menos una columna de entrada y una columna de salida")
        else:
            messagebox.showinfo("Éxito", f"Columnas de entrada: {entradas}\nColumna de salida: {salida}")

            # Solo usar las columnas seleccionadas
            columnas_usadas = entradas + [salida]
            df_seleccionado = df[columnas_usadas]

            # 👇 Llamamos al manejo de datos inexistentes
            manejo_datos_inexistentes(df_seleccionado)

    # Crear ventana
    root = tk.Toplevel()  #  usa Toplevel para que no bloquee la ventana principal
    root.title("Selección de Columnas")

    # Sección de entradas
    tk.Label(root, text="Selecciona columnas de entrada:").pack()

    if regression_type == "multiple":
        check_vars = {}
        for col in columns:
            var = tk.BooleanVar()
            chk = tk.Checkbutton(root, text=col, variable=var)
            chk.pack(anchor='w')
            check_vars[col] = var
    else:
        entrada_var = tk.StringVar()
        entrada_menu = tk.OptionMenu(root, entrada_var, *columns)
        entrada_menu.pack()

    # Sección de salida
    tk.Label(root, text="Selecciona columna de salida:").pack()
    salida_var = tk.StringVar()
    salida_menu = tk.OptionMenu(root, salida_var, *columns)
    salida_menu.pack()

    # Botón de confirmación
    confirm_btn = tk.Button(root, text="Confirmar selección", command=confirmar_seleccion)
    confirm_btn.pack(pady=10)