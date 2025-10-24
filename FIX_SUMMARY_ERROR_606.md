# FRITZ!Box Restart Error 606 Fix - Summary

## Issue
Users reported that the FRITZ!Box restart functionality was still not working, experiencing HTTP 500 errors with UPnP error code 606 "Action Not Authorized". This persisted even after v1.1.1 which added the Content-Type header.

## Investigation
Downloaded and analyzed the log file from the GitHub issue (`fritzbox_restart.log.txt`). The log showed:

```
Headers:
  Content-Type: text/xml; charset=utf-8
  soapaction: urn:dslforum-org:service:DeviceConfig:1#Reboot
  charset: utf-8

Response: HTTP 500 - Error 606: Action Not Authorized
```

## Root Cause
Compared the Android app's headers with the working Python fritzconnection library:

**Python (working):**
```python
headers = {"soapaction": "", "content-type": "text/xml", "charset": "utf-8"}
```

**Android v1.1.1 (failing):**
```
Content-Type: text/xml; charset=utf-8  # Combined and capitalized
soapaction: ...
charset: utf-8
```

The issue: OkHttp was automatically combining the headers when using `.toRequestBody("text/xml".toMediaType())`, even though we tried to add separate headers.

## Solution
Modified `FritzBoxClient.kt` to use `null` MediaType and manually add lowercase headers:

```kotlin
// Before (v1.1.1)
.post(soapBody.toRequestBody("text/xml".toMediaType()))
.addHeader("Content-Type", "text/xml; charset=utf-8")

// After (v1.1.2)
.post(soapBody.toByteArray().toRequestBody(null))
.addHeader("content-type", "text/xml")
```

This produces headers that exactly match Python:
```
content-type: text/xml
charset: utf-8
soapaction: urn:dslforum-org:service:DeviceConfig:1#Reboot
```

## Changes Made

### Code Changes
1. **FritzBoxClient.kt**: Changed request body creation and header format
2. **FritzBoxClientTest.kt**: Updated tests to verify correct header format

### Documentation
3. **CHANGELOG.md**: Added v1.1.2 release notes
4. **FIX_ERROR_606_HEADERS.md**: Comprehensive documentation of issue and fix

## Testing Results

### Android Tests
✅ All 13 unit tests passing
- Header format validation
- SOAP envelope format
- Success/error scenarios

### Python Tests
✅ All 21 unit tests passing
- No regression in Python script

## Expected Outcome
Users who experienced error 606 should now be able to successfully restart their FRITZ!Box from the Android app. The headers now match the Python fritzconnection library exactly, which is the reference implementation for TR-064 API communication.

## Files Changed
- `FritzBoxRestart/app/src/main/kotlin/com/fritzbox/restart/FritzBoxClient.kt`
- `FritzBoxRestart/app/src/test/kotlin/com/fritzbox/restart/FritzBoxClientTest.kt`
- `FritzBoxRestart/CHANGELOG.md`
- `FritzBoxRestart/FIX_ERROR_606_HEADERS.md` (new)

## Security
✅ No security issues detected by CodeQL
✅ No new dependencies added
✅ No credentials or sensitive data exposed

## Version
This fix will be released as **v1.1.2**.
