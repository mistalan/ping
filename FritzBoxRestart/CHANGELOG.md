# Changelog

All notable changes to the FRITZ!Box Restart Android app will be documented in this file.

## [1.1.2] - 2025-10-24

### Fixed
- **HTTP 500 Error with "Action Not Authorized" (Error Code 606) - FINAL FIX**
  - Fixed incorrect header format that was still causing error 606 even with Content-Type header
  - The issue was that OkHttp was combining `content-type` and `charset` into a single header
  - FRITZ!Box TR-064 API requires separate lowercase headers matching Python fritzconnection format
  - Now sends headers exactly as Python fritzconnection does:
    - `content-type: text/xml` (lowercase, separate)
    - `charset: utf-8` (separate)
    - `soapaction: urn:dslforum-org:service:DeviceConfig:1#Reboot`
  - Previously sent: `Content-Type: text/xml; charset=utf-8` (combined, capitalized)
  - This resolves the persistent error 606 "Action Not Authorized"

### Technical Details
- Modified `FritzBoxClient.kt` to use `.toByteArray().toRequestBody(null)` instead of `.toRequestBody("text/xml".toMediaType())`
- Using `null` MediaType prevents OkHttp from automatically adding/combining Content-Type headers
- Headers are now manually added with lowercase names to match Python fritzconnection exactly
- Updated tests to verify headers are sent in correct format
- All 13 unit tests passing with correct header validation

## [1.1.1] - 2025-10-24

### Fixed
- **HTTP 500 Error with "Action Not Authorized" (Error Code 606)**
  - Fixed missing `Content-Type` header in HTTP requests
  - The `Content-Type` header was not being sent, causing FRITZ!Box to reject the request
  - Now explicitly sets `Content-Type: text/xml; charset=utf-8` header
  - This ensures the header is preserved through the OkHttp authentication chain
  - Matches the header format used by the Python fritzconnection library
  - Resolves UPnP error 606 "Action Not Authorized"
  - **NOTE: This fix was incomplete - see v1.1.2 for the final fix**

### Added
- **Comprehensive Unit Test Suite**
  - 13 unit tests for `FritzBoxClient` covering all critical functionality
  - Tests verify Content-Type header is always sent (regression prevention)
  - Tests validate SOAP envelope format matches Python fritzconnection
  - Tests cover success scenarios, error handling, and edge cases
  - Uses MockWebServer for realistic HTTP testing
  - All tests pass successfully with 100% success rate
  - Test documentation in `app/src/test/kotlin/com/fritzbox/restart/README.md`

### Technical Details
- Modified `FritzBoxClient.kt` to explicitly add `Content-Type` header
- The header was being set via `RequestBody.toRequestBody()` but not preserved
- Now uses `.addHeader("Content-Type", "text/xml; charset=utf-8")` to ensure it's sent
- Combined with existing `charset: utf-8` header for compatibility
- Added test dependencies: kotlinx-coroutines-test, mockwebserver, mockito, robolectric
- Modified `FritzBoxClient` to support port in host parameter for testing

## [1.1.0] - 2025-10-24

### Added - Comprehensive Debugging and Diagnostic System

This release adds extensive diagnostic capabilities to help identify and resolve the persistent HTTP 500 error that some users experience.

#### New Features:

1. **Diagnostic Report Generator**
   - Generates comprehensive diagnostic reports with one tap
   - Includes system information, network diagnostics, and all logs
   - Provides comparison with working Python client
   - Includes troubleshooting checklist and suggestions
   - Can be shared directly from the app

2. **Network Diagnostics**
   - Automatic network connectivity tests before each request
   - DNS resolution check
   - Host reachability test (ping)
   - Port accessibility tests (TR-064 port 49000, HTTP 80, HTTPS 443)
   - Provides troubleshooting suggestions based on test results

3. **System Information Collector**
   - Collects app version, Android version, SDK level
   - Device manufacturer, model, brand information
   - Hardware details and supported ABIs
   - Automatically included in diagnostic reports

4. **Enhanced HTTP Logging**
   - Detailed logging of all HTTP requests and responses
   - Complete header logging (with password redaction)
   - Request/response body logging
   - Request duration tracking
   - SOAP fault parsing for detailed error messages

5. **SOAP Envelope Validation**
   - Validates SOAP envelope format matches Python client
   - Checks for single-line format, XML declaration, closing tags
   - Logs envelope length and format details

6. **Enhanced Error Messages**
   - More specific error messages with troubleshooting hints
   - Suggests checking logs for HTTP 500 errors
   - Includes network diagnostic results in error flow
   - Full stack traces logged for unexpected errors

7. **Updated Log Viewer**
   - New "Generate Diagnostic Report" button
   - Progress indicator during report generation
   - Option to view or share diagnostic reports
   - Enhanced menu with diagnostic option

8. **Comprehensive Documentation**
   - New TROUBLESHOOTING.md guide with step-by-step debugging
   - Updated README with diagnostic report instructions
   - Information checklist for reporting issues
   - Comparison guide with Python client

### Changed
- MainActivity now runs network diagnostics before each request
- Error messages now suggest viewing logs
- Log viewer layout updated with diagnostic button
- Enhanced troubleshooting section in README

### Technical Details
- New files: NetworkDiagnostics.kt, SystemInfoCollector.kt, DiagnosticReportGenerator.kt
- OkHttp interceptor added for request/response logging
- SOAP fault parsing for better error details
- Network permission handling for diagnostics

### For Users Experiencing HTTP 500 Errors

This release provides all the tools needed to identify why the error occurs:

1. **Generate a diagnostic report** (tap ℹ️ → Generate Diagnostic Report)
2. **Test with Python script** to confirm TR-064 works
3. **Share the diagnostic report** when reporting the issue
4. **Include**: FRITZ!Box model, firmware version, Python test result

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed instructions.

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
