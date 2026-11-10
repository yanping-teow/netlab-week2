import sys
import yaml
import ipaddress
from mininet.net import Mininet
from mininet.node import OVSBridge
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel, info

def check(data):
    last4 = str(data.get("student_id_last4", ""))
    if last4 != "2318":
        print(f"PROBLEM: student_id_last4 '{last4}' does not match expected '2318'")
        sys.exit(1)

    ipv4_block = ipaddress.ip_network("10.18.0.0/16")
    ipv6_block = ipaddress.ip_network("fd00:2318::/32")

    switches = {s["name"] for s in data.get("switches", [])}
    hosts = {h["name"] for h in data.get("hosts", [])}
    all_nodes = switches.union(hosts)

    seen_ipv4 = {}
    seen_ipv6 = {}

    for h in data.get("hosts", []):
        name = h["name"]
        ip_str = h.get("ip")
        if ip_str:
            ip_addr = ipaddress.ip_interface(ip_str).ip
            if ip_addr not in ipv4_block:
                print(f"PROBLEM: Host {name} IPv4 {ip_addr} is outside assigned block {ipv4_block}")
                sys.exit(1)
            if ip_addr in seen_ipv4:
                print(f"PROBLEM: {name} and {seen_ipv4[ip_addr]} both use {ip_addr}")
                sys.exit(1)
            seen_ipv4[ip_addr] = name

        ip6_str = h.get("ipv6")
        if ip6_str:
            ip6_addr = ipaddress.ip_interface(ip6_str).ip
            if ip6_addr not in ipv6_block:
                print(f"PROBLEM: Host {name} IPv6 {ip6_addr} is outside assigned block {ipv6_block}")
                sys.exit(1)
            if ip6_addr in seen_ipv6:
                print(f"PROBLEM: {name} and {seen_ipv6[ip6_addr]} both use {ip6_addr}")
                sys.exit(1)
            seen_ipv6[ip6_addr] = name

    for link in data.get("links", []):
        n1, n2 = link[0], link[1]
        if n1 not in all_nodes:
            print(f"PROBLEM: Link references unknown node '{n1}'")
            sys.exit(1)
        if n2 not in all_nodes:
            print(f"PROBLEM: Link references unknown node '{n2}'")
            sys.exit(1)

def run_network(filepath="topology.yaml"):
    with open(filepath, "r") as f:
        data = yaml.safe_load(f)

    print("Checking network data model...")
    check(data)
    print("✅ Validation passed successfully.")

    net = Mininet(switch=OVSBridge, link=TCLink)

    info("*** Adding switches\n")
    switches = {}
    for s in data.get("switches", []):
        switches[s["name"]] = net.addSwitch(s["name"], dpid=s.get("dpid"))

    info("*** Adding hosts with custom IP, IPv6, and MAC\n")
    hosts = {}
    for h in data.get("hosts", []):
        host = net.addHost(h["name"], ip=h["ip"], mac=h.get("mac"))
        hosts[h["name"]] = host

    all_nodes = {**switches, **hosts}

    info("*** Adding links\n")
    for l in data.get("links", []):
        n1, n2 = l[0], l[1]
        net.addLink(all_nodes[n1], all_nodes[n2])

    info("*** Starting network\n")
    net.start()

    info("*** Configuring IPv6 addresses on hosts\n")
    for h in data.get("hosts", []):
        if "ipv6" in h and h["ipv6"]:
            host_obj = hosts[h["name"]]
            host_obj.cmd(f"ip -6 addr add {h['ipv6']} dev {h['name']}-eth0")
            host_obj.cmd(f"ip -6 route add default dev {h['name']}-eth0")

    info("*** Testing full connectivity (pingall)\n")
    net.pingAll()
    CLI(net)
    net.stop()

if __name__ == "__main__":
    setLogLevel("info")
    run_network(sys.argv[1] if len(sys.argv) > 1 else "topology.yaml")
