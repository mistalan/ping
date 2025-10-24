# FRITZ!Box Restart - Android App

A simple Android application to restart your FRITZ!Box router with a single button press.

## Features

- ✅ Simple, clean user interface
- ✅ Password input with show/hide toggle
- ✅ Autofill support for password managers (Google/Samsung)
- ✅ Confirmation dialog before restart
- ✅ Real-time status updates
- ✅ Error handling with user-friendly messages
- ✅ **Comprehensive logging system for debugging**
- ✅ **Log viewer with share/copy functionality**
- ✅ No Play Store integration required - sideload the APK

## Requirements

- Android 7.0 (API 24) or higher
- FRITZ!Box router accessible on your local network
- TR-064 API enabled on FRITZ!Box (usually enabled by default)

## Installation

### Option 1: Build from source using Android Studio

1. Install [Android Studio](https://developer.android.com/studio)
2. Open the `FritzBoxRestart` folder in Android Studio
3. Wait for Gradle sync to complete
4. Connect your Android device via USB with USB debugging enabled
5. Click **Run** (or press Shift+F10)

### Option 2: Build APK for sideloading

1. Open the project in Android Studio
2. Go to **Build > Build Bundle(s) / APK(s) > Build APK(s)**
3. Wait for the build to complete
4. The APK will be in `app/build/outputs/apk/debug/app-debug.apk`
5. Transfer the APK to your phone and install it

**Note**: You need to enable "Install from Unknown Sources" in your Android settings to install the APK.

## Usage

1. Launch the app
2. Enter your FRITZ!Box IP address (default: 192.168.178.1)
3. Enter your FRITZ!Box password
   - The password field supports autofill from Google/Samsung password managers
   - You can use fingerprint unlock if configured in your password manager
4. Tap **Restart FRITZ!Box**
5. Confirm the restart in the dialog
6. Wait 1-2 minutes for the router to reboot

### Viewing Logs (for Debugging)

The app includes a comprehensive logging system to help diagnose issues:

1. Tap the **info icon** (ℹ️) in the top-right corner of the main screen
2. This opens the **Log Viewer** showing all app activity
3. You can:
   - **Refresh**: Update logs with latest entries
   - **Copy**: Copy logs to clipboard
   - **Share**: Send logs via email/messaging apps
   - **Clear**: Delete all logs

**When to share logs:**
- If you encounter HTTP 500 errors
- Authentication failures
- Connection timeouts
- Any unexpected behavior

The logs contain detailed information about:
- SOAP requests sent to FRITZ!Box
- Authentication attempts
- HTTP response codes and messages
- Error details with stack traces

## Configuration

The app uses these default settings:
- Host: `192.168.178.1` (standard FRITZ!Box IP)
- Connection timeout: 10 seconds
- Username: Not required (most FRITZ!Box setups don't need it)

You can change the host IP if your FRITZ!Box uses a different address.

## Security

- Passwords are NOT stored in the app
- Password input supports Android autofill framework
- Sensitive data is excluded from backups
- All communication uses HTTP (as FRITZ!Box TR-064 doesn't use HTTPS by default)
- The app requires INTERNET and ACCESS_NETWORK_STATE permissions

## Technical Details

### Dependencies

- AndroidX Core, AppCompat, Material Components
- ConstraintLayout for UI
- OkHttp 4.12.0 for HTTP requests
- Kotlin Coroutines for async operations

### TR-064 API

The app communicates with FRITZ!Box using the TR-064 protocol (UPnP-based):
- Service: `urn:dslforum-org:service:DeviceConfig:1`
- Action: `Reboot`
- Control URL: `http://{host}:49000/upnp/control/deviceconfig`

The implementation uses SOAP/XML requests with HTTP Digest Authentication (RFC 2617).

**Recent Fixes:**
- **v1.0.2** (Latest): Fixed HTTP headers to use separate charset header instead of combined Content-Type
  - Changed from: `Content-Type: text/xml; charset=utf-8`
  - Changed to: `Content-Type: text/xml` + separate `charset: utf-8` header
  - This non-standard header format matches the Python fritzconnection library exactly
  - **This should resolve all remaining HTTP 500 errors**
- **v1.0.1**: Fixed SOAP envelope format (single-line, lowercase soapaction header)
  - Added comprehensive logging throughout the codebase
  - Created log viewer for easy debugging and issue reporting

## Troubleshooting

### "HTTP 500: Internal Server Error"
**This error has been fixed in v1.0.2**. If you still encounter it:
- Make sure you have the latest version of the app
- Check the logs (tap ℹ️ icon) for detailed error information
- Verify TR-064 is enabled in FRITZ!Box settings
- Try restarting your FRITZ!Box manually via web interface first

### "Authentication failed"
- Check if your password is correct
- Verify that TR-064 is enabled in FRITZ!Box settings (System > FRITZ!Box Users > Login to the Home Network)
- Try using the web interface password
- The app uses HTTP Digest Authentication which is the standard for FRITZ!Box TR-064 API
- Check logs for detailed authentication error messages

### "Cannot reach FRITZ!Box"
- Verify the IP address is correct
- Make sure you're connected to the same network as the FRITZ!Box
- Check if TR-064 is enabled in FRITZ!Box settings
- Review logs to see the exact connection error

### "Connection timeout"
- Check your network connection
- Verify the FRITZ!Box is powered on and accessible
- Try increasing timeout (currently 10 seconds)

### App won't install
- Enable "Install from Unknown Sources" in Android settings
- Make sure you have enough storage space

### Getting Help
If you encounter issues:
1. Open the Log Viewer (ℹ️ icon)
2. Try the operation that fails
3. Share the logs via email/GitHub issue
4. Include your FRITZ!Box model and Android version

## Building for Production

To create a production-ready APK:

1. Generate a signing key:
   ```bash
   keytool -genkey -v -keystore fritzbox-restart.keystore -alias fritzbox -keyalg RSA -keysize 2048 -validity 10000
   ```

2. Create `keystore.properties` in the project root:
   ```properties
   storeFile=path/to/fritzbox-restart.keystore
   storePassword=your_store_password
   keyAlias=fritzbox
   keyPassword=your_key_password
   ```

3. Build release APK:
   ```bash
   ./gradlew assembleRelease
   ```

## License

This project is provided as-is for personal use with FRITZ!Box routers.

## Related Projects

This Android app is part of the [mistalan/ping](https://github.com/mistalan/ping) repository, which includes:
- Python version: `fritzbox_restart.py`
- Network monitoring tools: `NetWatch.ps1`, `fritzlog_pull.py`
- Windows GUI: `NetWatchUI.ps1`
