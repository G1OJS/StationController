import socket

class rigctrld:
    def get_frequency(host='localhost', port=4532):
        with socket.create_connection((host, port)) as sock:
            sock.sendall(b'f\n')
            response = sock.recv(1024)
            return int(response.strip())

    #print(get_frequency())


    def set_frequency(freq_hz, host='localhost', port=4532):
        cmd = f'F {int(freq_hz)}\n'
        with socket.create_connection((host, port)) as sock:
            sock.sendall(cmd.encode())
            response = sock.recv(1024)
            print(response.decode().strip())

    # Example: Set to 14.074 MHz (FT8)
    # set_frequency(14074000)

    def rigctl_session(commands, host='localhost', port=4532):
        with socket.create_connection((host, port)) as sock:
            for cmd in commands:
                sock.sendall((cmd + '\n').encode())
                print(sock.recv(1024).decode().strip())

    #rigctl_session([
    #    'F 7074000',   # 7.074 MHz for FT8 on 40m
    #    'M USB 3000'   # Set mode to USB
    #])
