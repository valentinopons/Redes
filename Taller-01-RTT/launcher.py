import subprocess
import time
import sys

address = "127.0.0.1"

processes = []

# Solo ploteamos en el primer proceso, el resto estan para saturar la red
plot_proc = subprocess.Popen([
    sys.executable, "ping_client.py",
    "--plot",
    "--duration", "30",
    "--window_size", "5000",
    "--address", address
])
processes.append(plot_proc)

time.sleep(5)

# COMPLETAR con el lanzamiento de ráfagas de procesos

# Esperamos a que terminen todos los subprocesos antes de cerrar el programa
for p in processes:
    p.wait()
