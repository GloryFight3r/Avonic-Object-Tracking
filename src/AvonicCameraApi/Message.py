import socket
import time

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
address = ('192.168.5.93', 80)

def send(header, command, data):
    header = bytes.fromhex(header)
    command = bytes.fromhex(command)
    data = bytes.fromhex(data)
    message = header + command + data + bytes([sum(header + command + data) & 0xFF])

    sock.sendall(message)

    data2 = sock.recv(3)

    return data2

def move_right():
    return send_message('', '8101060110100203FF', '')

def move_left():
    return send_message('', '8101060110100103FF', '')

def stop():
    send_message('', '8101060105050303FF', '')

def home():
    return send_message('', '81 01 06 04 FF', '')

def main():
    sock.connect(address)

    # Define VISCA message
    #while True:
    #    x = input()
    #    if x == 'a':
    #        move_left()
    #    elif x == 'd':
    #        move_right()
    #    elif x == 'x':
    #        stop()
    #    elif x == 'h':
    #        home()
    #    elif x == 'z':
    #        break

    #    time.sleep(1)

    #sock.close()

main()
