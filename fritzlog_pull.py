#!/usr/bin/env python3
# fritzlog_pull.py
# Loggt in festen Intervallen WAN-Status, Uptime, externe IP, Fehlercode,
# Traffic-Zähler und (falls vorhanden) DSL-Link-Status der FRITZ!Box.

import csv
import time
import argparse
import datetime
import os

# Import-Pfad je nach fritzconnection-Version:
try:
    from fritzconnection import FritzConnection
except ImportError:
    from fritzconnection.core.fritzconnection import FritzConnection  # fallback


def now() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_safe(fc: FritzConnection, service: str, action: str) -> dict:
    """Ruft eine TR-064 Action sicher auf und liefert bei Fehler ein Dict mit '__error__'."""
    try:
        return fc.call_action(service, action)
    except Exception as e:
        return {"__error__": str(e)}


def open_fc(address: str, user: str | None, password: str, timeout: int = 5) -> FritzConnection:
    # use_cache=True reduziert Roundtrips
    return FritzConnection(address=address, user=user, password=password, timeout=timeout, use_cache=True)


def ensure_header(path: str, header: list[str]) -> None:
    try:
        with open(path, "x", encoding="utf-8", newline="") as f:
            f.write(",".join(header) + "\n")
    except FileExistsError:
        pass


def collect_once(fc: FritzConnection) -> dict:
    """
    Holt eine Status-Sonde von der Box.
    Behandelt unterschiedliche Service-Namen (WANIPConnection1 / WANPPPConnection1).
    """
    # WAN-Status (erst IP, dann PPP probieren)
    wan = get_safe(fc, "WANIPConnection1", "GetStatusInfo")
    if "__error__" in wan:
        wan = get_safe(fc, "WANPPPConnection1", "GetStatusInfo")

    # Externe IP (falls IP-Service nicht verfügbar, leer lassen)
    ext = get_safe(fc, "WANIPConnection1", "GetExternalIPAddress")
    external_ip = "" if "NewExternalIPAddress" not in ext else ext["NewExternalIPAddress"]

    # Traffic-Zähler (WAN Common)
    common = get_safe(fc, "WANCommonIFC1", "GetAddonInfos")

    # DSL-Link (bei Kabel/FTTH evtl. nicht vorhanden)
    dsl = get_safe(fc, "WANDSLLinkC1", "GetDSLLinkInfo")

    data = {
        "timestamp": now(),
        "wan_connection_status": wan.get("NewConnectionStatus", ""),
        "wan_uptime_s": wan.get("NewUptime", ""),
        "wan_external_ip": external_ip,
        "wan_last_error": wan.get("NewLastConnectionError", ""),
        "common_bytes_sent": common.get("NewTotalBytesSent", ""),
        "common_bytes_recv": common.get("NewTotalBytesReceived", ""),
        "dsl_link_status": dsl.get("NewLinkStatus", "") if "__error__" not in dsl else "",
    }
    return data


def main():
    ap = argparse.ArgumentParser(description="FRITZ!Box WAN/Status Puller (TR-064)")
    ap.add_argument("--host", default="192.168.178.1", help="FRITZ!Box IP/Host (default: 192.168.178.1)")
    ap.add_argument("--user", default=None, help="FRITZ!Box Benutzername (oft None/leer bei älteren Setups)")
    ap.add_argument("--password", required=True, help="FRITZ!Box Passwort")
    ap.add_argument("--interval", type=int, default=30, help="Intervall in Sekunden (default: 30)")
    default_out = os.path.join(os.path.expanduser("~"), "Ping", "Log", "fritz_status_log.csv")
    ap.add_argument("--out", default=default_out, help=f"Pfad zur CSV (default: {default_out})")
    args = ap.parse_args()

    header = [
        "timestamp",
        "wan_connection_status",
        "wan_uptime_s",
        "wan_external_ip",
        "wan_last_error",
        "common_bytes_sent",
        "common_bytes_recv",
        "dsl_link_status",
    ]
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    ensure_header(args.out, header)

    try:
        fc = open_fc(args.host, args.user, args.password)
    except Exception as e:
        raise SystemExit(f"Verbindung zur FRITZ!Box fehlgeschlagen: {e}")

    print(f"[{now()}] Starte Logging → {args.out} (Intervall {args.interval}s). Abbruch mit STRG+C.")
    with open(args.out, "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        try:
            while True:
                row = collect_once(fc)
                writer.writerow([row[h] for h in header])
                f.flush()
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print(f"\n[{now()}] Beendet.")
        except Exception as e:
            print(f"\n[{now()}] Fehler: {e}")


if __name__ == "__main__":
    main()
