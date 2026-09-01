#!/usr/bin/env python3
"""
fdb_monitor.py
Monitorea tablas MAC (learning MAC) de bridges OVS en intervalos regulares.

- Ejecuta: ovs-appctl fdb/show <bridge>
- Parsea: port, vlan, mac, age
- Emite: CSV con timestamp + bridge + cantidad de entradas + detalle por MAC

Uso típico:
  python3 fdb_monitor.py --bridges B1 B2 B3 --interval 1 --duration 60 --outdir results

Salida:
  results/fdb_monitor.csv
  (opcional) snapshots en results/fdb_<bridge>_<timestamp>.txt con --snapshots
"""

import argparse
import csv
import subprocess
import time
from datetime import datetime
from pathlib import Path


def now_iso():
    return datetime.now().isoformat(timespec="seconds")


def sh(cmd: str) -> str:
    p = subprocess.run(cmd, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        # No abortamos: registramos error para diagnóstico.
        return f"__ERROR__ {p.stderr.strip()}"
    return p.stdout


def parse_fdb(output: str):
    """
    Formato esperado (ejemplo):
     port  VLAN  MAC                Age
        2     0  f2:48:39:49:e9:31  100
        3     0  12:53:5f:fc:9a:fd   79

    Retorna lista de dicts: {port, vlan, mac, age}
    """
    lines = [ln.strip() for ln in output.splitlines() if ln.strip()]
    entries = []

    # Manejo simple de error
    if lines and lines[0].startswith("__ERROR__"):
        return entries, lines[0]

    # Buscar header
    # Si no está, igual intentamos parsear líneas tipo "2 0 aa:bb ... 12"
    start_idx = 0
    for i, ln in enumerate(lines):
        if ln.lower().startswith("port") and "mac" in ln.lower():
            start_idx = i + 1
            break

    for ln in lines[start_idx:]:
        parts = ln.split()
        if len(parts) < 4:
            continue
        port, vlan, mac, age = parts[0], parts[1], parts[2], parts[3]
        entries.append({"port": port, "vlan": vlan, "mac": mac, "age": age})

    return entries, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bridges", nargs="+", required=True, help="Bridges OVS a monitorear (ej: B1 B2 B3)")
    ap.add_argument("--interval", type=float, default=1.0, help="Intervalo de muestreo en segundos")
    ap.add_argument("--duration", type=float, default=60.0, help="Duración total del monitoreo (s)")
    ap.add_argument("--outdir", default="results", help="Directorio de salida")
    ap.add_argument("--snapshots", action="store_true", help="Guardar snapshots crudos por bridge/tiempo")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    csv_path = outdir / "fdb_monitor.csv"

    # CSV con cabecera estable (útil para análisis)
    fieldnames = [
        "timestamp",
        "bridge",
        "entries_count",
        "mac",
        "port",
        "vlan",
        "age",
        "note"
    ]

    t0 = time.time()
    t_end = t0 + args.duration

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        while time.time() < t_end:
            ts = now_iso()

            for br in args.bridges:
                raw = sh(f"ovs-appctl fdb/show {br}")
                entries, err = parse_fdb(raw)

                if args.snapshots:
                    snap = outdir / f"fdb_{br}_{ts.replace(':','-')}.txt"
                    snap.write_text(raw, encoding="utf-8")

                # Si hubo error, lo registramos como fila “vacía” con nota
                if err:
                    writer.writerow({
                        "timestamp": ts,
                        "bridge": br,
                        "entries_count": 0,
                        "mac": "",
                        "port": "",
                        "vlan": "",
                        "age": "",
                        "note": err
                    })
                    continue

                # Registramos una fila por cada MAC (más fácil para filtrar luego)
                if not entries:
                    writer.writerow({
                        "timestamp": ts,
                        "bridge": br,
                        "entries_count": 0,
                        "mac": "",
                        "port": "",
                        "vlan": "",
                        "age": "",
                        "note": "no_entries"
                    })
                else:
                    for e in entries:
                        writer.writerow({
                            "timestamp": ts,
                            "bridge": br,
                            "entries_count": len(entries),
                            "mac": e["mac"],
                            "port": e["port"],
                            "vlan": e["vlan"],
                            "age": e["age"],
                            "note": ""
                        })

            f.flush()
            time.sleep(args.interval)

    print(f"[OK] Monitor finalizado. CSV: {csv_path}")


if __name__ == "__main__":
    main()
