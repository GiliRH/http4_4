import os
import socket, threading

exts_txt = ['.js', '.txt', '.css']
exts_bin = ['.html', '.jpg', '.gif', '.ico']

moved_302 = {'A/dog.jpg': 'B/dog.jpg', 'B/dog.jpg': 'B/dog2.jpg'}

exit_all = False

PROTOCOL = 'HTTP1.1'
STRINGDIR = "E:\cyber\Commu\Python\\4_4proj\webroot"


def check_HTTP(url):
    url_list = url.split()
    if url_list[0] != "GET ":
        return False
    if url_list[1] != "HTTP/1.1\r\n":
        return False
    return True


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
    if(not is_valid_url(st)):
        exit_all = True
        return "ERR", "not valid url"
    header = ""
    if ("HTTP/1.0" in st):
        PROTOCOL = "HTTP/1.0"
    if("HTTP/1.1" in st):
        PROTOCOL = "HTTP/1.1"
    else:
        return "ERR", "HTTP err"
    body = st.strip("GET ")
    body = st.strip(header + "\r\n")
    return PROTOCOL, st


def get_type_header(requested_file):
    print("path: ", requested_file)
    type_file = requested_file.split('.')
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


def get_file_data(requested_file):
    with open(requested_file, 'rb') as f:
        b = f.read()



def handle_request(request_header, body):
    """ Check the required resource, generate proper HTTP response and send to client"""
    # TO DO : add code that given a resource (URL and parameters) generates the proper response
    pass

    # TO DO: check if URL had been redirected, not available or other error code. For example:
    # if url in REDIRECTION_DICTIONARY:
    # TO DO: send 302 redirection response

    # TO DO: extract requested file tupe from URL (html, jpg etc)
    print("url:", url)
    http_header = check_contents_type(url)
    # TO DO: handle all other headers

    # TO DO: read the data from the file
    data = get_file_data(url)
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
    main()


