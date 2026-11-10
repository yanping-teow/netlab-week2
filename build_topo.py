
import sys
import yaml
import ipaddress
from mininet.net import Mininet
from mininet.node import OVSBridge
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel, info


def check(spec):
    problems = []

    # 0. Addresses must come from YOUR blocks (10.NN.0.0/16, fd00:NNNN::/32)
    last4 = str(spec.get("student_id_last4", ""))
    if not (len(last4) == 4 and last4.isdigit()):
        problems.append("PROBLEM: student_id_last4 must be 4 digits")
    else:
        v4_block = ipaddress.ip_network(f"10.{int(last4[-2:])}.0.0/16")
        v6_block = ipaddress.ip_network(f"fd00:{last4}::/32")
        for host in spec["hosts"]:
            for key, block in (("ip", v4_block), ("ipv6", v6_block)):
                if key not in host:
                    continue
                try:
                    addr = ipaddress.ip_interface(host[key]).ip
                except ValueError:
                    problems.append(f"PROBLEM: {host['name']} {key} {host[key]} isn't a valid address")
                    continue
                if addr not in block:
                    problems.append(f"PROBLEM: {host['name']} {key} {host[key]} isn't in your block {block}")

    # 1. Duplicate addresses, IPv4 and IPv6
    seen = {}  # address -> host name
    for host in spec["hosts"]:
        for key in ("ip", "ipv6"):
            if key not in host:
                continue
            try:
                addr = str(ipaddress.ip_interface(host[key]).ip)
            except ValueError:
                continue  # already reported above
            if addr in seen:
                problems.append(f"PROBLEM: {host['name']} and {seen[addr]} both use {addr}")
            else:
                seen[addr] = host["name"]

    # 2. Every link must name a switch or host that exists
    def names(items):
        return {i["name"] if isinstance(i, dict) else i for i in items}

    known = names(spec["switches"]) | names(spec["hosts"])
    for a, b in spec["links"]:
        for end in (a, b):
            if end not in known:
                problems.append(f"PROBLEM: link [{a}, {b}] names {end}, which doesn't exist")

    return problems


def run_network(filepath="topology.yaml"):
    with open(filepath, "r") as f:
        data = yaml.safe_load(f)

    print("Checking network data model...")
    problems = check(data)
    if problems:
        for p in problems:
            print(p)
        sys.exit(1)          # stop: a network that fails a check is never built
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