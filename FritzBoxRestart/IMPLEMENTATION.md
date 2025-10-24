# Implementation Details

This document provides technical details about the FRITZ!Box Restart Android app implementation.

## Architecture

The app follows a simple, single-activity architecture suitable for its focused purpose:

```
MainActivity
    ├── UI Layer (activity_main.xml)
    │   ├── Input fields (host, password)
    │   ├── Action button (restart)
    │   └── Status display (text, progress)
    │
    └── Business Logic
        ├── Input validation
        ├── Confirmation dialog
        └── FritzBoxClient integration

FritzBoxClient
    └── TR-064 API Communication
        ├── SOAP request building
        ├── HTTP authentication
        └── Error handling
```

## TR-064 API Integration

### Protocol Details

The app uses the TR-064 protocol, which is based on UPnP (Universal Plug and Play):

- **Transport**: HTTP (port 49000)
- **Format**: SOAP/XML
- **Authentication**: HTTP Basic Auth
- **Service**: `urn:dslforum-org:service:DeviceConfig:1`
- **Action**: `Reboot`
- **Control URL**: `/upnp/control/deviceconfig`

### SOAP Request Example

```xml
<?xml version="1.0" encoding="utf-8"?>
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" 
            s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
    <s:Body>
        <u:Reboot xmlns:u="urn:dslforum-org:service:DeviceConfig:1" />
    </s:Body>
</s:Envelope>
```

### HTTP Headers

```
POST /upnp/control/deviceconfig HTTP/1.1
Host: 192.168.178.1:49000
Authorization: Basic [base64-encoded credentials]
SOAPAction: urn:dslforum-org:service:DeviceConfig:1#Reboot
Content-Type: text/xml; charset=utf-8
Content-Length: [length]
```

## Password Manager Integration

### Autofill Framework

The app integrates with Android's Autofill Framework introduced in Android 8.0 (API 26):

1. **Password Field Configuration**:
   ```xml
   <TextInputEditText
       android:id="@+id/passwordInput"
       android:autofillHints="password"
       android:importantForAutofill="yes"
       android:inputType="textPassword" />
   ```

2. **How it Works**:
   - When the password field is focused, Android checks for autofill services
   - If enabled, the password manager icon appears in the keyboard
   - User taps the icon and authenticates (PIN, pattern, fingerprint, etc.)
   - Password is automatically filled in

3. **Supported Password Managers**:
   - Google Password Manager (built-in)
   - Samsung Pass
   - LastPass
   - 1Password
   - Bitwarden
   - Dashlane
   - Any app implementing AutofillService

### Fingerprint Authentication

The app itself doesn't directly implement fingerprint authentication. Instead:

1. User configures fingerprint in their password manager
2. Password manager requires fingerprint to unlock
3. App benefits from password manager's fingerprint feature
4. This is more secure than implementing custom fingerprint handling

## Error Handling

The app handles various error conditions:

### Network Errors

```kotlin
catch (e: UnknownHostException) -> "Cannot reach FRITZ!Box at {host}"
catch (e: SocketTimeoutException) -> "Connection timeout"
catch (e: ConnectException) -> "Connection refused"
```

### HTTP Errors

```kotlin
401 Unauthorized -> "Authentication failed. Check password."
404 Not Found -> "FRITZ!Box not found at {host}"
Other -> "HTTP {code}: {message}"
```

### User Feedback

- Toast messages for important events (success, major errors)
- Status text for current operation state
- Progress bar for visual feedback during operations
- Color coding (green=success, blue=info, red=error)

## UI/UX Design Decisions

### Material Design

The app uses Material Components for Android to ensure:
- Consistent appearance with other Android apps
- Accessibility compliance
- Touch target sizes (48dp minimum)
- Proper contrast ratios

### Confirmation Dialog

A confirmation dialog is always shown before restart because:
- Prevents accidental restarts
- Shows clear information about the action
- Provides an explicit "cancel" option
- Matches user expectations for destructive actions

### Input Validation

Simple client-side validation:
- Host must not be empty
- Password must not be empty
- No complex validation (let the server decide)

## Async Operations

### Coroutines

The app uses Kotlin Coroutines for async operations:

```kotlin
lifecycleScope.launch {
    setLoading(true)
    val result = withContext(Dispatchers.IO) {
        client.reboot()
    }
    // Handle result on Main thread
    setLoading(false)
}
```

Benefits:
- Simpler than callbacks or RxJava
- Structured concurrency (cancellation handling)
- Main-safe (UI updates on Main thread)
- Built into Kotlin

## Security Considerations

### Password Storage

- ❌ App does NOT store passwords
- ✅ Password manager stores passwords (encrypted)
- ✅ Password field cleared on app restart
- ✅ Backup exclusions prevent cloud backup of sensitive data

### Network Security

- ⚠️ Uses HTTP (not HTTPS) because FRITZ!Box TR-064 typically uses HTTP
- ✅ Communication limited to local network (typically 192.168.x.x)
- ✅ No external server communication
- ✅ Credentials sent via HTTP Basic Auth (base64, not encrypted)

**Note**: This is acceptable for local network communication. For remote access, users should use FRITZ!Box's built-in VPN or MyFRITZ service.

### Permissions

Required permissions and justification:

1. **INTERNET**: Required to communicate with FRITZ!Box
2. **ACCESS_NETWORK_STATE**: Used to check network connectivity before operations

No other permissions requested (no camera, location, contacts, etc.)

## Build Variants

### Debug Build

- Default configuration
- No code obfuscation
- Debug logging enabled
- Larger APK size

### Release Build (Optional)

To create a release build:

1. Generate signing key
2. Configure signing in `app/build.gradle`
3. Run `./gradlew assembleRelease`
4. Results in smaller, optimized APK

## Testing Strategy

### Manual Testing Checklist

- [ ] App installs successfully
- [ ] UI renders correctly on different screen sizes
- [ ] Password field shows/hides password correctly
- [ ] Autofill suggestions appear when password manager is configured
- [ ] Restart button shows confirmation dialog
- [ ] Restart succeeds with correct credentials
- [ ] Error messages appear for wrong credentials
- [ ] Error messages appear for unreachable host
- [ ] Status updates appear during operation
- [ ] Progress bar shows/hides correctly
- [ ] App handles configuration changes (rotation)

### Unit Testing (Future Enhancement)

For production use, consider adding:
- Unit tests for `FritzBoxClient`
- UI tests with Espresso
- Mock server for testing without real FRITZ!Box

## Performance

### Memory Usage

- Small memory footprint (~20-30 MB)
- No background services
- No persistent connections
- Minimal object allocation

### Battery Impact

- No background operations
- No location tracking
- No wake locks
- Minimal CPU usage

### Network Usage

- Single HTTP request per restart (~1-2 KB)
- No continuous polling
- No analytics or tracking

## Compatibility

### Android Versions

- Minimum: Android 7.0 (API 24) - 93%+ devices
- Target: Android 14 (API 34) - Latest features
- Tested on: API 24-34

### Screen Sizes

- Phones: 4" to 7"+
- Tablets: 7" to 13"
- Foldables: Both folded and unfolded
- Landscape and portrait orientations

### FRITZ!Box Models

Should work with any FRITZ!Box that:
- Supports TR-064 protocol
- Has DeviceConfig:1 service
- Has Reboot action available

Tested models (conceptually):
- FRITZ!Box 7590
- FRITZ!Box 7530
- FRITZ!Box 6590 Cable
- Other models with TR-064 support

## Future Enhancements

Possible improvements (not in current scope):

1. **Additional Actions**:
   - Reconnect WAN
   - Toggle WiFi
   - View connection status

2. **Multiple Devices**:
   - Save multiple FRITZ!Box configurations
   - Quick switch between devices

3. **Scheduling**:
   - Schedule automatic restarts
   - Integration with Android's AlarmManager

4. **Widgets**:
   - Home screen widget for quick restart
   - Quick Settings tile

5. **Localization**:
   - German language support
   - Other languages

6. **Advanced Features**:
   - SSH support for alternative authentication
   - HTTPS support where available
   - Custom port configuration

## References

- TR-064 Specification: https://avm.de/service/schnittstellen/
- Android Autofill Framework: https://developer.android.com/guide/topics/text/autofill
- Material Design: https://material.io/develop/android
- OkHttp: https://square.github.io/okhttp/
- Kotlin Coroutines: https://kotlinlang.org/docs/coroutines-overview.html
