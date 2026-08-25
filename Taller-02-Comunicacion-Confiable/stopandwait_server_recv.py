import socket
import random
import argparse
import time
import common

parser = argparse.ArgumentParser()

parser.add_argument("--file", type=str, default="out.bmp", help="Archivo a guardar")
parser.add_argument("--delay", type=float, default=0.0, help="Simula un delay al enviar frames (tanto de emisor como de receptor)")
parser.add_argument("--loss", type=float, default=0.01, help="Probabilidad de pérdida de un frame")

args = parser.parse_args()
out_filename = args.file

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", 12001))
with open(out_filename, "wb") as out:
    while True:
        raw_data, addr = sock.recvfrom(common.STOPANDWAIT_DATA_FRAME_SIZE)
        time.sleep(args.delay)
        (is_last, data) = common.decode_stopandwait_data_frame(raw_data)
        
        if random.random() < args.loss:
            print(f"Simulando perdida de frame de datos")
            continue

        ack_frame = common.encode_stopandwait_ack_frame()
        if random.random() < args.loss:
            print(f"Simulando perdida de frame de acknowledgement")
        else:
            sock.sendto(ack_frame, addr)
            time.sleep(args.delay)

        out.write(data)
        out.flush()

        if is_last:
            print("ultimo frame -> terminamos")
            break

print(f"Descarga guardada en {out_filename}")
sock.close()

