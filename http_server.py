# Ex 4.4 - HTTP Server Shell
# Author: Barak Gonen
# Purpose: Provide a basis for Ex. 4.4
# Note: The code is written in a simple way, without classes, log files or other utilities, for educational purpose
# Usage: Fill the missing functions and constants

# TO DO: import modules
import socket
import threading
import os

# TO DO: set constants
IP = '0.0.0.0'
PORT = 80
SOCKET_TIMEOUT = 0.1
DEFAULT_URL = "index.html"
PROTOCOL = "HTTP/1.1"


def is_valid_url(url):
    data = url.split('\r\n')
    data = data[0].split()
    if data[0].upper() == "GET " and data[-1].upper() == PROTOCOL:
        return True
    return False


def http_send(s, reply_header, reply_body):
    reply = reply_header.encode()
    if reply_body != b'':
        try:
            body_length = len(reply_body)
            reply_header += 'Content-Length: ' + str(body_length) + '\r\n' + '\r\n'
            reply = reply_header.encode() + reply_body
        except Exception as e:
            print(e)
    else:
        reply += b'\r\n'
    s.send(reply)
    print('SENT:', reply[:min(100, len(reply))])


def http_recv(sock, BLOCK_SIZE=8192):
    st = sock.recv(BLOCK_SIZE)
    if not is_valid_url(st):
        exit_all = True
        return "ERR", "not valid url"
    close = False
    if "HTTP/1.0" in st:
        PROTOCOL = "HTTP/1.0"
        close = True
    if "HTTP/1.1" in st:
        PROTOCOL = "HTTP/1.1"
    body = st.strip("GET ")
    body = st.strip(PROTOCOL + "\r\n")
    return close, body


def check_contents_type(path):
    type_file = path.split('.')
    if type_file[1] == "html" or type_file[1] == "txt":
        return "Content-Type: text/html; charset=utf-8"
    if type_file[1] == "jpg":
        return "Content-Type: image/jpeg"
    if type_file[1] == "js":
        return "Content-Type: text/javascript; charset=utf-8"
    if type_file[1] == "css":
        return "Content-Type: text/css"
    else:
        return ""


def get_file_data(filename):
    """ Get data from file """
    if '/' in filename:
        requested_file = filename.replace('/','\\')
    try:
        with open("E:\webroot" + requested_file, 'rb') as f:
            b = f.read()
            return b
    except os.path.isfile as err:
        print("file does not exist")
        return "404 NOT FOUND"


def handle_client_request(resource, client_socket):
    """ Check the required resource, generate proper HTTP response and send to client"""
    # TO DO : add code that given a resource (URL and parameters) generates the proper response

    if resource == '':
        url = DEFAULT_URL
    else:
        url = resource

    # TO DO: check if URL had been redirected, not available or other error code. For example:
    # if url in REDIRECTION_DICTIONARY:
        # TO DO: send 302 redirection response

    # TO DO: extract requested file tupe from URL (html, jpg etc)
    http_header = check_contents_type(url)
    # TO DO: handle all other headers

    # TO DO: read the data from the file
    data = get_file_data(filename)
    http_response = http_header + data
    client_socket.send(http_response.encode())
    return


def handle_client(s_clint_sock, tid, addr):
    global exit_all
    print('new client arrive', tid, addr)
    while not exit_all:
        request_header, body = http_recv(s_clint_sock)
        if request_header == b'':
            print('seems client disconected, client socket will be close')
            break
        else:
            reply_header, body = handle_request(request_header, body)
            if PROTOCOL == "HTTP1.0":
                reply_header += "Connection': close\r\n"
            else:
                reply_header += "Connection: keep-alive\r\n"
            http_send(s_clint_sock, reply_header, body)
            if PROTOCOL == "HTTP1.0":
                break
    print("Client", tid, "Closing")
    s_clint_sock.close()


def main():
    # Open a socket and loop forever while waiting for clients
    global exit_all
    server_socket = socket.socket()
    server_socket.bind(('0.0.0.0', 80))
    server_socket.listen(5)
    threads = []
    tid = 1
    while True:
        try:
            # print('\nbefore accept')
            client_socket, addr = server_socket.accept()
            t = threading.Thread(target=handle_client, args=(client_socket, tid, addr))
            t.start()
            threads.append(t)
            tid += 1

        except socket.error as err:
            print('socket error', err)
            break
    exit_all = True
    for t in threads:
        t.join()

    server_socket.close()
    print('server will die now')


if __name__ == "__main__":
    # Call the main handler function
    main()