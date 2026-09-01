#!/bin/bash
mkdir -p /var/run/openvswitch

if [ ! -f /etc/openvswitch/conf.db ]; then
  ovsdb-tool create /etc/openvswitch/conf.db \
    /usr/share/openvswitch/vswitch.ovsschema
fi

ovsdb-server \
  --remote=punix:/var/run/openvswitch/db.sock \
  --remote=db:Open_vSwitch,Open_vSwitch,manager_options \
  --pidfile \
  --detach

ovs-vswitchd --pidfile --detach

exec "$@"
