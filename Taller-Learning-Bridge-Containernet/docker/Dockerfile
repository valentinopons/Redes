FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONPATH=/opt/containernet:/opt/containernet/mininet


RUN apt-get update && apt-get install -y \
    git python3 python3-pip iproute2 iputils-ping net-tools \
    tcpdump tshark bridge-utils \
    openvswitch-switch openvswitch-common \
    curl vim nano \
    docker.io \
    && rm -rf /var/lib/apt/lists/*
    
RUN pip3 install --no-cache-dir setuptools wheel
RUN pip3 install pyyaml docker networkx pandas matplotlib


WORKDIR /opt
RUN git clone https://github.com/containernet/containernet && \
    cd containernet && \
    pip3 install -r util/install/requirements.txt || true

WORKDIR /opt/containernet

RUN apt update && apt install -y \
    python-is-python3 \
    gcc make libc6-dev iproute2 util-linux

RUN make mnexec && cp mnexec /usr/local/bin/
RUN apt update && apt install -y openvswitch-switch

COPY start_ovs.sh /start_ovs.sh
RUN chmod +x /start_ovs.sh
ENTRYPOINT ["/start_ovs.sh"]

CMD ["/bin/bash"]
