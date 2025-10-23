#!/usr/bin/env python3
# fritzbox_restart.py
# Send a restart command to FRITZ!Box via TR-064 API
# Requires: TR-064 enabled, `pip install fritzconnection`

import argparse
import sys
from datetime import datetime

# Import-Pfad je nach fritzconnection-Version
try:
    from fritzconnection import FritzConnection
except ImportError:
    from fritzconnection.core.fritzconnection import FritzConnection  # fallback


def now() -> str:
    """Return current timestamp in standard format"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def reboot_fritzbox(host: str, user: str | None, password: str, timeout: int = 10) -> tuple[bool, str]:
    """
    Send reboot command to FRITZ!Box.
    
    Args:
        host: FRITZ!Box IP address or hostname
        user: Username (optional, can be None)
        password: Password for authentication
        timeout: Connection timeout in seconds
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        print(f"[{now()}] Verbinde zur FritzBox ({host})...")
        fc = FritzConnection(
            address=host,
            user=user,
            password=password,
            timeout=timeout,
            use_cache=False  # Don't cache for admin operations
        )
        
        print(f"[{now()}] Sende Neustart-Befehl...")
        fc.call_action("DeviceConfig:1", "Reboot")
        
        message = f"[{now()}] Neustart-Befehl erfolgreich gesendet [OK]"
        print(message)
        print(f"[{now()}] Die FRITZ!Box wird jetzt neu gestartet. Dies kann 1-2 Minuten dauern.")
        return True, message
        
    except Exception as e:
        error_msg = f"[{now()}] Fehler beim Senden des Neustartbefehls: {e}"
        print(error_msg, file=sys.stderr)
        return False, error_msg


def main():
    parser = argparse.ArgumentParser(
        description="Send reboot command to FRITZ!Box via TR-064 API"
    )
    parser.add_argument(
        "--host",
        default="192.168.178.1",
        help="FRITZ!Box IP/Host (default: 192.168.178.1)"
    )
    parser.add_argument(
        "--user",
        default=None,
        help="FRITZ!Box username (optional)"
    )
    parser.add_argument(
        "--password",
        required=True,
        help="FRITZ!Box password"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Connection timeout in seconds (default: 10)"
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip confirmation prompt"
    )
    
    args = parser.parse_args()
    
    # Confirmation prompt unless --yes flag is used
    if not args.yes:
        print(f"\n{'='*60}")
        print("WARNING: You are about to restart your FRITZ!Box!")
        print(f"Host: {args.host}")
        print("This will interrupt your internet connection for 1-2 minutes.")
        print(f"{'='*60}\n")
        
        try:
            response = input("Are you sure you want to continue? (yes/no): ").strip().lower()
            if response not in ["yes", "y"]:
                print("Restart cancelled.")
                sys.exit(0)
        except (KeyboardInterrupt, EOFError):
            print("\nRestart cancelled.")
            sys.exit(0)
    
    success, message = reboot_fritzbox(args.host, args.user, args.password, args.timeout)
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
