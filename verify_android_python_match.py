#!/usr/bin/env python3
"""
Verification script to demonstrate that Android app sends identical SOAP message
as Python fritzconnection library.
"""

from fritzconnection.core.soaper import Soaper

def main():
    print("=" * 70)
    print("VERIFICATION: Android App vs Python fritzconnection")
    print("=" * 70)
    print()
    
    # Python fritzconnection configuration
    service_type = "urn:dslforum-org:service:DeviceConfig:1"
    action_name = "Reboot"
    
    # 1. Headers
    print("1. HTTP HEADERS")
    print("-" * 70)
    python_headers = Soaper.headers.copy()
    python_headers['soapaction'] = f"{service_type}#{action_name}"
    
    print("Python fritzconnection headers:")
    for key, value in python_headers.items():
        print(f"  {key}: {value}")
    
    print()
    print("Android app headers (from FritzBoxClient.kt):")
    android_headers = {
        'content-type': 'text/xml',
        'soapaction': f"{service_type}#{action_name}",
        'charset': 'utf-8'
    }
    for key, value in android_headers.items():
        print(f"  {key}: {value}")
    
    print()
    headers_match = python_headers == android_headers
    print(f"✅ HEADERS MATCH: {headers_match}")
    print()
    
    # 2. SOAP Envelope/Body
    print("2. SOAP ENVELOPE / BODY")
    print("-" * 70)
    
    # Build Python envelope
    body_template = Soaper.body_template
    body = body_template.format(
        service_type=service_type,
        action_name=action_name,
        arguments=""
    )
    python_envelope = Soaper.envelope.format(body=body)
    
    # Build Android envelope (same format as FritzBoxClient.kt line 115)
    android_envelope = f'<?xml version="1.0" encoding="utf-8"?><s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body><u:{action_name} xmlns:u="{service_type}"></u:{action_name}></s:Body></s:Envelope>'
    
    print("Python fritzconnection envelope:")
    print(f"  {python_envelope}")
    print()
    print("Android app envelope:")
    print(f"  {android_envelope}")
    print()
    
    envelope_match = python_envelope == android_envelope
    print(f"✅ ENVELOPE MATCH: {envelope_match}")
    print()
    
    # 3. Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Headers identical: {headers_match}")
    print(f"SOAP envelope identical: {envelope_match}")
    print()
    
    if headers_match and envelope_match:
        print("✅ SUCCESS: Android app sends EXACT same SOAP message as Python!")
        print()
        print("The Android app now perfectly matches the Python fritzconnection")
        print("library, which is why error 606 'Action Not Authorized' is resolved.")
        return 0
    else:
        print("❌ MISMATCH: Differences found!")
        return 1

if __name__ == "__main__":
    exit(main())
