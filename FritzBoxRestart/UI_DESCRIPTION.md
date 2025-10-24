# FRITZ!Box Restart Android App - UI Overview

This document describes the user interface of the FRITZ!Box Restart Android app since we cannot include actual screenshots in the repository.

## Main Screen

The app has a single, simple screen with the following elements:

### Header Section
- **App Icon**: FRITZ!Box logo (currently using default Android icon)
- **Title**: "FRITZ!Box Restart" in bold, primary color text (FRITZ!Box red: #E30613)

### Input Section

1. **Host Input Field**
   - Label: "FRITZ!Box IP Address"
   - Default value: `192.168.178.1`
   - Material Design outlined text input
   - Keyboard type: Text
   - Action: Next (moves to password field)

2. **Password Input Field**
   - Label: "Password"
   - Material Design outlined text input with password toggle
   - Shows/hides password with eye icon button
   - Keyboard type: Password
   - Action: Done
   - **Autofill support**: Shows autofill suggestions from password managers
   - **Fingerprint support**: When using password manager with fingerprint unlock

### Action Section

3. **Restart Button**
   - Text: "Restart FRITZ!Box"
   - Material Design outlined button
   - Icon: Rotate/refresh icon
   - Full width
   - Disabled while operation is in progress

### Status Section

4. **Status Text**
   - Shows current operation status:
     - Empty when idle
     - "Connecting to FRITZ!Box…" (blue) when connecting
     - "Sending restart command…" (blue) when sending
     - "Restart command sent successfully!" (green) on success
     - "Error: [error message]" (red) on failure

5. **Progress Bar**
   - Circular progress indicator
   - Hidden when not in progress
   - Visible during connection and restart operations

### Footer Section

6. **Help Text**
   - Small gray text at bottom
   - "Enter your FRITZ!Box password and tap the restart button. The router will reboot and be unavailable for 1-2 minutes."

## Confirmation Dialog

When the restart button is tapped, a confirmation dialog appears:

- **Title**: "Restart FRITZ!Box?"
- **Icon**: Warning/alert icon
- **Message**: 
  ```
  Are you sure you want to restart your FRITZ!Box?
  
  Host: 192.168.178.1
  
  This will interrupt your internet connection for 1-2 minutes.
  ```
- **Buttons**:
  - "NO" (negative button, dismisses dialog)
  - "YES" (positive button, proceeds with restart)

## Success Toast

After successful restart:
- Toast message: "FRITZ!Box is restarting. Please wait 1-2 minutes."
- Duration: LONG (3.5 seconds)

## Error Toast

After failed restart:
- Toast message: Specific error message (e.g., "Connection refused. Please check if FRITZ!Box is accessible.")
- Duration: LONG (3.5 seconds)

## Color Scheme

- **Primary color**: FRITZ!Box Red (#E30613)
- **Success color**: Green (#4CAF50 / holo_green_dark)
- **Error color**: Red (#F44336 / holo_red_dark)
- **Info color**: Blue (#2196F3 / holo_blue_dark)
- **Background**: White
- **Text**: Dark gray/black

## Interaction States

### Idle State
- All fields enabled
- Restart button enabled
- No status text
- Progress bar hidden

### Loading State
- All fields disabled (grayed out)
- Restart button disabled
- Status text visible (blue)
- Progress bar visible

### Success State
- All fields enabled
- Restart button enabled
- Status text visible (green)
- Progress bar hidden
- Success toast shown

### Error State
- All fields enabled
- Restart button enabled
- Status text visible (red)
- Progress bar hidden
- Error toast shown

## Password Manager Integration

The password field is configured to work with Android's Autofill Framework:

1. When the password field is focused, the password manager icon appears in the keyboard
2. Tapping it shows saved passwords for "192.168.178.1" or similar entries
3. If fingerprint is configured in the password manager, it prompts for fingerprint
4. Password is automatically filled in after authentication

This works with:
- Google Password Manager (built into Android)
- Samsung Pass
- LastPass
- 1Password
- Bitwarden
- And other password managers that support Android Autofill Framework

## Accessibility

The app supports:
- TalkBack screen reader
- Large text sizes
- High contrast mode
- Keyboard navigation (tab through fields)

## Screen Sizes

The app uses ConstraintLayout and works on:
- Phones (4" to 7"+)
- Tablets (7" to 13")
- Foldables (in both folded and unfolded states)

All layouts are responsive and adjust to different screen sizes.
