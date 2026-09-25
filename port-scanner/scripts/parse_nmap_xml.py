#!/usr/bin/env python3
"""Parse nmap XML output (-oX) into structured JSON for report generation."""

import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def parse_nmap_xml(xml_source):
    """Parse nmap XML output and return structured dict."""
    tree = ET.parse(xml_source)
    root = tree.getroot()

    result = {
        "scanner": root.get("scanner", "nmap"),
        "args": root.get("args", ""),
        "start_time": root.get("startstr", ""),
        "start_timestamp": root.get("start", ""),
        "version": root.get("version", ""),
        "hosts": [],
        "tasks": [],
        "summary": {},
    }

    for task in root.findall("taskbegin"):
        task_entry = {
            "task": task.get("task", ""),
            "time": task.get("time", ""),
            "extrainfo": task.get("extrainfo", ""),
        }
        end = root.find(f"taskend[@task='{task.get('task', '')}']")
        if end is not None:
            task_entry["end_time"] = end.get("time", "")
            task_entry["extrainfo_end"] = end.get("extrainfo", "")
        result["tasks"].append(task_entry)

    runstats = root.find("runstats")
    if runstats is not None:
        finished = runstats.find("finished")
        hosts_elem = runstats.find("hosts")
        if finished is not None:
            result["summary"]["end_time"] = finished.get("timestr", "")
            result["summary"]["elapsed"] = finished.get("elapsed", "")
            result["summary"]["exit_status"] = finished.get("exit", "")
        if hosts_elem is not None:
            result["summary"]["hosts_up"] = int(hosts_elem.get("up", 0))
            result["summary"]["hosts_down"] = int(hosts_elem.get("down", 0))
            result["summary"]["hosts_total"] = int(hosts_elem.get("total", 0))

    for host_elem in root.findall("host"):
        host = _parse_host(host_elem)
        result["hosts"].append(host)

    return result


def _parse_host(host_elem):
    """Parse a single host element."""
    host = {
        "status": "",
        "addresses": [],
        "hostnames": [],
        "ports": [],
        "os": [],
        "scripts": [],
        "traceroute": [],
        "uptime": None,
        "distance": None,
        "tcp_sequence": None,
        "ip_id_sequence": None,
        "tcp_ts_sequence": None,
    }

    status = host_elem.find("status")
    if status is not None:
        host["status"] = status.get("state", "")
        host["status_reason"] = status.get("reason", "")

    for addr in host_elem.findall("address"):
        host["addresses"].append({
            "addr": addr.get("addr", ""),
            "type": addr.get("addrtype", ""),
            "vendor": addr.get("vendor", ""),
        })

    hostnames = host_elem.find("hostnames")
    if hostnames is not None:
        for hn in hostnames.findall("hostname"):
            host["hostnames"].append({
                "name": hn.get("name", ""),
                "type": hn.get("type", ""),
            })

    ports = host_elem.find("ports")
    if ports is not None:
        for port in ports.findall("port"):
            host["ports"].append(_parse_port(port))
        for extraports in ports.findall("extraports"):
            host.setdefault("extraports", []).append({
                "state": extraports.get("state", ""),
                "count": int(extraports.get("count", 0)),
            })

    os_elem = host_elem.find("os")
    if os_elem is not None:
        for match in os_elem.findall("osmatch"):
            os_entry = {
                "name": match.get("name", ""),
                "accuracy": match.get("accuracy", ""),
                "classes": [],
            }
            for osclass in match.findall("osclass"):
                cls = {
                    "type": osclass.get("type", ""),
                    "vendor": osclass.get("vendor", ""),
                    "osfamily": osclass.get("osfamily", ""),
                    "osgen": osclass.get("osgen", ""),
                    "accuracy": osclass.get("accuracy", ""),
                    "cpe": [],
                }
                for cpe in osclass.findall("cpe"):
                    if cpe.text:
                        cls["cpe"].append(cpe.text)
                os_entry["classes"].append(cls)
            host["os"].append(os_entry)

    for script in host_elem.findall(".//hostscript/script"):
        host["scripts"].append(_parse_script(script))

    trace = host_elem.find("trace")
    if trace is not None:
        host["traceroute_proto"] = trace.get("proto", "")
        host["traceroute_port"] = trace.get("port", "")
        for hop in trace.findall("hop"):
            host["traceroute"].append({
                "ttl": hop.get("ttl", ""),
                "rtt": hop.get("rtt", ""),
                "ipaddr": hop.get("ipaddr", ""),
                "host": hop.get("host", ""),
            })

    uptime = host_elem.find("uptime")
    if uptime is not None:
        host["uptime"] = {
            "seconds": uptime.get("seconds", ""),
            "lastboot": uptime.get("lastboot", ""),
        }

    distance = host_elem.find("distance")
    if distance is not None:
        host["distance"] = int(distance.get("value", 0))

    tcpseq = host_elem.find("tcpsequence")
    if tcpseq is not None:
        host["tcp_sequence"] = {
            "index": tcpseq.get("index", ""),
            "difficulty": tcpseq.get("difficulty", ""),
            "values": tcpseq.get("values", ""),
        }

    ipidseq = host_elem.find("ipidsequence")
    if ipidseq is not None:
        host["ip_id_sequence"] = {
            "class": ipidseq.get("class", ""),
            "values": ipidseq.get("values", ""),
        }

    tcptsseq = host_elem.find("tcptssequence")
    if tcptsseq is not None:
        host["tcp_ts_sequence"] = {
            "class": tcptsseq.get("class", ""),
            "values": tcptsseq.get("values", ""),
        }

    return host


def _parse_port(port_elem):
    """Parse a single port element."""
    port = {
        "protocol": port_elem.get("protocol", ""),
        "portid": port_elem.get("portid", ""),
        "state": "",
        "reason": "",
        "reason_ttl": "",
        "service": "",
        "product": "",
        "version": "",
        "extrainfo": "",
        "tunnel": "",
        "cpe": [],
        "scripts": [],
    }

    state = port_elem.find("state")
    if state is not None:
        port["state"] = state.get("state", "")
        port["reason"] = state.get("reason", "")
        port["reason_ttl"] = state.get("reason_ttl", "")

    service = port_elem.find("service")
    if service is not None:
        port["service"] = service.get("name", "")
        port["product"] = service.get("product", "")
        port["version"] = service.get("version", "")
        port["extrainfo"] = service.get("extrainfo", "")
        port["tunnel"] = service.get("tunnel", "")
        port["method"] = service.get("method", "")
        port["conf"] = service.get("conf", "")
        for cpe in service.findall("cpe"):
            if cpe.text:
                port["cpe"].append(cpe.text)

    for script in port_elem.findall("script"):
        port["scripts"].append(_parse_script(script))

    return port


def _parse_script(script_elem):
    """Parse a single script element, including structured table output."""
    entry = {
        "id": script_elem.get("id", ""),
        "output": script_elem.get("output", ""),
    }
    tables = script_elem.findall("table")
    if tables:
        entry["tables"] = []
        for table in tables:
            entry["tables"].append(_parse_script_table(table))
    elems = script_elem.findall("elem")
    if elems:
        entry["elements"] = {}
        for elem in elems:
            key = elem.get("key", "")
            if key and elem.text:
                entry["elements"][key] = elem.text
    return entry


def _parse_script_table(table_elem):
    """Recursively parse NSE script table output."""
    result = {"key": table_elem.get("key", "")}
    elems = {}
    for elem in table_elem.findall("elem"):
        key = elem.get("key", "")
        if key and elem.text:
            elems[key] = elem.text
    if elems:
        result["elements"] = elems
    subtables = table_elem.findall("table")
    if subtables:
        result["tables"] = [_parse_script_table(t) for t in subtables]
    return result


def format_version(port):
    """Build a human-readable version string from port service info."""
    parts = []
    if port["product"]:
        parts.append(port["product"])
    if port["version"]:
        parts.append(port["version"])
    if port["extrainfo"]:
        parts.append(f"({port['extrainfo']})")
    return " ".join(parts) if parts else ""


def format_cpe(port):
    """Format CPE identifiers for display."""
    return ", ".join(port.get("cpe", [])) or ""


def print_summary(data):
    """Print a concise JSON summary to stdout."""
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <nmap-xml-file-or-stdin>", file=sys.stderr)
        print("  Pass '-' to read from stdin.", file=sys.stderr)
        sys.exit(1)

    source = sys.stdin if sys.argv[1] == "-" else sys.argv[1]

    try:
        data = parse_nmap_xml(source)
        print_summary(data)
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(f"File not found: {sys.argv[1]}", file=sys.stderr)
        sys.exit(1)
