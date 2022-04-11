import subprocess

process = []

while True:
    ACTION = input('Выберите действие: q - выход, '
                   's - запустить сервер и клиенты, x - закрыть все окна: ')

    if ACTION == 'q':
        break
    elif ACTION == 's':
        process.append(subprocess.Popen('python server.py',
                                        creationflags=subprocess.CREATE_NEW_CONSOLE))
        for i in range(2):
            process.append(subprocess.Popen('python client.py -m send',
                                            creationflags=subprocess.CREATE_NEW_CONSOLE))
        for i in range(2):
            process.append(subprocess.Popen('python client.py -m listen',
                                            creationflags=subprocess.CREATE_NEW_CONSOLE))
    elif ACTION == 'x':
        while process:
            victim = process.pop()
            victim.kill()
