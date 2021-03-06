from flask import Flask, jsonify
from test_data import test_data
import threading
import socket
import ssl

app = Flask(__name__)

cert_file = '../cert.pem'
key_file = '../cert.pem'
tcp_tls_server_port = 8888
tcp_server_port = 8887
udp_server_port = 8886


@app.route('/integrationServices/v2/session', methods=['GET', 'POST'])
def session():
    return '{"sessionId":"348-5UH2SZ4S7GKA","success":true,"message":"Success"}'


@app.route('/integrationServices/v2/notification', methods=['GET', 'POST'])
def notification():
    #
    # Yes str vs json since this emulates what the Cb Defense returns
    #
    return jsonify(test_data)


class FuncThread(threading.Thread):
    def __init__(self, target, *args):
        self._target = target
        self._args = args
        threading.Thread.__init__(self)

    def run(self):
        self._target(*self._args)

def udp_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('0.0.0.0', udp_server_port)
    print "udp_server is listening on port {}".format(udp_server_port)
    sock.bind(server_address)

    while True:
        data, address = sock.recvfrom(4096)
        print address
        print len(data)
        print data


def tcp_server():
    # Create a TCP/IP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', tcp_server_port))
    server_socket.listen(1)
    print "tcp_server is listening on port {}".format(tcp_server_port)

    while True:
        new_client_socket, address = server_socket.accept()

        secured_client_socket = new_client_socket

        print new_client_socket, address
        buffer = secured_client_socket.recv(4096)
        print len(buffer)
        print buffer
        secured_client_socket.close()

def tcp_tls_server():

    # Create a TCP/IP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', tcp_tls_server_port))
    server_socket.listen(1)
    print "tcp_tls_server is listening on port {}".format(tcp_tls_server_port)

    while True:
        new_client_socket, address = server_socket.accept()

        secured_client_socket = ssl.wrap_socket(new_client_socket,
                                                server_side=True,
                                                certfile=cert_file,
                                                keyfile=key_file,
                                                ssl_version=ssl.PROTOCOL_TLSv1)

        print new_client_socket, address
        buffer = secured_client_socket.recv()
        print len(buffer)
        print buffer
        secured_client_socket.close()


def main():
    #
    # Create a listening server to test UDP, TCP and TCP/TLS
    #
    server1 = FuncThread(tcp_server)
    server2 = FuncThread(tcp_tls_server)
    server3 = FuncThread(udp_server)
    server1.start()
    server2.start()
    server3.start()
    #
    # Default port is 5000
    #
    app.run(host='0.0.0.0')

if __name__ == "__main__":
    main()
