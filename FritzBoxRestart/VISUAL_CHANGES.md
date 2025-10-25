# Visual Layout Changes

## Main Activity - Before and After

### BEFORE (3 input fields):
```
┌─────────────────────────────────────┐
│   FRITZ!Box Restart                 │
│         [Logo]                      │
│                                     │
│  ┌───────────────────────────────┐  │
│  │ FRITZ!Box IP Address          │  │
│  │ 192.168.178.1                 │  │
│  └───────────────────────────────┘  │
│                                     │
│  ┌───────────────────────────────┐  │
│  │ Password             [👁]     │  │
│  │ ••••••••                      │  │
│  └───────────────────────────────┘  │
│                                     │
│  ┌───────────────────────────────┐  │
│  │   Restart FRITZ!Box           │  │
│  └───────────────────────────────┘  │
│                                     │
│         Status messages             │
│         [Progress bar]              │
│                                     │
│    Help text about the app          │
└─────────────────────────────────────┘
```

### AFTER (4 input fields - username added):
```
┌─────────────────────────────────────┐
│   FRITZ!Box Restart                 │
│         [Logo]                      │
│                                     │
│  ┌───────────────────────────────┐  │
│  │ FRITZ!Box IP Address          │  │
│  │ 192.168.178.1                 │  │
│  └───────────────────────────────┘  │
│                                     │
│  ┌───────────────────────────────┐  │  ⬅️ NEW!
│  │ Username (optional)           │  │
│  │                               │  │
│  └───────────────────────────────┘  │
│                                     │
│  ┌───────────────────────────────┐  │
│  │ Password             [👁]     │  │
│  │ ••••••••                      │  │
│  └───────────────────────────────┘  │
│                                     │
│  ┌───────────────────────────────┐  │
│  │   Restart FRITZ!Box           │  │
│  └───────────────────────────────┘  │
│                                     │
│         Status messages             │
│         [Progress bar]              │
│                                     │
│    Help text about the app          │
└─────────────────────────────────────┘
```

**Key Change:** Added optional username field between host and password fields.

---

## Log Viewer Activity - Before and After

### BEFORE (4 buttons in 1 row - causes overlap on smaller screens):
```
┌─────────────────────────────────────┐
│ Application Logs              [←]   │
├─────────────────────────────────────┤
│                                     │
│  ┌────┐ ┌────┐ ┌─────┐ ┌─────┐    │ ⚠️ Buttons too small
│  │Ref │ │Copy│ │Share│ │Clear│    │    on smaller screens
│  │resh│ │    │ │     │ │     │    │
│  └────┘ └────┘ └─────┘ └─────┘    │
│                                     │
│  ┌───────────────────────────────┐  │
│  │  Generate Diagnostic Report   │  │
│  └───────────────────────────────┘  │
│                                     │
│  ┌───────────────────────────────┐  │
│  │ [Log content area]            │  │
│  │                               │  │
│  │ 2024-10-24 22:00:00 INFO...   │  │
│  │ MainActivity: App started     │  │
│  │                               │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

### AFTER (2 rows of 2 buttons - better spacing):
```
┌─────────────────────────────────────┐
│ Application Logs              [←]   │
├─────────────────────────────────────┤
│                                     │
│  ┌──────────────┐ ┌──────────────┐ │ ✅ Row 1: Better spacing
│  │   Refresh    │ │     Copy     │ │
│  └──────────────┘ └──────────────┘ │
│                                     │
│  ┌──────────────┐ ┌──────────────┐ │ ✅ Row 2: No overlap
│  │    Share     │ │    Clear     │ │
│  └──────────────┘ └──────────────┘ │
│                                     │
│  ┌───────────────────────────────┐  │
│  │  Generate Diagnostic Report   │  │
│  └───────────────────────────────┘  │
│                                     │
│  ┌───────────────────────────────┐  │
│  │ [Log content area]            │  │
│  │                               │  │
│  │ 2024-10-24 22:00:00 INFO...   │  │
│  │ MainActivity: App started     │  │
│  │                               │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

**Key Change:** Split 4 buttons from single row into 2 rows of 2 buttons each.

---

## Benefits Summary

### Username Field Addition:
✅ Users can now provide username for FRITZ!Box authentication
✅ Field is clearly marked as "optional" 
✅ Maintains backward compatibility (works without username)
✅ Follows Material Design guidelines
✅ Includes proper autofill hints

### Log Viewer Layout Fix:
✅ Buttons no longer overlap on smaller screens
✅ Better touch targets for usability
✅ More balanced visual appearance
✅ Maintains all original functionality
✅ Uses proper constraint layout techniques

---

## Technical Implementation Notes

### Username Handling Flow:
1. User enters username in MainActivity (optional)
2. MainActivity captures username text
3. If username is blank → passed as `null` to FritzBoxClient
4. FritzBoxClient converts `null` to empty string for DigestAuthenticator
5. DigestAuthenticator uses username in HTTP Digest authentication

### Layout Constraint Updates:
- Main Activity: Password field now constrains to username field instead of host field
- Log Viewer: Second button row constrains to first button row
- All other constraints adjusted to maintain proper spacing
