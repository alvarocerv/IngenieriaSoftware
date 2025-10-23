import wx

class MiVentana(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Interfaz Mínima", size=(300,200))
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Cuadro de texto donde el usuario puede escribir
        self.cuadro_texto = wx.TextCtrl(panel)
        vbox.Add(self.cuadro_texto, flag=wx.EXPAND|wx.ALL, border=40)

        # Botón que muestra un mensaje
        boton = wx.Button(panel, label="Mostrar mensaje")
        boton.Bind(wx.EVT_BUTTON, self.mostrar_mensaje)
        vbox.Add(boton, flag=wx.ALIGN_CENTER|wx.ALL, border=10)

        panel.SetSizer(vbox)
        self.Centre()
        self.Show()

    def mostrar_mensaje(self, event):
        texto = self.cuadro_texto.GetValue()
        wx.MessageBox(f"Has escrito: {texto}", "Mensaje", wx.OK | wx.ICON_INFORMATION)

if __name__ == "__main__":
    app = wx.App(False)
    ventana = MiVentana()
    app.MainLoop()
