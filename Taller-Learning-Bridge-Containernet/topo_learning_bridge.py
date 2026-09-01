#!/usr/bin/env python3

from mininet.net import Containernet
from mininet.node import OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel


def main():
    setLogLevel("error")

    net = Containernet(controller=None)
    
    setLogLevel("info")

    print("\n[INFO] Creando switches (bridges)...")

    B1 = net.addSwitch("B1", cls=OVSSwitch, failMode="standalone")
    B2 = net.addSwitch("B2", cls=OVSSwitch, failMode="standalone")
    B3 = net.addSwitch("B3", cls=OVSSwitch, failMode="standalone")

    print("[INFO] Creando hosts...")

    X = net.addHost("X", ip="10.0.0.1/24", mac='AA:AA:AA:11:11:11')
    Y = net.addHost("Y", ip="10.0.0.2/24", mac='AA:AA:AA:22:22:22')
    Z = net.addHost("Z", ip="10.0.0.3/24", mac='AA:AA:AA:33:33:33')
    W = net.addHost("W", ip="10.0.0.4/24", mac='AA:AA:AA:44:44:44')

    print("[INFO] Creando enlaces...")

    # Host → bridge
    net.addLink(X, B1)
    net.addLink(Y, B2)
    net.addLink(Z, B3)
    net.addLink(W, B3)

    # Bridge → bridge
    net.addLink(B1, B2)
    net.addLink(B2, B3)

    print("[INFO] Iniciando red...")

    net.start()
    for host in ('X', 'Y', 'Z', 'W', 'B1', 'B2', 'B3'):
        net[host].cmd('sysctl -w net.ipv6.conf.all.disable_ipv6=1')

    print("\n====================================================")
    print("  Taller Learning Bridge listo.")
    print("  Probar desde CLI:")
    print("  X ping -c 1 10.0.0.2")
    print("  X ping -c 1 10.0.0.3")
    print("  sh bridge fdb show br-B1")
    print("====================================================\n")

    CLI(net)

    print("\n[INFO] Deteniendo red...")
    net.stop()


if __name__ == "__main__":
    main()