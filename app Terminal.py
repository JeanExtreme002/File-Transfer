from fileTransfer import FileTransfer
import keyboard
import os

def showProgress(percent,size=25):
    """
    Função para mostrar o progresso da transferência.
    """

    global filename,mode
    size /= 100
    percent = int(percent)

    if mode == 1:
        print('\r Sending "{}" ... {}% [{}{}] '.format(filename,percent,"#"*int((percent*size))," "*int(((100*size)-percent*size))),end="")
    else:
        print('\r Downloading "{}" ... {}% [{}{}] '.format(filename,percent,"#"*int((percent*size))," "*int(((100*size)-percent*size))),end="")


filename = None
filename_size = 20
ip = None
mode = None
path = None
port = None


# Pergunta ao usuário se ele deseja enviar ou fazer 
# download de um arquivo e aguarda a sua resposta.

print("\n What do you want to do ?\n 1: Upload\n 2: Download")

while not mode:
    if keyboard.is_pressed("1"):
        mode = 1
    elif keyboard.is_pressed("2"):
        mode = 2
keyboard.press("backspace")


# Pede para que o usuário insira o IP e o PORT NUMBER, 
# verificando se o PORT é válido.

ip = input("\n\n Enter the IP: ")

while not port:
    try:
        port = int(input("\n Enter the Port: "))
    except:
        input(" You entered an invalid value.")

# Pede para que o usuário insira um caminho de pasta ou arquivo.
while not path:

    # Se o usuário desejar enviar um arquivo, será pedido o nome do arquivo.
    # Após isso, será verificado se este arquivo existe ou não.

    if mode == 1:
        input_ = input("\n Enter the file name to upload: ")

        if os.path.exists(input_):
            path = input_
        else:
            input(" Could not find this file.")

    # Se o usuário desejar fazer download de um arquivo, será pedido o caminho
    # de uma pasta para que o arquivo baixado seja salvo.

    else:
        input_ = input("\n Enter a directory to save the file: ")

        if not input_:
            path = os.getcwd()
        else:
            if os.path.isdir(input_):
                path = input_
            else:
                input(" Could not find this directory.")

print("\n")

# Inicia uma conexão de Host ou Client utilizando 
# as informações passadas pelo usuário. 

if mode == 1:
    fileTransfer = FileTransfer(filename=path,mode=FileTransfer.HOST)
    print(" Awaiting connection ...")
else:
    print(" Connecting ...")
    fileTransfer = FileTransfer(path=path,mode=FileTransfer.CLIENT)
try:
    info = fileTransfer.connect((ip,port))
except:
    input(" Failed to attempt to connect.")
    quit()


# Caso o usuário esteja enviando um arquivo, ele será 
# informado de que precisa esperar a confirmação do cliente.
# Após a confirmação, o arquivo será enviado.

if mode == 1:
    print(" Awaiting confirmation of {} ...".format(info[0]))
    filename = os.path.split(path)[-1]

    # Verifica se o tamanho do nome do arquivo é maior que o tamanho limite. Se sim, ele será reduzido.
    if len(filename.split(".")[0]) > filename_size:
        filename = filename.split(".")[0][0:filename_size]+"."+filename.split(".")[-1]

    try:
        fileTransfer.transfer(showProgress)
        print("")
        input("\n Transfer completed successfully.\n\n")
    except:
        input("\n Connection terminated.\n\n")
    finally:
        fileTransfer.close()


# Caso o usuário queira fazer download um arquivo, serão mostradas
# as informações do arquivo para que o usuário confirme se está tudo bem.
# Após a confirmação, o arquivo será recebido.

else:

    # Formata o tamanho do arquivo adequadamente.
    size = int(float(info[1]))
    size = FileTransfer.getFormattedSize(size)

    filename = info[0]

    # Verifica se o tamanho do nome do arquivo é maior que o tamanho limite. Se sim, ele será reduzido.
    if len(filename.split(".")[0]) > filename_size:
        filename = filename.split(".")[0][0:filename_size]+"."+filename.split(".")[-1]

    print('\n Do you want to download "%s" [%.2f %s] ? (Y/N)'%(filename,size[0],size[1]))

    # Aguarda pela resposta do usuário.
    resp = None
    while not resp:
        if keyboard.is_pressed("y") or keyboard.is_pressed("Y"):
            resp = 1
        if keyboard.is_pressed("n") or keyboard.is_pressed("N"):
            resp = 0
    keyboard.press("backspace")

    # Fecha a conexão e o programa caso o usuário não aceite o arquivo.
    if resp == 0:
        fileTransfer.close()
        quit()

    # Inicializa a transferência.
    try:
        fileTransfer.transfer(showProgress)
        print("")
        input("\n Transfer completed successfully.\n\n")
    except:
        print("")
        input("\n A failure occurred during the transfer.\n\n")
    finally:
        fileTransfer.close()



