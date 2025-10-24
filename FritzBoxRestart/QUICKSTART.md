# Quick Start Guide - FRITZ!Box Restart Android App

## Prerequisites

1. **Android Studio** - Download from https://developer.android.com/studio
2. **Android Phone** running Android 7.0 (API 24) or higher
3. **FRITZ!Box router** accessible on your local network

## Step 1: Install Android Studio

1. Download and install Android Studio from the official website
2. During installation, make sure to install:
   - Android SDK
   - Android SDK Platform
   - Android Virtual Device (optional, for testing in emulator)

## Step 2: Open the Project

1. Launch Android Studio
2. Select **Open an Existing Project**
3. Navigate to the `FritzBoxRestart` folder in this repository
4. Click **OK**
5. Wait for Gradle sync to complete (this may take a few minutes on first launch)

## Step 3: Build the APK

### Option A: Build and Install Directly to Phone

1. Enable **Developer Options** on your Android phone:
   - Go to Settings > About Phone
   - Tap "Build Number" 7 times
   - Go back to Settings > Developer Options
   - Enable **USB Debugging**

2. Connect your phone to computer via USB
3. In Android Studio, click the **Run** button (green play icon) or press **Shift+F10**
4. Select your device from the list
5. The app will be built and installed automatically

### Option B: Build APK for Sideloading

1. In Android Studio, go to **Build > Build Bundle(s) / APK(s) > Build APK(s)**
2. Wait for the build to complete
3. Click **locate** in the notification that appears (or navigate to `app/build/outputs/apk/debug/`)
4. Copy `app-debug.apk` to your phone (via USB, email, cloud storage, etc.)
5. On your phone:
   - Go to Settings > Security
   - Enable **Install from Unknown Sources** (or **Allow from this source** on newer Android versions)
   - Open the APK file with a file manager
   - Tap **Install**

## Step 4: Use the App

1. Open the **FRITZ!Box Restart** app
2. Enter your FRITZ!Box IP address (default is 192.168.178.1)
3. Enter your FRITZ!Box password
   - If you use a password manager, it should offer to autofill
   - You can use fingerprint to unlock if configured
4. Tap **Restart FRITZ!Box**
5. Confirm in the dialog
6. Wait 1-2 minutes for your router to reboot

## Troubleshooting

### Build Errors in Android Studio

**Gradle sync failed:**
- Make sure you have internet connection
- Go to File > Invalidate Caches and Restart
- Try Build > Clean Project, then Build > Rebuild Project

**SDK not found:**
- Go to Tools > SDK Manager
- Install Android SDK Platform 34 and build tools

**Missing dependencies:**
- Gradle should download them automatically
- Check your internet connection
- Try Build > Clean Project

### Installation Issues

**"App not installed" on phone:**
- Make sure you have enough storage space
- Enable "Install from Unknown Sources" in settings
- If updating an existing app, uninstall the old version first

**USB debugging not working:**
- Try a different USB cable
- Make sure to allow USB debugging when the popup appears on your phone
- Try running `adb devices` in terminal to check if device is recognized

### App Runtime Issues

**"Cannot reach FRITZ!Box":**
- Make sure your phone is connected to the same WiFi network
- Verify the IP address is correct (check your router's sticker or admin panel)
- Try pinging the IP from another device

**"Authentication failed":**
- Double-check your password
- Make sure TR-064 is enabled in FRITZ!Box (Home Network > Network > Network Settings)

## Building for Release (Optional)

To create a signed release APK for distribution:

1. Generate a signing key:
   ```bash
   keytool -genkey -v -keystore fritzbox-restart.keystore -alias fritzbox -keyalg RSA -keysize 2048 -validity 10000
   ```

2. Create `keystore.properties` in project root:
   ```properties
   storeFile=/path/to/fritzbox-restart.keystore
   storePassword=your_password
   keyAlias=fritzbox
   keyPassword=your_password
   ```

3. Update `app/build.gradle` to use the signing config (see Android documentation)

4. Build release APK:
   ```bash
   ./gradlew assembleRelease
   ```

5. The signed APK will be in `app/build/outputs/apk/release/app-release.apk`

## Next Steps

- Save your FRITZ!Box password in your password manager for easy autofill
- Add the app to your home screen for quick access
- Consider automating router restarts with Tasker or similar automation apps

## Resources

- Android Studio: https://developer.android.com/studio
- Android Developer Guide: https://developer.android.com/guide
- FRITZ!Box TR-064: https://avm.de/service/schnittstellen/
