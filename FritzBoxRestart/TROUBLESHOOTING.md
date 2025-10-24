# FRITZ!Box Restart - Comprehensive Troubleshooting Guide

## For the Third Occurrence of HTTP 500 Error

This guide provides a comprehensive strategy to track down, log, debug, and analyze the HTTP 500 error that persists after two previous fix attempts.

---

## Overview

Despite fixes in v1.0.1 (SOAP envelope format) and v1.0.2 (HTTP headers), some users continue to experience HTTP 500 errors. This suggests the issue may be:

1. **Environment-specific** (certain FRITZ!Box models/firmware versions)
2. **Network-specific** (certain router configurations)
3. **Implementation gap** (something we're still missing compared to working Python client)

---

## New Diagnostic Features (v1.1.0)

The app now includes comprehensive debugging tools to help identify the root cause:

### 1. Enhanced Logging
- **Detailed HTTP Request/Response Logging**: Every header, every byte
- **SOAP Envelope Validation**: Checks format matches Python client
- **Network Diagnostics**: DNS, ping, port checks before sending request
- **System Information**: Android version, device details
- **Stack Traces**: Full error details for unexpected failures

### 2. Diagnostic Report Generator
- **Network Health Check**: Tests connectivity, DNS, port accessibility
- **System Information**: App version, Android version, device info
- **Comparison with Python Client**: Shows what working implementation sends
- **Troubleshooting Checklist**: Step-by-step diagnostic guide
- **Full Application Logs**: All debug output in one report

### 3. How to Use
1. Open the app
2. Tap the **ℹ️ (info)** icon in the top right
3. Tap **"Generate Diagnostic Report"**
4. Enter your FRITZ!Box IP address
5. Wait for the report to generate (runs network tests)
6. **View** the report or **Share** it for support

---

## Information Needed from Users

When reporting the HTTP 500 error, please provide:

### 1. FRITZ!Box Information
- **Model**: (e.g., FRITZ!Box 7590, 7530, 7490)
- **Firmware Version**: Found in FRITZ!Box web UI → System → Update
- **TR-064 Enabled**: System → FRITZ!Box Users → Login to Home Network
- **Region/Country**: Some features vary by region

### 2. Network Setup
- **Connection Type**: WiFi, Ethernet, Mobile Data
- **Same Network**: Is Android device on same network as FRITZ!Box?
- **Network Configuration**: Any VPNs, firewalls, proxies?
- **Router Cascading**: Is FRITZ!Box behind another router?

### 3. Python Client Test
**This is critical for diagnosis!**

Run the Python script to confirm TR-064 is working:

```bash
# Install dependencies
pip install fritzconnection

# Run the Python script
python3 fritzbox_restart.py --host 192.168.178.1 --password YOUR_PASSWORD --yes
```

**Result:**
- ✅ **Works**: Issue is Android-specific (implementation difference)
- ❌ **Fails**: Issue is with FRITZ!Box TR-064 configuration (not app bug)

### 4. Diagnostic Report
- Generate and share the full diagnostic report from the app
- This includes system info, network tests, and all logs

### 5. Detailed Logs
Look for these sections in the logs:

```
=== HTTP REQUEST ===
URL: http://192.168.178.1:49000/upnp/control/deviceconfig
Method: POST
Headers:
  soapaction: urn:dslforum-org:service:DeviceConfig:1#Reboot
  Content-Type: text/xml
  charset: utf-8
Body:
<?xml version="1.0" encoding="utf-8"?><s:Envelope...
```

```
=== HTTP RESPONSE ===
Code: 500
Message: Internal Server Error
Duration: XXXms
Headers:
  ...
Body:
<SOAP-ENV:Fault>...</SOAP-ENV:Fault>
```

---

## Step-by-Step Debugging Process

### Step 1: Verify Basic Connectivity
1. Open app
2. Go to Logs (ℹ️ icon)
3. Generate Diagnostic Report
4. Check network diagnostics section:
   - ✅ Network connected
   - ✅ DNS resolves host
   - ✅ Host reachable (ping)
   - ✅ TR-064 port (49000) open

**If any fail**: Fix network/FRITZ!Box configuration first

### Step 2: Test Python Client
```bash
python3 fritzbox_restart.py --host 192.168.178.1 --password YOUR_PASSWORD --yes
```

- **Success**: TR-064 is working → Issue is in Android app implementation
- **Failure**: TR-064 is broken → Check FRITZ!Box settings

### Step 3: Compare HTTP Requests
If Python works but Android fails:

1. Enable verbose logging in Python:
   ```python
   # Edit fritzconnection library to log requests
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. Run Python script and capture HTTP traffic:
   ```bash
   python3 fritzbox_restart.py --host 192.168.178.1 --password YOUR_PASSWORD --yes > python_output.txt 2>&1
   ```

3. Generate Android diagnostic report

4. **Compare**:
   - HTTP headers (exact format)
   - SOAP envelope (byte-for-byte)
   - Authentication header format
   - Any encoding differences

### Step 4: Capture FRITZ!Box Logs
1. Open FRITZ!Box web UI
2. Go to **System → Events**
3. Look for TR-064 related errors around the time of failed attempt
4. Share relevant log entries

### Step 5: Test with Packet Capture (Advanced)
Use Wireshark or tcpdump to capture the actual HTTP traffic:

**On Computer:**
```bash
# Capture traffic on port 49000
tcpdump -i any -w fritzbox_traffic.pcap port 49000
```

Run both Python (working) and Android (failing) attempts while capturing.

**Compare**:
- Exact HTTP request bytes
- Header order and format
- Body content
- Any differences in TCP handshake

---

## Common Causes and Solutions

### Cause 1: SOAP Envelope Whitespace
**Symptom**: HTTP 500, Python works, headers look correct

**Check**: SOAP envelope has NO line breaks, NO extra whitespace

**Solution**: Already fixed in v1.0.1

### Cause 2: HTTP Header Format
**Symptom**: HTTP 500, SOAP looks correct

**Check**: Headers are sent as separate `charset: utf-8` not combined `Content-Type: text/xml; charset=utf-8`

**Solution**: Already fixed in v1.0.2

### Cause 3: Header Case Sensitivity
**Symptom**: HTTP 500, everything looks right

**Check**: 
- `soapaction` (lowercase) not `SOAPAction`
- `content-type` (lowercase) not `Content-Type`

**Solution**: OkHttp normalizes headers, but check logs to confirm

### Cause 4: FRITZ!Box Firmware Version
**Symptom**: Works on some FRITZ!Box models, not others

**Check**: FRITZ!Box firmware version

**Solution**: May need firmware-specific SOAP format

### Cause 5: Authentication Header Format
**Symptom**: HTTP 500 after authentication challenge

**Check**: Digest auth response format in logs

**Solution**: Compare with Python's digest auth

### Cause 6: Character Encoding
**Symptom**: HTTP 500, SOAP looks identical

**Check**: Actual byte encoding (UTF-8 BOM, etc.)

**Solution**: May need to specify exact encoding

---

## What We've Already Tried

### v1.0.1 - SOAP Format Fix
- ❌ Changed header from `SOAPAction` to `soapaction`
- ❌ Removed whitespace from SOAP envelope
- ❌ Changed to single-line format
- ❌ Used closing tags instead of self-closing tags

**Result**: Still failed for some users

### v1.0.2 - Header Format Fix
- ❌ Split `Content-Type: text/xml; charset=utf-8` into two headers
- ❌ Sent as `Content-Type: text/xml` + `charset: utf-8`

**Result**: Still failed for some users

---

## Next Steps for Developers

### If Pattern Emerges from User Reports

1. **Specific FRITZ!Box Models**:
   - Add model detection
   - Use model-specific SOAP format

2. **Specific Firmware Versions**:
   - Add firmware version check
   - Adapt request format based on version

3. **Specific Network Configurations**:
   - Add network configuration detection
   - Provide warnings/workarounds

### If Python Always Works

The issue is definitely in our Android implementation. Need to:

1. **Exact HTTP Packet Match**:
   - Use Wireshark to compare byte-for-byte
   - Ensure Android sends IDENTICAL request to Python

2. **Library Difference**:
   - Python uses `requests` + `fritzconnection`
   - Android uses `OkHttp`
   - May need to work around OkHttp's automatic header handling

3. **Consider Native HTTP**:
   - Use `HttpURLConnection` instead of OkHttp
   - Gives more control over exact header format

---

## Questions for Users Experiencing This

Please help us debug by answering:

1. **Does the Python script work for you?**
   - Yes → Android implementation issue
   - No → FRITZ!Box configuration issue

2. **What FRITZ!Box model and firmware version?**
   - Helps identify if issue is model-specific

3. **Can you capture and share HTTP traffic?**
   - Shows exact difference between working/failing requests

4. **What does FRITZ!Box event log show?**
   - May reveal the exact parsing error

5. **Does it work over Ethernet vs WiFi?**
   - Helps rule out network-specific issues

6. **Any special characters in password?**
   - Could be encoding issue in digest auth

---

## How to Share Diagnostic Information

### Option 1: In-App Diagnostic Report
1. Open app → Tap ℹ️
2. Tap "Generate Diagnostic Report"
3. Tap "Share"
4. Send via email/GitHub issue

### Option 2: Manual Log Export
1. Open app → Tap ℹ️
2. Tap "Share" to export raw logs
3. Attach to GitHub issue or email

### Option 3: Python Test Output
```bash
python3 fritzbox_restart.py --host YOUR_HOST --password YOUR_PASSWORD --yes > test_output.txt 2>&1
```
Share `test_output.txt` (remove password first!)

---

## Summary: What We Need

To finally fix this issue, we need from users experiencing HTTP 500:

✅ **FRITZ!Box model and firmware version**
✅ **Python client test result** (works/fails)
✅ **Full diagnostic report from app**
✅ **FRITZ!Box event logs** (during failed attempt)
✅ **Packet capture** (if possible)

With this information, we can identify the exact difference and implement a permanent fix.

---

## Contact

- **GitHub Issues**: https://github.com/mistalan/ping/issues
- **Include**: "FRITZ!Box Restart HTTP 500" in title
- **Attach**: Diagnostic report (passwords redacted)
