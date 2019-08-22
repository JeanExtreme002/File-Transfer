from os.path import exists,getsize,normpath,split
import socket
import io

class ActiveConnectionException(Exception):
    def __str__(self):
        return "Once you have made the connection, you will not be able to create a new connection or make changes to the file name or transfer mode until the connection is terminated."

class IncompleteTransferError(Exception):
    def __str__(self):
        return "The transfer was not completed successfully."

class NoConnectionException(Exception):
    def __str__(self):
        return "You must first start a connection."

class FileTransfer(object):
    __CLIENT = 0
    __HOST = 1
    __OK = "OK+"
    __END = "{;[???END???];}"

    CLIENT = __CLIENT
    HOST = __HOST
    OK = __OK
    END = __END

    MODE = None
    PATH = None
    FILENAME = None

    __connected = False
    __stop = False
    __running = False


    def __init__(self,filename=None,path=None,mode=CLIENT):
        """
        Os parâmetros "filename" e "path" são obrigatórios antes da chamada 
        dos métodos "connect" e "transfer".

        Caso o tipo de transferência seja UPLOAD, será obrigatório 
        passar o caminho do arquivo no parâmetro "filename".
        Caso o tipo de transferência seja DOWNLOAD, será obrigatório 
        passar um diretório para salvar o arquivo no parâmetro "path".

        O parâmetro "mode" deve ser FileTransfer.CLIENT ou FileTransfer.HOST.
        """

        self.changeMode(mode)
        self.changeFileName(filename)
        self.changePath(path)
        self.__socket = socket.socket()


    def changeFileName(self,filename):
        """
        Método para trocar o nome do arquivo.
        """
        if self.__connected:
            raise ActiveConnectionException

        if not filename or exists(filename):
            self.__filename = filename
            self.FILENAME = self.__filename
        else: raise FileNotFoundError


    def changeMode(self,mode):
        """
        Método para trocar o modo de transferência.
        """
        if self.__connected: 
            raise ActiveConnectionException

        if mode in [self.__CLIENT,self.__HOST]:
            self.__mode = mode
            self.MODE = self.__mode
        else: raise ValueError("The mode parameter must be FileTransfer.CLIENT or FileTransfer.HOST")


    def changePath(self,path):
        """
        Método para trocar o diretório para salvar o arquivo baixado.
        """
        if self.__connected:
            raise ActiveConnectionException

        if not path or exists(path):
            self.__path = path
            self.PATH = self.__path
        else: raise FileNotFoundError


    def close(self):
        """
        Método para encerrar a conexão
        """
        self.__stop = True
        self.__socket.close()
        self.__running = False
        self.__connected = False


    def connect(self,address,family=socket.AF_INET,type_=socket.SOCK_STREAM):
        """
        Método para conectar-se. O parâmetro "address" deve ser uma 
        sequência contendo o IP e PORT NUMBER.

        Caso o tipo de conexão seja CLIENT, será retornado o nome do 
        arquivo e seu tamanho em bytes. Exemplo: ["hello world.txt","987"].
        Caso o tipo de conexão seja HOST, será retornado o endereço do Client.
        """


        if self.__connected:
            raise ActiveConnectionException

        self.__socket = socket.socket(family,type_)

        if self.__mode == self.CLIENT:
            
            # Verifica se existe um diretório para salvar o arquivo que será baixado
            if not self.__path: 
                raise TypeError("You must define a directory to save the file to.")
            
            # Realiza a conexão com o servidor
            self.__socket.connect(address)
            self.__connected = True

            # Recebe o nome e o tamanho do arquivo em bytes no formato b'filename?size'
            transferInfo = self.__socket.recv(1024).decode().split("?")
            self.__filename = transferInfo[0]
            self.__size = int(float(transferInfo[1]))

            # Retorna uma sequência contendo o nome e tamanho do arquivo
            return transferInfo

        elif self.__mode == self.HOST:

            # Verifica se existe um arquivo definido para enviar
            if not self.__filename: 
                raise TypeError("You must set a file name to upload.")
            
            # Cria o servidor
            self.__socket.bind(address)
            self.__socket.listen(1)

            # Obtêm a conexão e os dados do client
            newSocket,clientInfo = self.__socket.accept()
            self.__connected = True

            # Fecha a conexão antiga e o socket passa a ser a conexão com o usuário
            self.__socket.close()
            self.__socket = newSocket

            # Obtêm o tamanho do arquivo a ser enviado
            self.__size = getsize(self.__filename)

            # Envia para o client o nome do arquivo e o tamanho em bytes no formato b'filename?size' 
            transferInfo = "%s?%f"%(split(self.__filename)[-1],self.__size)
            self.__socket.send(transferInfo.encode())

            return clientInfo


    @staticmethod
    def getFormattedSize(bytes_):
        """
        Método estático para obter um tamanho em bytes formatado.
        """
        types = ["Bytes","KB","MB","GB","TB"]
        index = 0

        while bytes_ > 1024 and index < len(types):
            bytes_ /= 1024
            index += 1
        return bytes_,types[index]


    def transfer(self,progressFunction=None):
        """
        Método para inciar a transferência do arquivo.

        O parâmetro progressFunction (opcional) deve ser uma função contendo 
        obrigatóriamente um parâmetro para receber o progresso da transferência em porcentagem.
        """

        if self.__running: return

        if not self.__connected:
            raise NoConnectionException

        self.__running = True
        self.__stop = False

        if self.__mode == self.CLIENT:

            # Essa variável irá guardar a quantidade de bytes recebidos
            received = 0

            # Cria um arquivo e um bufferWriter para salvar os dados do arquivo baixado
            file = io.FileIO(normpath(self.__path+"/"+self.__filename),'wb')
            bufferedWriter = io.BufferedWriter(file,self.__size)

            # Envia uma confirmação de que está pronto para receber os dados
            self.__socket.send(self.__OK.encode())

            while not self.__stop:
                try:
                    data = self.__socket.recv(1024)
                except:
                    break
                
                # Sai do bloco while caso o dado informe que este é o fim da transferência
                if data == self.__END.encode():
                    break

                # Escreve os dados no buffer
                bufferedWriter.write(data) 

                # Soma a quantidade de bytes recebidos
                received+=len(data)

                # Envia o progresso da transferência em porcentagem para a função
                if progressFunction:
                    progressFunction(100/self.__size*received)

            # Fecha o buffer e o arquivo
            bufferedWriter.flush()
            bufferedWriter.close()
            self.__running = False

            # Informa que a transferência foi finalizada com sucesso.
            if data == self.__END.encode():
                return self.__OK
            else: 
                raise IncompleteTransferError

        elif self.__mode == self.HOST:

            # Essa variável irá guardar a quantidade de bytes enviados
            sent = 0

            # Cria um arquivo e um bufferReader para ler os dados do arquivo que será enviado
            file = io.FileIO(self.__filename,'rb')
            bufferedReader = io.BufferedReader(file)
            confirmation = None

            # Aguarda uma confirmação para começar a enviar os dados
            while confirmation != self.__OK and not self.__stop:
                confirmation = self.__socket.recv(1024).decode()
            
            # Começa a enviar os dados do arquivo
            for data in bufferedReader.readlines():
                if self.__stop: break
                try:
                    self.__socket.send(data)
                except:
                    raise IncompleteTransferError

                # Soma a quantidade de bytes enviados
                sent+=len(data)

                # Envia o progresso da transferência em porcentagem para a função
                if progressFunction:
                    progressFunction(100/self.__size*sent)

            # Informa que todos os dados do arquivo foram enviados.
            self.__socket.send(self.__END.encode())

            # Fecha o buffer e o arquivo
            bufferedReader.close()
            self.__running = False

            # Informa que a transferência foi finalizada com sucesso
            return self.__OK



        
