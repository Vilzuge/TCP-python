import threading
import socket

IP = socket.gethostbyname(socket.gethostname())
PORT = 5050
ADDR = (IP, PORT)
HEADER = 10

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
server.listen()

clients = []
nicknames = []

#takes strings and broadcasts
def broadcast(message, sending_client):
    try:
        for client in clients:
            if client != sending_client:
                client.send(message)
    #if something went wrong with broadcasting
    except Exception as e:
        print('Broadcast Error: ' + format(str(e)))

def handle(client):
    while True:
        try:
            #receiving messages from the client
            user_header = client.recv(HEADER)
            user_length = int(user_header.decode('utf-8').strip())
            user_content = client.recv(user_length)

            msg_header = client.recv(HEADER)
            msg_length = int(msg_header.decode('utf-8').strip())
            msg_content = client.recv(msg_length)

            #broadcast message
            broadcast(user_header + user_content + msg_header + msg_content, client)

            #if a user left, tell clients
            if (msg_content.decode("utf-8") == "/q"):
                index = clients.index(client)
                nickname = nicknames[index]

                user = 'SERVER'.encode('utf-8')
                user_header = f"{len(user):<{HEADER}}".encode('utf-8')
                msg_bye = f'{nickname} left the chatroom!'.encode('utf-8')
                header_bye = f"{len(msg_bye):<{HEADER}}".encode("utf-8")
                broadcast(user_header + user + header_bye + msg_bye, client)
                print(nickname + " left the chatroom.")
                clients.remove(client)
                client.close()
                nickname = nicknames[index]
                nicknames.remove(nickname)
                break

        except Exception as e:
            #if we get something weird from the client, kick him out
            print('Server Handle Error: ' + format(str(e)))
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            nicknames.remove(nickname)
            break

def receive():
    while True:
        #we get to know to the new client, store it and the nickname and start threading with handle()
        #if this operation fails, jump out and 
        try:
            #accepting connection
            client, address = server.accept()
            print(f"Connected with {str(address)}")

            #getting the nickname
            user = 'SERVER'.encode('utf-8')
            user_header = f"{len(user):<{HEADER}}".encode('utf-8')
            nick = '/nickname'.encode('utf-8')
            nick_header = f"{len(nick):<{HEADER}}".encode('utf-8')
            client.send(user_header + user + nick_header + nick)

            #storing the nickname
            nick_header = client.recv(HEADER)
            nick_length = int(nick_header.decode("utf-8").strip())
            nickname = client.recv(nick_length).decode('utf-8')

            if nickname in nicknames:
                print("Nickname already taken..")
                break
            
            #appending the client and the nickname
            nicknames.append(nickname)
            clients.append(client)

            #telling others about the new chatter
            print(f'New user entered with the nickname: {nickname}')
            user = 'SERVER'.encode('utf-8')
            user_header = f"{len(user):<{HEADER}}".encode('utf-8')
            msg_welcome = f'{nickname} joined the chatroom!'.encode('utf-8')
            header_welcome = f"{len(msg_welcome):<{HEADER}}".encode("utf-8")
            broadcast(user_header + user + header_welcome + msg_welcome, client) #broadcast join event

            thread = threading.Thread(target=handle, args=(client,))
            thread.start()
        except Exception as e:
            print('Server receive Error: ' + format(str(e)))
            pass

print(f"Server is listening on {IP}/{PORT}...")
receive()