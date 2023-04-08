'''
Example:
    1. Finish the server, and run it in an arbitrary directory.
    ```sh
    sudo python server.py
    ```

    2. In another directory, download any file in the folder.
    ```sh
    ftp -Aa 127.0.0.1:server.py
    ```
    In this example we download the script itself.

Remember to rename it.
'''
import threading
import socket
import hashlib
import json
import os
import secrets
import string
import codecs

random = secrets.SystemRandom()

passwd_map = {}
is_end = False

class ftp_DTP:
    # data_addr: tuple(int: ipv4/6, str: ip, int: port)
    def __init__(self, addr: tuple):
        self.data_addr = addr
        # self.client.connect((addr[1],addr[2]))

        
    def send_file(self, wclient: socket.socket, file: str, data_type):
        if os.path.isfile(file):
            try:
                if self.data_addr[0] == 1:
                    self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                else:
                    self.client = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                self.client.settimeout(5.0)
                self.client.connect((self.data_addr[1], self.data_addr[2]))
                # wclient.send(b'200 Active data connection established.\r\n')
                wclient.send(b'125 Data connection already open. Transfer starting.\r\n')
            except:
                wclient.send(b'425 Cannot open Data connection\r\n')
                return
            try:
                if data_type == 'I':
                    f = open(file, 'rb')
                elif data_type == 'A':
                    f = open(file, 'r')
                elif data_type == 'E':
                    f = codecs.open(file, mode='r', encoding='cp1047')
                else:
                    self.client.close()
                    wclient.send(b'550 Requested action not taken. File type unavaliable.\r\n')
                    return
                    
            except:
                self.client.close()
                wclient.send(b'550 Requested action not taken. File unavailable.\r\n')
                return
            try:
                data = f.read()
                self.client.send(data)
            except:
                f.close()
                self.client.close()
                wclient.send(b'426 Connection closed; transfer aborted.\r\n')
                return
            f.close()
            self.client.close()
            wclient.send(b'226 Transfer complete.\r\n')
            return
        else:
            wclient.send(b'550 Requested action not taken. File unavailable.\r\n')
            return
    
    def recv_file(self, wclient: socket.socket, file: str, data_type):
        # print('recv: ', self.data_addr, file)
        
        if not os.path.isfile(file):
            try:
                f = open(file, 'x')
                f.close()
            except:
                # print('failed')
                wclient.send(b'550 Requested action not taken. File unavailable.\r\n')
                return
        try:
            if self.data_addr[0] == 1:
                self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            else:
                self.client = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            self.client.settimeout(5.0)
            self.client.connect((self.data_addr[1], self.data_addr[2]))
            # wclient.send(b'200 Active data connection established.\r\n')
            wclient.send(b'125 Data connection already open. Transfer starting.\r\n')
        except:
            print('connetion failed: ', self.data_addr)
            wclient.send(b'425 Cannot open Data connection\r\n')
            return
        if os.path.isfile(file):
            try:
                if data_type == 'I':
                    f = open(file, 'wb')
                elif data_type == 'A':
                    f = open(file, 'w')
                elif data_type == 'E':
                    f = codecs.open(file, mode='w', encoding='cp1047')
                else:
                    self.client.close()
                    # print('error file type')
                    wclient.send(b'550 Requested action not taken. File type unavaliable.\r\n')
                    return
            except:
                self.client.close()
                # print('error open file')
                wclient.send(b'550 Requested action not taken. File unavailable.\r\n')
                return
            try:
                while True:
                    data = self.client.recv(4096)
                    # print('data: ', data)
                    f.write(data)
                    if len(data) != 4096:
                        break
            except socket.error as e:
                print(e)
                f.flush()
                f.close()
                self.client.close()
                # print('abort')
                wclient.send(b'426 Connection closed; transfer aborted.\r\n')
                return
            f.flush()
            f.close()
            self.client.close()
            wclient.send(b'226 Transfer complete.\r\n')
            return
        else:
            self.client.close()
            wclient.send(b'550 Requested action not taken. File unavailable.\r\n')
            return


def ftp_PI(client: socket.socket, addr: tuple):
    # Send welcome message
    global is_end
    print('new user: ', addr)
    dtp = None
    client.send(b"220 12112012 ready\r\n")
    line = client.recv(1024).decode('ascii').strip()
    user_name = str()
    data_addr = tuple()
    is_login = False
    mode_char = 'I'
    try:
        while line != "QUIT" and not is_end:
            print('line: ', line)
            if line[:4] == "USER":
                user_name = line[4:].strip()
                if user_name:
                    client.send(b'331 Username ok, send password.\r\n')
                else:
                    client.send(b'430 Invalid username.\r\n')
                is_login = False
                pass
            
            elif line[:4] == "PASS":
                passwd = line[4:].strip()
                if passwd_map.__contains__(user_name):
                    stdwd = passwd_map[user_name]
                    if hashlib.sha256((passwd+stdwd[0]).encode()).hexdigest() == stdwd[1]:
                        client.send(b'230 Login successful\r\n')
                        is_login = True
                    else:
                        client.send(b'430 Invalid username or password\r\n')
                        is_login = False
                else:
                    client.send(b'430 Invalid username or password\r\n')
                    is_login = False
                pass

            elif line[:4] == "PORT":
                if not is_login:
                    client.send(b'530 Not logged in.\r\n')
                else:
                    tmp = line[4:].strip().split(',')
                    if len(tmp) != 6:
                        client.send(b'425 Can\'t open data connection.\r\n')
                    data_addr = (1,
                                tmp[0] + '.' + tmp[1] + '.' + tmp[2] + '.' + tmp[3],
                                int(tmp[4]) * 256 + int(tmp[5]))
                    dtp = ftp_DTP(data_addr)
                    client.send(b'200 port ready.\r\n')
                    # Parse the data coonection ip and port
                pass

            elif line[:4] == "EPRT":
                if not is_login:
                    client.send(b'530 Not logged in.\r\n')
                else:
                    tmp = line[4:].strip().split('|')
                    data_addr = (int(tmp[1]),
                                tmp[2],
                                int(tmp[3]))
                    dtp = ftp_DTP(data_addr)
                    client.send(b'200 port ready.\r\n')
                    # Same as PORT
                pass

            elif line[:4] == "STOR":
                if not is_login:
                    client.send(b'530 Not logged in.\r\n')
                elif passwd_map[user_name][2] == 0: # user privilege
                    client.send(b'550 Permission Denied.\r\n')
                else:
                    # client.send(b'125 Data connection already open. Transfer starting.\r\n')
                    dtp.recv_file(client, line[4:].strip(), mode_char)
                    # Establish data connection
                pass

            elif line[:4] == "RETR":
                if not is_login:
                    client.send(b'530 Not logged in.\r\n')
                else:
                    # client.send(b'125 Data connection already open. Transfer starting.\r\n')
                    dtp.send_file(client, line[4:].strip(), mode_char)
                pass

            elif line[:4] == "SIZE":
                if not is_login:
                    client.send(b'530 Not logged in.\r\n')
                else:
                    size = os.path.getsize(line[4:].strip())
                    client.send("213 {}\r\n".format(size).encode())
            
            elif line[:4] == "SYST":
                client.send(b"215 UNIX Type: L8\r\n")
            
            elif line[:4] == "TYPE":
                if not is_login:
                    client.send(b'530 Not logged in.\r\n')
                else:
                    se_ch = line[4:].strip()
                    if se_ch == 'I':
                        mode_char = se_ch
                        client.send(b'200 Type set to binary.\r\n')
                    elif se_ch == 'A':
                        mode_char = se_ch
                        client.send(b'200 Type set to ascii.\r\n')
                    elif se_ch == 'E':
                        mode_char = se_ch
                        client.send(b'200 Type set to ebcdic.\r\n')
                    else:
                        client.send(b'504 Command not implemented for that parameter.\r\n')
                        

            else:
                client.send(b'502 Command not implemented.\r\n')

            line = client.recv(1024).decode('ascii').strip()
        
        print('bye')
        if is_end: # server shutdown
            client.send(b'421 Service not available, closing control connection.\r\n')
        else:
            client.send(b'221 Goodbye\r\n')
        client.close()
    
    except:
        client.close()
        pass
    
# read users from file in json
def read_user():
    if not os.path.isfile('user_passwd.json'):
        with open('user_passwd.json', 'x') as w:
            w.write('{}')
    with open('user_passwd.json', 'r') as f:
        J = json.load(f)
        return J

# save users into file
def save_user():
    with open('user_passwd.json', 'w') as f:
        json.dump(passwd_map, f)

# process input
def input_process():
    global is_end
    while not is_end:
        comm = input()
        if comm == "user": # add an new user
            user_name = input('username: ')
            passwd = input('passwd: ')
            pri = input('privilege: ')
            salt = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            passwd_map[user_name] = (salt, hashlib.sha256((passwd+salt).encode()).hexdigest(), pri)
            save_user()
        if comm == "end": # end the server
            is_end = True

if __name__ == '__main__':
    passwd_map = read_user()
    # Listening on port 52305
    try: # If the port has been used, then just quit
        s = socket.socket()
        s.bind(("127.0.0.1", 52305))
        s.listen(5)
        s.settimeout(5.0)
        threading.Thread(target=input_process).start()

        while not is_end:
            try:
                client, addr = s.accept()
                # Give every user an thread to ensure responsible
                threading.Thread(target=ftp_PI, args=(client, addr)).start()
            except socket.timeout: # every 5 seconds check if server will quit
                pass
            if is_end:
                break
    except:
        pass
    is_end = True
    s.close()
