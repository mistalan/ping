#!/usr/bin/env python3
# fritzlog_pull.py
# FRITZ!Box-Statuslogging inkl. GetCommonLinkProperties + DSL-Fehlerzähler.
# Voraussetzung: TR-064 aktiviert, `pip install fritzconnection`

import csv
import time
import argparse
import datetime
import os

# Import-Pfad je nach fritzconnection-Version
try:
    from fritzconnection import FritzConnection
except ImportError:
    from fritzconnection.core.fritzconnection import FritzConnection  # fallback


def now() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_safe(fc: FritzConnection, service: str, action: str) -> dict:
    """TR-064 Action robust aufrufen. Liefert dict oder {'__error__': '...'}."""
    try:
        return fc.call_action(service, action)
    except Exception as e:
        return {"__error__": str(e)}


def first_ok(fc: FritzConnection, candidates: list[tuple[str, str]]) -> dict:
    """Teste mehrere (service, action)-Kandidaten und gib das erste OK-Ergebnis zurück."""
    for svc, act in candidates:
        res = get_safe(fc, svc, act)
        if "__error__" not in res:
            return res
    return {"__error__": "no candidate succeeded"}


def open_fc(address: str, user: str | None, password: str, timeout: int = 5) -> FritzConnection:
    return FritzConnection(address=address, user=user, password=password, timeout=timeout, use_cache=True)


def ensure_header(path: str, header: list[str]) -> None:
    try:
        with open(path, "x", encoding="utf-8", newline="") as f:
            f.write(",".join(header) + "\n")
    except FileExistsError:
        pass


def collect_once(fc: FritzConnection) -> dict:
    """
    Holt eine Status-Sonde von der Box. Unterstützt unterschiedliche Service-Bezeichner.
    """

    # --- WAN Status / External IP ---
    wan = first_ok(fc, [
        ("WANIPConnection1", "GetStatusInfo"),
        ("WANPPPConnection1", "GetStatusInfo"),
        ("WANIPConn1", "GetStatusInfo"),
        ("WANPPPConn1", "GetStatusInfo"),
    ])

    ext_ip = first_ok(fc, [
        ("WANIPConnection1", "GetExternalIPAddress"),
        ("WANIPConn1", "GetExternalIPAddress"),
    ])
    external_ip = "" if "__error__" in ext_ip else ext_ip.get("NewExternalIPAddress", "")

    # --- WAN Common: Traffic & Raten ---
    common = first_ok(fc, [
        ("WANCommonIFC1", "GetAddonInfos"),
        ("WANCommonInterfaceConfig1", "GetAddonInfos"),
    ])
    # enthält: NewTotalBytesSent, NewTotalBytesReceived, NewByteSendRate, NewByteReceiveRate

    # --- CommonLinkProperties (L1/Access/Physical Link) ---
    link_props = first_ok(fc, [
        ("WANCommonIFC1", "GetCommonLinkProperties"),
        ("WANCommonInterfaceConfig1", "GetCommonLinkProperties"),
    ])
    # enthält: NewWANAccessType, NewLayer1UpstreamMaxBitRate, NewLayer1DownstreamMaxBitRate,
    #          NewPhysicalLinkStatus

    # --- DSL Link Status ---
    dsl_link = first_ok(fc, [
        ("WANDSLLinkC1", "GetDSLLinkInfo"),
        ("WANDSLLinkConfig1", "GetDSLLinkInfo"),
        ("WANDSLLinkConfig", "GetDSLLinkInfo"),
    ])
    # enthält: NewLinkStatus

    # --- DSL Info (aktuelle Raten) ---
    dsl_info = first_ok(fc, [
        ("WANDSLInterfaceConfig1", "GetInfo"),
        ("WANDSLInterfaceConfig", "GetInfo"),
    ])
    # typ. enthält: NewUpstreamCurrRate, NewDownstreamCurrRate

    # --- DSL Fehlerzähler (Total) ---
    dsl_stats = first_ok(fc, [
        ("WANDSLInterfaceConfig1", "GetStatisticsTotal"),
        ("WANDSLInterfaceConfig", "GetStatisticsTotal"),
    ])
    # typ. enthält: NewFECErrors, NewCRCErrors, NewHECErrors, NewErroredSecs, NewSeverelyErroredSecs,
    #               NewLinkRetrain, NewInitErrors, NewInitTimeouts, sowie ATUC_*-Varianten

    data = {
        "timestamp": now(),

        # WAN core
        "wan_connection_status": "" if "__error__" in wan else wan.get("NewConnectionStatus", ""),
        "wan_uptime_s": "" if "__error__" in wan else wan.get("NewUptime", ""),
        "wan_external_ip": external_ip,
        "wan_last_error": "" if "__error__" in wan else wan.get("NewLastConnectionError", ""),

        # WAN common traffic
        "common_bytes_sent": "" if "__error__" in common else common.get("NewTotalBytesSent", ""),
        "common_bytes_recv": "" if "__error__" in common else common.get("NewTotalBytesReceived", ""),
        "common_rate_send_bps": "" if "__error__" in common else common.get("NewByteSendRate", ""),
        "common_rate_recv_bps": "" if "__error__" in common else common.get("NewByteReceiveRate", ""),

        # Common link properties
        "access_type": "" if "__error__" in link_props else link_props.get("NewWANAccessType", ""),
        "phys_link_status": "" if "__error__" in link_props else link_props.get("NewPhysicalLinkStatus", ""),
        "l1_up_max_bps": "" if "__error__" in link_props else link_props.get("NewLayer1UpstreamMaxBitRate", ""),
        "l1_down_max_bps": "" if "__error__" in link_props else link_props.get("NewLayer1DownstreamMaxBitRate", ""),

        # DSL link & current rates
        "dsl_link_status": "" if "__error__" in dsl_link else dsl_link.get("NewLinkStatus", ""),
        "dsl_curr_up_bps": "" if "__error__" in dsl_info else dsl_info.get("NewUpstreamCurrRate", ""),
        "dsl_curr_down_bps": "" if "__error__" in dsl_info else dsl_info.get("NewDownstreamCurrRate", ""),

        # DSL errors (Totals)
        "dsl_fec_errors": "" if "__error__" in dsl_stats else dsl_stats.get("NewFECErrors", ""),
        "dsl_crc_errors": "" if "__error__" in dsl_stats else dsl_stats.get("NewCRCErrors", ""),
        "dsl_hec_errors": "" if "__error__" in dsl_stats else dsl_stats.get("NewHECErrors", ""),
        "dsl_errored_secs": "" if "__error__" in dsl_stats else dsl_stats.get("NewErroredSecs", ""),
        "dsl_severely_errored_secs": "" if "__error__" in dsl_stats else dsl_stats.get("NewSeverelyErroredSecs", ""),
        "dsl_link_retrain": "" if "__error__" in dsl_stats else dsl_stats.get("NewLinkRetrain", ""),
        "dsl_init_errors": "" if "__error__" in dsl_stats else dsl_stats.get("NewInitErrors", ""),
        "dsl_init_timeouts": "" if "__error__" in dsl_stats else dsl_stats.get("NewInitTimeouts", ""),

        # Optional: Gegenstellen-Fehler (ATUC_*)
        "dsl_atuc_fec_errors": "" if "__error__" in dsl_stats else dsl_stats.get("NewATUC_FECErrors", ""),
        "dsl_atuc_crc_errors": "" if "__error__" in dsl_stats else dsl_stats.get("NewATUC_CRCErrors", ""),
        "dsl_atuc_hec_errors": "" if "__error__" in dsl_stats else dsl_stats.get("NewATUC_HECErrors", ""),
    }
    return data


def main():
    ap = argparse.ArgumentParser(description="FRITZ!Box WAN/DSL Extended Logger (TR-064)")
    ap.add_argument("--host", default="192.168.178.1", help="FRITZ!Box IP/Host (default: 192.168.178.1)")
    ap.add_argument("--user", default=None, help="FRITZ!Box Benutzername")
    ap.add_argument("--password", required=True, help="FRITZ!Box Passwort")
    ap.add_argument("--interval", type=int, default=30, help="Intervall in Sekunden (default: 30)")
    default_out = os.path.join(os.path.expanduser("~"), "Ping", "Log", "fritz_status_log.csv")
    ap.add_argument("--out", default=default_out, help=f"Pfad zur CSV (default: {default_out})")

    args = ap.parse_args()

    header = [
        "timestamp",
        "wan_connection_status", "wan_uptime_s", "wan_external_ip", "wan_last_error",
        "common_bytes_sent", "common_bytes_recv", "common_rate_send_bps", "common_rate_recv_bps",
        "access_type", "phys_link_status", "l1_up_max_bps", "l1_down_max_bps",
        "dsl_link_status", "dsl_curr_up_bps", "dsl_curr_down_bps",
        "dsl_fec_errors", "dsl_crc_errors", "dsl_hec_errors",
        "dsl_errored_secs", "dsl_severely_errored_secs",
        "dsl_link_retrain", "dsl_init_errors", "dsl_init_timeouts",
        "dsl_atuc_fec_errors", "dsl_atuc_crc_errors", "dsl_atuc_hec_errors",
    ]
    ensure_header(args.out, header)

    try:
        fc = open_fc(args.host, args.user, args.password)
    except Exception as e:
        raise SystemExit(f"Verbindung zur FRITZ!Box fehlgeschlagen: {e}")

    print(f"[{now()}] Logging → {args.out} (Intervall {args.interval}s). Abbruch mit STRG+C.")
    with open(args.out, "a", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        try:
            while True:
                row = collect_once(fc)
                w.writerow([row.get(h, "") for h in header])
                f.flush()
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print(f"\n[{now()}] Beendet.")
        except Exception as e:
            print(f"\n[{now()}] Fehler: {e}")


if __name__ == "__main__":
    main()
