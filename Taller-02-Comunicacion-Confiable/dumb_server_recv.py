import socket
import random
import argparse
import common

parser = argparse.ArgumentParser()

parser.add_argument("--file", type=str, default="out.bmp", help="Archivo a guardar")
parser.add_argument("--loss", type=float, default=0.01, help="Probabilidad de pérdida de un frame")

args = parser.parse_args()
out_filename = args.file

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", 12000))
last_seqno = None
with open(out_filename, "wb") as out:
    while True:
        raw_data, addr = sock.recvfrom(common.DUMB_DATA_FRAME_SIZE)
        (is_last, data) = common.decode_dumb_data_frame(raw_data)
        
        if random.random() < args.loss:
            print(f"Simulando perdida de frame de datos")
            continue

        out.write(data)
        out.flush()

        if is_last:
            print("ultimo frame -> terminamos")
            break

print(f"Descarga guardada en {out_filename}")
sock.close()

