import socket
import os
import time
import argparse
import collections
import common

parser = argparse.ArgumentParser()

parser.add_argument("--address", type=str, default="127.0.0.1", help="Direccion del servidor")
parser.add_argument("--file", type=str, default="tux.bmp", help="Archivo a enviar")
parser.add_argument("--timeout", type=float, default=0.5, help="Timeout en segundos")
parser.add_argument("--window-size", type=int, default=16, help="Tamaño de ventana")

args = parser.parse_args()

chunks = common.split_file_in_chunks(args.file)

total = len(chunks)
last_chunk = len(chunks) - 1
addr = (args.address, 12002)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(args.timeout)
print(f"enviando {os.path.basename(args.file)} en {total} frames")

last_ack_recvd = -1
last_frame_sent = -1

# los timers son tuplas (momento_de_procesamiento, secuencia_a_retransmitir)
Timer = collections.namedtuple('Timer', ['when', 'sequence_number'])
timers = []

def send_chunk_and_add_timer(chunk_index):
    is_last = chunk_index == last_chunk
    frame = common.encode_slidingwindow_data_frame(is_last, chunk_index, chunks[chunk_index])
    sock.sendto(frame, addr)
    # Esperar al menos args.timeout segundos para retransmitir el frame
    timers.append(Timer(when=time.time() + args.timeout, sequence_number=chunk_index))

while last_ack_recvd != last_chunk:
    # print(f"LAR = {last_ack_recvd}, LFS = {last_frame_sent}")

    # Paso 1: reenvío frames pendientes que no hayan recibido acknowledge
    while timers and timers[0].when <= time.time():
        (_, sequence_number) = timers.pop(0)
        if sequence_number < last_ack_recvd:
            # Desestimo el timer, el frame ya recibió acknowledgement
            continue
        print(f"Resending {sequence_number}")
        send_chunk_and_add_timer(sequence_number)

    # Paso 2: envío frames nuevos hasta que se llene el buffer
    while last_frame_sent - last_ack_recvd < args.window_size:
        if last_frame_sent == last_chunk:
            # Todos los frames fueron enviados. A lo sumo va a haber que reenviarlos
            break
        last_frame_sent += 1
        send_chunk_and_add_timer(last_frame_sent)

    # Espero a recibir un acknowledge
    try:
        raw_data = sock.recv(common.SLIDINGWINDOW_ACK_FRAME_SIZE)
        (sequence_number,) = common.decode_slidingwindow_ack_frame(raw_data)

        # Actualizo last_ack_recvd si se recibió un sequence_number mayor
        last_ack_recvd = max(last_ack_recvd, sequence_number)

        # print(f"Got ack for {sequence_number}, LAR={last_ack_recvd}")
    except socket.timeout:
        print('Got timeout')

print("transferencia terminada")
sock.close()

