# Changelog

All notable changes to the FRITZ!Box Restart Android app will be documented in this file.

## [1.0.2] - 2025-10-24

### Fixed
- **HTTP 500 Internal Server Error** when restarting FRITZ!Box (second fix)
  - Fixed HTTP headers to match exact format expected by FRITZ!Box TR-064 API
  - Changed from combined `Content-Type: text/xml; charset=utf-8` header to separate headers
  - Now sends `Content-Type: text/xml` and `charset: utf-8` as separate headers
  - This non-standard header format matches the Python `fritzconnection` library exactly
  - Previous fix in v1.0.1 addressed SOAP envelope format but headers were still incorrect

## [1.0.1] - 2025-10-24

### Fixed
- **HTTP 500 Internal Server Error** when restarting FRITZ!Box (first attempt)
  - Fixed SOAP envelope format to match TR-064 specification exactly
  - Changed SOAP header from `SOAPAction` to `soapaction` (lowercase)
  - Removed extraneous whitespace from SOAP body that caused parsing errors
  - SOAP envelope now matches format used by `fritzconnection` Python library
  - Note: This fix was incomplete; v1.0.2 addresses the remaining header issue

### Added
- **Comprehensive logging system**
  - `LogManager` class for centralized log management
  - Logs written to app's external files directory
  - Automatic log rotation when file exceeds 500KB
  - Timestamps with millisecond precision for all log entries
  
- **Log Viewer Activity**
  - View all application logs in chronological order
  - Refresh logs in real-time
  - Copy logs to clipboard
  - Share logs via email/messaging apps
  - Clear all logs
  - Accessible via info icon (ℹ️) in main menu
  
- **Enhanced debugging throughout app**
  - Detailed logging in `FritzBoxClient` for SOAP requests/responses
  - Authentication step logging in `DigestAuthenticator`
  - Error logging with full exception details in `MainActivity`
  - All HTTP response codes logged with body content

### Changed
- Updated error messages to be more specific for HTTP 500 errors
- Enhanced error handling with more detailed user feedback

## [1.0.0] - 2025-10-23

### Added
- Initial release of FRITZ!Box Restart Android app
- Simple UI with Material Design components
- FRITZ!Box IP address input (default: 192.168.178.1)
- Password input with show/hide toggle
- Autofill support for password managers
- Confirmation dialog before restart
- Real-time status updates during operation
- Error handling with user-friendly messages
- HTTP Digest Authentication for TR-064 API
- SOAP/XML communication with FRITZ!Box
- Connection timeout handling (10 seconds)
- Support for Android 7.0 (API 24) and higher
