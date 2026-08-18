import socket
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("--port", type=int, default=12000, help="Puerto del servidor")

args = parser.parse_args()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('0.0.0.0', args.port))

print(f'Escuchando conexiones en el puerto {args.port}...')

while True:
    message, address = server_socket.recvfrom(1024)
    _ping = message.decode("utf-8")
    # print(f'Recibido: {_ping} @ {address[0]}:{address[1]}')
    server_socket.sendto(b"pong!", address)