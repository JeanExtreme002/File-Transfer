from fileTransfer import FileTransfer
from threading import Thread
from tkinter import DoubleVar,Frame,Label,Tk
from tkinter.filedialog import askdirectory,askopenfilename
from tkinter.ttk import Button,Entry,Progressbar,Style
import os

class App(object):

    screen_background = "#EAEAAE"
    screen_resizable = (False,False)
    screen_title = "File Transfer GUI"

    __address = None
    __path = None
    __mode = FileTransfer.CLIENT


    def __init__(self):
        
        # Obtém a largura da tela do dispositivo do usuário
        self.__window = Tk()
        width = self.__window.winfo_screenwidth()
        default_width = 600
        self.__window.destroy()

        # Define o tamanho da janela do programa
        if width >= default_width:
            self.screen_geometry = [default_width,int(0.16666666666666666666666666666667*default_width)]
        else:
            self.screen_geometry = [width,int(0.16666666666666666666666666666667*width)]

        # Ajusta o tamanho de fonte, largura e outros com base na resolução da janela do programa
        self.button_font = ("Arial",int(15/default_width*self.screen_geometry[0]))
        self.button_width = int(10/default_width*self.screen_geometry[0])
        self.entry_font = ("Arial",int(20/default_width*self.screen_geometry[0]))
        self.filename_size = int(20/default_width*self.screen_geometry[0])
        self.label_font = ("Arial",int(15/default_width*self.screen_geometry[0]))
        self.__sep = int(5/default_width*self.screen_geometry[0])

        # Cria um objeto para realizar a transferência
        self.fileTransfer = FileTransfer()

        # Cria a janela
        self.buildWindow()

        # Cria parte para inserir o endereço e tipo da transferência
        self.buildInterfaceToCreateConnection()
    
        self.__window.mainloop()


    def buildWindow(self,title=screen_title):
        """
        Método para criar a janela do programa.
        """

        # Cria janela e realiza algumas configurações
        self.__window = Tk()
        self.__window.title(title)
        self.__window.resizable(*self.screen_resizable)
        self.__window.geometry("{}x{}".format(*self.screen_geometry))
        self.__window.protocol("WM_DELETE_WINDOW",self.close)
        self.__window["bg"] = self.screen_background

        # Cria estilos dos botões do programa
        self.__style = Style()
        self.__style.configure("SELECTED.TButton",background=self.screen_background,foreground="red",font=self.button_font,width=self.button_width)
        self.__style.configure("TButton",background=self.screen_background,foreground="black",font=self.button_font,width=self.button_width)


    def buildInterfaceToCreateConnection(self):
        """
        Método para criar uma interface para o usuário 
        inserir o endereço e tipo de transferência.
        """

        def clearEntry(entry):
            """
            Função para limpar o título das Entrys.
            """
            if entry.hasTitle and entry.get() == entry.title:
                entry.delete(0,"end")
                entry.hasTitle = False

        # Cria um frame para colocar as Entrys de IP e PORT NUMBER
        entrysFrame = Frame(self.__window,bg=self.screen_background)
        entrysFrame.pack(side="left",padx=self.__sep)

        # Cria uma entry para inserir o IP 
        self.__ip_entry = Entry(entrysFrame,font=self.entry_font)
        self.__ip_entry.title = "IP: "
        self.__ip_entry.insert(0,self.__ip_entry.title)
        self.__ip_entry.hasTitle = True
        self.__ip_entry.bind("<Button-1>",lambda event: clearEntry(self.__ip_entry))
        self.__ip_entry.pack(padx=self.__sep)

        # Cria uma entry para inserir o PORT NUMBER
        self.__port_entry = Entry(entrysFrame,font=self.entry_font)
        self.__port_entry.title = "PORT: "
        self.__port_entry.insert(0,self.__port_entry.title)
        self.__port_entry.hasTitle = True
        self.__port_entry.bind("<Button-1>",lambda event: clearEntry(self.__port_entry))
        self.__port_entry.pack(padx=self.__sep,pady=self.__sep)

        # Cria um frame para os botões
        buttonsFrame = Frame(self.__window,bg=self.screen_background)
        buttonsFrame.pack(side="left",padx=self.__sep)

        #Cria um frame somente para botões de seleção de modo de transferência
        modeButtonsFrame = Frame(buttonsFrame,bg=self.screen_background)
        modeButtonsFrame.pack(side="top",pady=self.__sep*2)

        # Cria um botão para selecionar o modo Client (Download). Por padrão, ele já é selecionado.
        self.clientButton = Button(modeButtonsFrame,text="Client",style="SELECTED.TButton")
        self.clientButton.config(command=lambda: self.setMode("client",True))
        self.clientButton.pack(side="left",padx=self.__sep)

        # Cria um botão para selecionar o modo Host (Upload)
        self.hostButton = Button(modeButtonsFrame,text="Host",style="TButton")
        self.hostButton.config(command=lambda: self.setMode("host",True))
        self.hostButton.pack(side="left",padx=self.__sep)

        # Cria um botão para prosseguir
        self.continueButton = Button(buttonsFrame,text="Continue",width=(self.button_width*2)-3+self.__sep,style="TButton")
        self.continueButton.config(command=self.buildInterfaceToSelectPathOrFilename)
        self.continueButton.pack(side="top",pady=self.__sep)


    def buildInterfaceToSelectPathOrFilename(self):
        """
        Método para criar uma interface onde o usuário possa
        escolher o arquivo que será enviado ou o diretório onde
        o arquivo baixado será salvo.
        """

        def clearEntry(entry):
            """
            Função para limpar o título das Entrys.
            """
            if entry.hasTitle and entry.get() == entry.title:
                entry.delete(0,"end")
                entry.hasTitle = False
            elif self.__path:
                entry.delete(0,"end")
                self.__path_entry.insert(0,self.__path)

        def setPath():
            """
            Função para definir o caminho do arquivo ou da pasta.
            """
            path = functionToGetDirectory()
            if not path or path == self.__path_entry.title:
                return
            self.__path_entry.delete(0,"end")
            self.__path_entry.insert(0,path)
            self.__path = path


        # Recebe o IP e o PORT NUMBER dentro das entrys
        ip = self.__ip_entry.get()
        port = self.__port_entry.get()

        # Se o PORT NUMBER não for numérico ou o usuário não 
        # tiver inserido um IP ou PORT NUMBER, não será possível prosseguir.
        if port.isnumeric():
            port = int(port)
        else: return
        if (not ip or ip == self.__ip_entry.title) or (not port or port == self.__port_entry.title): return 
        

        self.__address = (ip,port)

        # Destrói a janela antiga para criar uma nova
        self.__window.destroy()
        self.buildWindow(self.screen_title+"   [ {} : {} ]".format(*self.__address))

        # Cria uma entry para guardar o caminho do arquivo ou pasta selecionada
        self.__path_entry = Entry(self.__window,font=self.entry_font)

        # Define o título da entry e a função para selecionar 
        # o caminho do arquivo ou pasta, com base no modo de transferência 
        # selecionado anteriormente.

        if self.__mode == FileTransfer.CLIENT:
            self.__path_entry.title = "Directory to save file: "
            self.__path_entry.insert(0,self.__path_entry.title)
            functionToGetDirectory = askdirectory
        else:
            self.__path_entry.title = "File to upload: "
            self.__path_entry.insert(0,self.__path_entry.title)
            functionToGetDirectory = askopenfilename
        
        # Configura a entry
        self.__path_entry.hasTitle = True
        self.__path_entry.bind("<Button-1>",lambda event: clearEntry(self.__path_entry))
        self.__path_entry.pack(side="left",padx=self.__sep*2)

        # Cria botão para selecionar um arquivo ou pasta
        findButton = Button(self.__window,text="Search",command=setPath,style="TButton")
        findButton.pack(side="left",padx=self.__sep)

        # Cria um botão para iniciar a transferência
        connectButton = Button(self.__window,text="Connect",style="TButton")
        connectButton.config(command=self.buildInterfaceToConnect)
        connectButton.pack(side="left",padx=self.__sep)

        self.__window.mainloop()


    def buildInterfaceToConnect(self):
        """
        Método para criar uma interface onde o usuário possa ver tudo relacionado
        à conexão do client e servidor e transferência do arquivo.
        """

        # Caso o usuário não tenha selecionado um arquivo ou pasta, 
        # não será possível prosseguir.
        if not self.__path:
            return

        if self.__path != self.__path_entry.get():
            self.__path_entry.delete(0,"end")
            self.__path_entry.insert(0,self.__path)
            return

        # Destrói a janela antiga para criar uma nova
        self.__window.destroy()
        self.buildWindow(self.screen_title+"   [ {} : {} ]".format(*self.__address))

        # Cria um label para mostrar todas as informações da transferência e conexão
        self.__infoLabel = Label(self.__window,bg=self.screen_background,font=self.label_font) 
        self.__infoLabel.pack(pady=self.__sep*3)

        # Essa variável irá guardar a resposta da conexão.
        self.__resp = None

        def connect():
            """
            Função para iniciar a conexão
            """
            try:
                # Obtêm uma resposta da conexão
                self.__resp = self.fileTransfer.connect(self.__address)
                self.buildInterfaceToTransfer()
            except:
                self.__infoLabel.config(text="Failed to attempt to connect.")
                Button(self.__window,text="Close",command=self.close,style="TButton").pack()

        # Define o modo da transferência
        self.fileTransfer.changeMode(self.__mode)

        # Informa o usuário que a conexão está sendo estabelecida
        if self.__mode == FileTransfer.CLIENT:
            self.__infoLabel.config(text="Connecting ...")
            self.fileTransfer.changePath(self.__path)
        else:
            self.fileTransfer.changeFileName(self.__path)
            self.__infoLabel.config(text="Awaiting connection ...")

        # Cria um processo para tentar conectar-se sem causar danos à interface gráfica
        Thread(target=connect).start()
        self.__window.mainloop()


    def buildInterfaceToTransfer(self):
        """
        Método para criar uma interface para o usuário 
        acompanhar o progresso da transferência.
        """

        def transfer():
            """
            Função para iniciar a transferência
            """
            def threadFunction():
                """
                Função que será executada dentro de uma Thread para realizar
                a transferência sem causar danos à interface gráfica.
                """

                try:
                    self.fileTransfer.transfer(progressFunction)
                    self.__progressBar.forget()
                    self.__infoLabel.config(text="Transfer completed successfully.")
                    Button(self.__window,text="Close",command=self.close,style="TButton").pack()
                except:
                    self.__progressBar.forget()

                    if self.__mode == FileTransfer.CLIENT:
                        self.__infoLabel.config(text="A failure occurred during the transfer.")
                    else:
                        self.__infoLabel.config(text="Connection terminated.")
                    Button(self.__window,text="Close",command=self.close,style="TButton").pack()

            # Destrói o botão para permitir o download
            downloadButton.destroy()

            # Cria um objeto de DoubleVar para o preenchimento da barra de progresso
            self.__variable = DoubleVar()
            self.__variable.set(0)

            # Cria uma barra de progresso para o usuário ter uma noção maior do andamento da transferência
            self.__progressBar = Progressbar(
                self.__window,
                variable=self.__variable,
                maximum=100,
                length=100*(int(self.screen_geometry[0]/100))-(self.__sep*2)
                )
            self.__progressBar.pack()

            # Executa toda a transferência dentro de uma thread
            Thread(target=threadFunction).start()

        def progressFunction(percent):
            """
            Função para atualizar o progresso da transferência.
            """

            if self.__mode == FileTransfer.CLIENT:

                filename = self.__resp[0]

                # Verifica se o tamanho do nome do arquivo é maior que o tamanho limite. Se sim, ele será reduzido
                if len(filename.split(".")[0]) > self.filename_size:
                    filename = filename.split(".")[0][0:self.filename_size]+"."+filename.split(".")[-1]

                self.__infoLabel.config(text='Downloading "{}" ... {}%'.format(filename,int(percent))) 
            else:
                filename = self.__path[-1]

                # Verifica se o tamanho do nome do arquivo é maior que o tamanho limite. Se sim, ele será reduzido
                if len(filename.split(".")[0]) > self.filename_size:
                    filename = filename.split(".")[0][0:self.filename_size]+"."+filename.split(".")[-1]

                self.__infoLabel.config(text='Sending "{}" ... {}%'.format(filename,int(percent)))
            self.__variable.set(percent)


        # Transforma a resposta da conexão em uma lista
        resp = list(self.__resp)

        # Divide o diretório
        self.__path = os.path.split(self.__path)

        # Cria um botão para que o usuário autorize ou não o download
        downloadButton = Button(self.__window,text="Download",width=self.button_width,command=transfer,style="TButton")

        # Se o usuário estiver realizando o download do arquivo, 
        # será mostrado o nome do arquivo, sua extensão e o tamanho
        # do arquivo formatado em (Bytes,KB,MB,GB,TB). 
        # O botão para permitir o download será mostrado apenas nesse modo.
        # Caso o usuário esteja realizando o envio do arquivo, o programa será 
        # mandado direto para a função de transferência onde o usuário,
        # terá que aguardar o Client autorizar o envio.

        if self.__mode == FileTransfer.CLIENT:

            # Formata o tamanho do arquivo
            resp[1] = int(float(resp[1]))
            size = FileTransfer.getFormattedSize(resp[1])

            # Verifica se o tamanho do nome do arquivo é maior que o tamanho limite. Se sim, ele será reduzido
            if len(resp[0].split(".")[0]) > self.filename_size:
                resp[0] = resp[0].split(".")[0][0:self.filename_size]+"."+resp[0].split(".")[-1]

            self.__infoLabel.config(text="%s [%.2f %s]"%(resp[0],size[0],size[1]))
            downloadButton.pack()

        else:
            self.__infoLabel.config(text="Awaiting confirmation of {} ...".format(resp[0]))
            transfer()


    def close(self):
        """
        Método para fechar o programa
        """
        self.fileTransfer.close()
        self.__window.destroy()
        quit()


    def getWindow(self):
        return self.__window


    def setAddress(self,ip,port):
        self.__address = (ip,port)


    def setMode(self,mode,button=None):
        
        # Altera o modo de transferência
        if mode.lower() == "client":
            mode = FileTransfer.CLIENT
        elif mode.lower() == "host":
            mode = FileTransfer.HOST
        else: raise TypeError

        self.__mode = mode   

        # Essa parte está relacionada à interface para inserir o endereço
        # e o modo de transferência. O estilo de botão será alterado adequamente.
        if button:
            if mode == FileTransfer.CLIENT:
                self.clientButton.config(style="SELECTED.TButton")
                self.hostButton.config(style="TButton")
            else:
                self.clientButton.config(style="TButton")
                self.hostButton.config(style="SELECTED.TButton")

if __name__ == "__main__":
    App()
