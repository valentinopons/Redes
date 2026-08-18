import time
import socket
import numpy as np
import matplotlib.pyplot as plt
import argparse
import os

parser = argparse.ArgumentParser()

parser.add_argument("--plot", action="store_true", help="Plotear RTT")
parser.add_argument("--duration", type=float, default=30.0, help="Tiempo de ejecucion en segundos")
parser.add_argument("--window_size", type=int, default=5000, help="Tamaño de ventana para media movil")
parser.add_argument("--address", type=str, default="127.0.0.1", help="Direccion del servidor")
parser.add_argument("--port", type=int, default=12000, help="Puerto del servidor")

args = parser.parse_args()
pid = os.getpid()

print(f"Arrancando pid: {pid} con args: {args}")

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.settimeout(1.0)
addr = (str(args.address), int(args.port))

def send_ping():
    start = time.time()
    client_socket.sendto(f"ping de {pid}".encode("utf-8"), addr)
    response, server = client_socket.recvfrom(1024)
    rtt = time.time() - start
    return rtt

def moving_average(x, y, n):
    """
    Calcula la media móvil de y con tamaño de ventana n.
    Devuelve x, y, e y_avg (que es y una vez que se le aplica la media móvil).
    Basado en: https://stackoverflow.com/questions/14313510/how-can-i-calculate-a-rolling-moving-average-using-python-numpy-scipy
    """
    avg = np.cumsum(y, dtype=float)
    avg[n:] = avg[n:] - avg[:-n]
    avg = avg[n - 1:] / n
    return x[n-1:], y[n-1:], avg

def plot(data):
    """
    Dada una lista de tuplas (t, r) donde t es el momento en que se recibió un
    paquete (medido en segundos, relativo al inicio del programa) y r es el
    RTT obtenido, grafica los resultados usando matplotlib.
    """
    times = np.array([t for (t, r) in data])
    rtts = np.array([r for (t, r) in data])
    times, rtts, rtts_avg = moving_average(times, rtts, args.window_size)
    plt.figure()
    # Descomentar para ver los resultados sin media móvil
    plt.plot(times, rtts, label='rtt')
    plt.plot(times, rtts_avg, label='media móvil')
    plt.xlabel("Tiempo desde inicio (s)")
    plt.ylabel("RTT (s)")
    plt.ylim(bottom=0)
    plt.tight_layout()
    plt.legend()
    plt.show()


start = time.time()

# COMPLETAR
# Se puede consultar los argumentos del programa usando args.duration, args.window_size, etc.
rtts = []
while time.time() - start < args.duration:
    rtt = send_ping()
    time1 = time.time()
    rtts.append((time1, rtt))
if args.plot:
    plot(rtts)
