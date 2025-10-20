#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyze NetWatch & FRITZ!Box logs, detect incidents, and summarize.
Author: your friendly latency exterminator :)
"""

import argparse
import csv
import sys
import os
import math
from datetime import datetime, timedelta
from collections import defaultdict

try:
    import pandas as pd
except ImportError:
    pd = None

# ---------- Config (Default thresholds) ----------
DEFAULT_LATENCY_SPIKE_MS = 20        # Ping > 20ms gilt als Spike (anpassbar)
DEFAULT_LOSS_SPIKE_PCT   = 1.0       # >1% Verlust in Messfenster -> Incident
MIN_BURST_SECONDS        = 60        # aggregiere Ereignisse zu Bursts ab 60s
TIME_FMT                 = "%Y-%m-%d %H:%M:%S"

# ---------- Helpers ----------
def parse_time(s):
    for fmt in (TIME_FMT, "%d.%m.%Y %H:%M:%S"):
        try:
            return datetime.strptime(s, fmt)
        except Exception:
            pass
    # letzter Versuch: ISO
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None

def to_float(x):
    if x is None or x == "":
        return math.nan
    try:
        return float(x)
    except Exception:
        return math.nan

def human_duration(delta: timedelta):
    secs = int(delta.total_seconds())
    if secs < 60:
        return f"{secs}s"
    mins, s = divmod(secs, 60)
    if mins < 60:
        return f"{mins}m {s}s"
    hrs, m = divmod(mins, 60)
    return f"{hrs}h {m}m"

# ---------- Detection ----------
def detect_netwatch_incidents(df, lat_thresh, loss_thresh):
    """
    Erwartete Spalten in netwatch_log.csv:
      timestamp,adapter,media_status,ipv4,ipv6_enabled,gateway,dns_ok,dns_ms,
      ping_<target>_avg_ms,ping_<target>_loss_pct, ...
    """
    incidents = []
    
    # Handle both pandas DataFrame and list of dicts
    is_dataframe = pd is not None and isinstance(df, pd.DataFrame)
    
    if is_dataframe:
        columns = df.columns
        rows = list(df.iterrows())
        get_row = lambda idx_row: idx_row[1]
    else:
        # List of dicts
        columns = df[0].keys() if df else []
        rows = list(enumerate(df))
        get_row = lambda idx_row: idx_row[1]

    # 1) DNS-Fehler
    if "dns_ok" in columns:
        for i, row_data in rows:
            row = get_row((i, row_data))
            if str(row.get("dns_ok", "1")) in ("0", "False", "false"):
                incidents.append({
                    "source": "PC",
                    "type": "DNS_FAIL",
                    "start": row["timestamp"], "end": row["timestamp"],
                    "details": f"dns_ms={row.get('dns_ms', '')}"
                })

    # 2) Adapter/Media-Statuswechsel
    for col in ("adapter", "media_status"):
        if col in columns and len(df) > 1:
            prev = None
            for i, row_data in rows:
                row = get_row((i, row_data))
                cur = str(row[col])
                if prev is not None and cur != prev:
                    incidents.append({
                        "source": "PC",
                        "type": f"{col.upper()}_CHANGE",
                        "start": row["timestamp"], "end": row["timestamp"],
                        "details": f"{col}: {prev} -> {cur}"
                    })
                prev = cur

    # 3) Ping/Verlust je Ziel
    # Finde dynamisch alle Ziele
    targets = []
    for c in columns:
        if c.startswith("ping_") and c.endswith("_avg_ms"):
            t = c[len("ping_"):-len("_avg_ms")]
            targets.append(t)

    for t in targets:
        avg_col = f"ping_{t}_avg_ms"
        loss_col = f"ping_{t}_loss_pct"
        if avg_col not in columns:
            continue

        # Latency spikes
        for i, row_data in rows:
            row = get_row((i, row_data))
            ts = row["timestamp"]
            avg = to_float(row.get(avg_col))
            if not math.isnan(avg) and avg > lat_thresh:
                incidents.append({
                    "source": "PC",
                    "type": "LATENCY_SPIKE",
                    "start": ts, "end": ts,
                    "details": f"{t}: {avg}ms"
                })

        # Loss spikes
        if loss_col in columns:
            for i, row_data in rows:
                row = get_row((i, row_data))
                ts = row["timestamp"]
                loss = to_float(row.get(loss_col))
                if not math.isnan(loss) and loss > loss_thresh:
                    incidents.append({
                        "source": "PC",
                        "type": "LOSS_SPIKE",
                        "start": ts, "end": ts,
                        "details": f"{t}: {loss}%"
                    })

    return incidents

def detect_fritz_incidents(df):
    """
    Erwartete Spalten in fritz_status_log.csv:
      timestamp, wan_connection_status, wan_uptime_s, wan_external_ip,
      wan_last_error, common_bytes_sent, common_bytes_recv, dsl_link_status
    """
    incidents = []
    
    # Handle both pandas DataFrame and list of dicts
    is_dataframe = pd is not None and isinstance(df, pd.DataFrame)
    
    if is_dataframe:
        rows = list(df.iterrows())
        get_row = lambda idx_row: idx_row[1]
    else:
        # List of dicts
        rows = list(enumerate(df))
        get_row = lambda idx_row: idx_row[1]
    
    # Uptime-Reset / Statuswechsel / IP-Wechsel
    prev = None
    for i, row_data in rows:
        row = get_row((i, row_data))
        ts = row["timestamp"]
        if prev is not None:
            # Uptime rückwärts -> Reconnect
            u_now  = to_float(row.get("wan_uptime_s"))
            u_prev = to_float(prev.get("wan_uptime_s"))
            if not math.isnan(u_prev) and not math.isnan(u_now) and u_now < u_prev:
                incidents.append({
                    "source": "FRITZ",
                    "type": "WAN_RECONNECT",
                    "start": ts, "end": ts,
                    "details": f"uptime {int(u_prev)}s -> {int(u_now)}s"
                })

            # Statuswechsel
            s_now  = str(row.get("wan_connection_status", ""))
            s_prev = str(prev.get("wan_connection_status", ""))
            if s_now != s_prev:
                incidents.append({
                    "source": "FRITZ",
                    "type": "WAN_STATUS_CHANGE",
                    "start": ts, "end": ts,
                    "details": f"{s_prev} -> {s_now}"
                })

            # Externe IP gewechselt
            ip_now  = str(row.get("wan_external_ip", ""))
            ip_prev = str(prev.get("wan_external_ip", ""))
            if ip_now and ip_prev and ip_now != ip_prev:
                incidents.append({
                    "source": "FRITZ",
                    "type": "EXTERNAL_IP_CHANGE",
                    "start": ts, "end": ts,
                    "details": f"{ip_prev} -> {ip_now}"
                })

        # DSL Link down?
        ls = str(row.get("dsl_link_status", ""))
        if ls and ls.lower() not in ("", "up", "connected"):
            incidents.append({
                "source": "FRITZ",
                "type": "DSL_LINK_ABNORMAL",
                "start": ts, "end": ts,
                "details": f"dsl_link_status={ls}"
            })

        prev = row

    return incidents

def extract_details_key(details):
    """
    Extracts a grouping key from the details string, handling multiple separators.
    """
    if not details:
        return ""
    for sep in [":", " -> "]:
        if sep in details:
            return details.split(sep)[0].strip()
    return details.strip()  

def aggregate_bursts(incidents, min_span_seconds=MIN_BURST_SECONDS):
    """
    Gleiche Typ+Quelle zusammen, wenn Einträge zeitlich eng beieinander liegen.
    """
    by_key = defaultdict(list)
    for inc in incidents:
        key = (inc["source"], inc["type"], extract_details_key(inc.get("details","")))  # gruppiere pro Ziel grob
        by_key[key].append(inc)

    aggregated = []
    for key, lst in by_key.items():
        lst = sorted(lst, key=lambda x: x["start"])
        cur = None
        for ev in lst:
            if cur is None:
                cur = dict(ev)
                continue
            gap = ev["start"] - cur["end"]
            if gap.total_seconds() <= min_span_seconds:
                cur["end"] = ev["end"]
                # details zusammenführen (kurz halten)
                if ev["details"] and ev["details"] not in cur["details"]:
                    if len(cur["details"]) < 120:
                        cur["details"] += f" | {ev['details']}"
            else:
                aggregated.append(cur)
                cur = dict(ev)
        if cur:
            aggregated.append(cur)

    return sorted(aggregated, key=lambda x: x["start"])

# ---------- Main ----------
def load_csv(path, time_col="timestamp"):
    if pd is None:
        # Fallback ohne pandas: sehr simple CSV-Reader (langsamer, aber ok)
        rows = []
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                r = dict(r)
                if time_col in r:
                    r[time_col] = parse_time(r[time_col])
                rows.append(r)
            fieldnames = reader.fieldnames
        return rows, fieldnames
    else:
        df = pd.read_csv(path, encoding="utf-8")
        if time_col in df.columns:
            df[time_col] = df[time_col].apply(parse_time)
        # drop rows ohne Zeit
        df = df.dropna(subset=[time_col]).copy()
        return df, list(df.columns)

def main():
    ap = argparse.ArgumentParser(description="Analyze NetWatch + FRITZ!Box CSV logs and detect incidents.")
    ap.add_argument("--netwatch", required=True, help="Pfad zu netwatch_log.csv")
    ap.add_argument("--fritz", required=True, help="Pfad zu fritz_status_log.csv")
    ap.add_argument("--out", default="incidents.csv", help="Ausgabe-CSV für Incidents")
    ap.add_argument("--latency", type=float, default=DEFAULT_LATENCY_SPIKE_MS, help="Latency-Spike-Schwelle in ms (default 20)")
    ap.add_argument("--loss", type=float, default=DEFAULT_LOSS_SPIKE_PCT, help="Loss-Spike-Schwelle in %% (default 1.0)")
    ap.add_argument("--plots", action="store_true", help="Einfache Plots erstellen (benötigt matplotlib+pandas)")
    args = ap.parse_args()

    # Laden
    nw, _ = load_csv(args.netwatch)
    fr, _ = load_csv(args.fritz)

    # in DataFrames konvertieren (wenn pandas vorhanden)
    if pd is not None:
        df_nw = nw if isinstance(nw, pd.DataFrame) else pd.DataFrame(nw)
        df_fr = fr if isinstance(fr, pd.DataFrame) else pd.DataFrame(fr)
    else:
        print("Hinweis: pandas nicht installiert - Fallback-Modus (langsamer)")
        df_nw = nw
        df_fr = fr

    # Sortieren
    if pd is not None:
        df_nw = df_nw.sort_values("timestamp").reset_index(drop=True)
        df_fr = df_fr.sort_values("timestamp").reset_index(drop=True)
    else:
        df_nw = sorted(df_nw, key=lambda r: r.get("timestamp"))
        df_fr = sorted(df_fr, key=lambda r: r.get("timestamp"))

    # Detektion
    inc_nw = detect_netwatch_incidents(df_nw, args.latency, args.loss)
    inc_fr = detect_fritz_incidents(df_fr)
    incidents = inc_nw + inc_fr
    # Bursts aggregieren
    incidents = aggregate_bursts(incidents)

    # Ausgabe CSV
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["source","type","start","end","duration","details"])
        for ev in incidents:
            dur = human_duration(ev["end"] - ev["start"])
            w.writerow([
                ev["source"], ev["type"],
                ev["start"].strftime(TIME_FMT),
                ev["end"].strftime(TIME_FMT),
                dur, ev.get("details","")
            ])

    # Konsole: kurze Zusammenfassung
    print(f"\nIncidents geschrieben nach: {os.path.abspath(args.out)}")
    if not incidents:
        print("✅ Keine Auffälligkeiten gefunden.")
    else:
        print("⚠️ Erkannte Ereignisse:")
        for ev in incidents:
            print(f"- [{ev['source']}/{ev['type']}] {ev['start'].strftime(TIME_FMT)} – {ev['end'].strftime(TIME_FMT)} ({human_duration(ev['end']-ev['start'])}) {(' | ' + ev['details']) if ev.get('details') else ''}")

    # Optional Plots
    if args.plots and pd is not None:
        try:
            import matplotlib.pyplot as plt
            # einfache Ping-Plot je Ziel
            targets = [c[len("ping_"):-len("_avg_ms")] for c in df_nw.columns if c.startswith("ping_") and c.endswith("_avg_ms")]
            for t in targets:
                col = f"ping_{t}_avg_ms"
                if col in df_nw.columns:
                    plt.figure()
                    plt.plot(df_nw["timestamp"], df_nw[col])
                    plt.title(f"Latency: {t}")
                    plt.xlabel("Zeit"); plt.ylabel("ms")
                    plt.tight_layout()
                    plt.savefig(f"latency_{t}.png")
                    plt.close()
            print("📈 Plots gespeichert (latency_*.png).")
        except Exception as e:
            print(f"(Plots übersprungen: {e})")

if __name__ == "__main__":
    main()
