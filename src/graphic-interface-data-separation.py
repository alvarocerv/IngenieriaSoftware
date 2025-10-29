import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import sqlite3
from sklearn.model_selection import train_test_split

#variables globales
df_original = None
df_train = None
df_test = None

# Función para cargar archivos
def load_data(file_path):
    try:
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        elif file_path.endswith((".xls", ".xlsx")):
            df = pd.read_excel(file_path)
        elif file_path.endswith((".sqlite", ".db")):
            conn = sqlite3.connect(file_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            if not tables:
                raise ValueError("No se encontraron tablas en la base de datos SQLite.")
            table_name = tables[0][0]
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
            conn.close()
        else:
            raise ValueError("Formato de archivo no válido.")
        return df

    except FileNotFoundError:
        messagebox.showerror("Error", "Archivo no encontrado.")
    except pd.errors.EmptyDataError:
        messagebox.showerror("Error", "El archivo está vacío.")
    except sqlite3.OperationalError:
        messagebox.showerror("Error", "No se pudo leer la base de datos SQLite.")
    except ValueError as e:
        messagebox.showerror("Error", str(e))
    except Exception as e:
        messagebox.showerror("Error inesperado", f"Ocurrió un problema:\n{e}")
    return None

# Interfaz gráfica
def abrir_archivo():
    global df_original
    ruta = filedialog.askopenfilename(
        title="Seleccionar archivo",
        filetypes=[
            ("Archivos soportados", "*.csv *.xls *.xlsx *.sqlite *.db"),
            ("Todos los archivos", "*.*")
        ]
    )
    if not ruta:
        return

    entrada_texto.config(state="normal")
    entrada_texto.delete(0, tk.END)
    entrada_texto.insert(0, ruta)
    entrada_texto.config(state="readonly")

    df = load_data(ruta)
    if df is not None:
        df_original = df.copy()
        mostrar_tabla(df)
        messagebox.showinfo("Éxito", "Datos cargados correctamente.")

def mostrar_tabla(df):
    # Limpiar tabla anterior
    for col in tree["columns"]:
        tree.heading(col, text="")
    tree.delete(*tree.get_children())

    # Configurar nuevas columnas
    columnas = list(df.columns)
    tree["columns"] = columnas
    for col in columnas:
        tree.heading(col, text=col)
        tree.column(col, width=120, anchor="w")

    # Insertar hasta 1000 filas para mantener fluidez
    for _, fila in df.head(1000).iterrows():
        tree.insert("", "end", values=list(fila))

#separar datos en test
def separar_datos():
    global df_original, df_train, df_test

    if df_original is  None:
        messagebox.showerror("Error", "Debe cargar los datos antes")
        return
    
    if len(df_original) <5 :
        messagebox.showerror("Error", "No hay suficientes datos para realizar la separación (se necesitan 5 filas)")
        return
    
    s = entry_test_size.get().strip()
    
    if s=="":
        messagebox.showerror("Error", "Ingrese el porcentaje de test")
    s = s.replace(",", ".")

    try:
        porcentaje = float(s)
    except ValueError:
        messagebox.showerror("Error", "Porcentaje no válido")
        return
    if not 0 <= porcentaje <= 100:
        messagebox.showerror("Error", "El porcentaje debe estra entre 0 y 100")
        return
    
    test_size = porcentaje / 100

    try:
        
        df_train, df_test = train_test_split(df_original, test_size=test_size, random_state=42)
    except ValueError:
        messagebox.showerror("Error", "No se pudo separar el dataset")
        return
    
    msg = (
        f"División realizada correctamente. \n\n"
        f"Filas en conjunto de entrenamiento: {len(df_train)}\n"
        f"Filas en conjunto de test: {len(df_test)}"
    )
    messagebox.showinfo("Exito", msg)
    mostrar_tabla(df_train)
   
# Crear ventana principal
ventana = tk.Tk()
ventana.title("Visor de Archivos de Datos")
ventana.geometry("900x600")

# Marco superior con etiqueta, cuadro y botón
frame_superior = ttk.Frame(ventana)
frame_superior.pack(pady=10)

etiqueta_ruta = ttk.Label(frame_superior, text="Ruta:")
etiqueta_ruta.grid(row=0, column=0, padx=5)

entrada_texto = tk.Entry(frame_superior, width=70, state="normal", fg="gray")
entrada_texto.insert(0, "Seleccione el archivo a cargar")
entrada_texto.config(state="readonly")
entrada_texto.grid(row=0, column=1, padx=5)

boton = ttk.Button(frame_superior, text="Abrir archivo", command=lambda: [abrir_archivo()])
boton.grid(row=0, column=2, padx=5)

# Marco para la tabla
frame_tabla = ttk.Frame(ventana)
frame_tabla.pack(fill="both", expand=True, padx=10, pady=10)

tree = ttk.Treeview(frame_tabla, show="headings")
scroll_y = ttk.Scrollbar(frame_tabla, orient="vertical", command=tree.yview)
scroll_x = ttk.Scrollbar(frame_tabla, orient="horizontal", command=tree.xview)
tree.configure(yscroll=scroll_y.set, xscroll=scroll_x.set)

tree.grid(row=0, column=0, sticky="nsew")
scroll_y.grid(row=0, column=1, sticky="ns")
scroll_x.grid(row=1, column=0, sticky="ew")

frame_tabla.rowconfigure(0, weight=1)
frame_tabla.columnconfigure(0, weight=1)

#marco para el porcentaje y separación
ttk.Label(frame_superior, text="Porcentaje Test (%): ").grid(row=1, column=0, padx=5, pady=5)
entry_test_size= ttk.Entry(frame_superior, width=10)
entry_test_size.insert(0, "20")
entry_test_size.grid(row=1, column=1, padx=5, pady=5)
boton_separar= ttk.Button(frame_superior, text="Separar datos", command=separar_datos)
boton_separar.grid(row=1, column=2, padx=5, pady=5)

ventana.mainloop()
