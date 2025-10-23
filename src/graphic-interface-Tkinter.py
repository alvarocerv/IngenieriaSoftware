import tkinter as tk
from tkinter import messagebox

# Función que se ejecutará cuando se presione el botón
def mostrar_mensaje():
    # Mostrar un mensaje después de presionar el botón
    messagebox.showinfo("Mensaje", "¡Has presionado el botón!")

# Función que habilita el cuadro de texto
def habilitar_texto():
    entrada_texto.config(state="normal")  # Habilita el cuadro de texto

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Interfaz Gráfica Simple")

# Crear un botón que mostrará un mensaje cuando se presione
boton = tk.Button(ventana, text="Presionar", command=lambda: [mostrar_mensaje(), habilitar_texto()])
boton.pack(pady=10)

# Crear un cuadro de texto donde el usuario pueda ingresar datos, inicialmente deshabilitado
entrada_texto = tk.Entry(ventana, width=30, state="disabled")  # Deshabilitado inicialmente
entrada_texto.pack(pady=10)

# Ejecutar el bucle de la interfaz
ventana.mainloop()
