import threading
import socket
import sys

port = 5050
HEADER = 10
server = input("Server IP (from servers information): ")
while True:
    nickname = input("Choose a nickname: ")
    if (nickname == 'SERVER'):
        print("Choose another nickname!")
    else:
        break

while True:
    print("Choose a channel to connect to: ")
    print("1) General")
    print("2) Videogames")
    choise = input("Choise: ")
    if choise == "1":
        channel = "general"
        break
    elif choise == "2":
        channel = "videogames"
        break
    else:
        print("Choose a valid channel!")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((server, port))

#Client receiving from the server
def receive():
    while True:
        try:
            #receiving messages from the server
            user_header = client.recv(HEADER)
            user_length = int(user_header.decode('utf-8').strip())
            user_content = client.recv(user_length)

            channel_header = client.recv(HEADER)
            channel_length = int(channel_header.decode('utf-8').strip())
            channel_content = client.recv(channel_length)

            msg_header = client.recv(HEADER)
            msg_length = int(msg_header.decode('utf-8').strip())
            msg_content = client.recv(msg_length)

            split_msg = msg_content.decode('utf-8').split()
            chan = channel_content.decode('utf-8')

            #if server asked for our nickname, automatically return our nick with header
            if (msg_content.decode('utf-8') == '/nickname' and user_content.decode('utf-8') == 'SERVER'):
                nick_answer = nickname.encode("utf-8")
                nick_header = f"{len(nick_answer):<{HEADER}}".encode("utf-8")
                channel_answer = channel.encode("utf-8")
                channel_header = f"{len(channel_answer):<{HEADER}}".encode("utf-8")
                client.send(nick_header + nick_answer + channel_header + channel_answer)

            #if private message but not for us
            elif (split_msg[0][0] == "/" and split_msg[0] != "/"+nickname):
                pass

            #if private message and is for us
            elif (split_msg[0][0] == "/" and split_msg[0] == "/"+nickname):
                message = ""
                for i in split_msg:
                    if i[0] == "/":
                        continue
                    else:
                        message = message + " " + i
                print(f'\nWhisper from <{user_content.decode("utf-8")}>: {message}')

            #dont print if message is from different channel
            elif (chan != channel):
                pass

            #Print the message for everyone
            else:
                print("\n" + user_content.decode('utf-8') + " >>> " + msg_content.decode('utf-8'))

        except Exception as e:
            print('Client receive Error: ' + format(str(e)))
            client.close()
            break

def write():
    while True:
        try:
            sender = nickname.encode("utf-8")
            sender_header = f"{len(sender):<{HEADER}}".encode("utf-8")
            new_msg = input(f"{nickname} at ({channel})>> ")
            message = new_msg.encode("utf-8")
            message_header = f'{len(message):<{HEADER}}'.encode("utf-8")
            ch = channel.encode("utf-8")
            channel_header = f'{len(ch):<{HEADER}}'.encode("utf-8")

            client.send(sender_header + sender + channel_header + ch + message_header + message)

            if (message.decode("utf-8") == '/q'):
                print("Thanks for chatting, see you soon!")
                client.close()
                sys.exit(0)

        except Exception as e:
            #if getting the info fails, close connection
            print('Client Write Error: ' + format(str(e)))
            client.close()
            break


receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()