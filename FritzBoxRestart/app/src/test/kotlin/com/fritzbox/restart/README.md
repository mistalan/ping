# FritzBoxClient Unit Tests

## Overview

This directory contains unit tests for the FRITZ!Box Restart Android app, specifically testing the `FritzBoxClient` class that handles communication with the FRITZ!Box router via the TR-064 API.

## Test Coverage

The test suite (`FritzBoxClientTest.kt`) includes 13 comprehensive tests that verify:

### Header Tests (Critical for Issue #53 Fix)
1. ✅ **Content-Type header is sent** - Verifies the fix for HTTP 500 error
2. ✅ **soapaction header is sent** - Verifies SOAP action is correct
3. ✅ **charset header is sent** - Verifies charset specification
4. ✅ **All required headers in single request** - Comprehensive header validation

### SOAP Envelope Tests
5. ✅ **Correct SOAP envelope format** - Validates XML structure
6. ✅ **SOAP envelope matches Python fritzconnection** - Format compatibility
7. ✅ **POST request to correct URL** - URL and method verification

### Success/Error Handling Tests
8. ✅ **Success on HTTP 200** - Happy path test
9. ✅ **Failure on HTTP 401** - Authentication error handling
10. ✅ **Failure on HTTP 404** - Not found error handling
11. ✅ **Failure on HTTP 500 with SOAP fault** - Server error with fault parsing
12. ✅ **SOAP fault parsing** - Extracts error details correctly
13. ✅ **Connection timeout handling** - Network error resilience

## Running the Tests

### Run all tests
```bash
./gradlew test
```

### Run only FritzBoxClient tests
```bash
./gradlew test --tests FritzBoxClientTest
```

### Run specific test
```bash
./gradlew test --tests FritzBoxClientTest."reboot sends Content-Type header"
```

### View test report
After running tests, open:
```
app/build/reports/tests/testDebugUnitTest/index.html
```

## Test Results

All 13 tests pass successfully:

```
testsuite: com.fritzbox.restart.FritzBoxClientTest
tests: 13
skipped: 0
failures: 0
errors: 0
time: ~8.3 seconds
```

## Key Test: Content-Type Header

The most critical test for issue #53 is:

```kotlin
@Test
fun `reboot includes all required headers in single request`() = runTest {
    // Arrange
    mockWebServer.enqueue(MockResponse().setResponseCode(200))

    // Act
    client.reboot()

    // Assert - This is the critical test for the bug fix
    val request = mockWebServer.takeRequest()
    
    // Verify all three headers are present (the fix for issue #53)
    assertNotNull("Content-Type header must be present", request.getHeader("Content-Type"))
    assertNotNull("soapaction header must be present", request.getHeader("soapaction"))
    assertNotNull("charset header must be present", request.getHeader("charset"))
    
    // Verify exact values
    assertEquals("text/xml; charset=utf-8", request.getHeader("Content-Type"))
    assertEquals("urn:dslforum-org:service:DeviceConfig:1#Reboot", request.getHeader("soapaction"))
    assertEquals("utf-8", request.getHeader("charset"))
}
```

This test ensures that the `Content-Type` header is always sent, preventing the HTTP 500 / UPnP Error 606 "Action Not Authorized" issue.

## Technologies Used

- **JUnit 4.13.2** - Test framework
- **Kotlin Coroutines Test** - For testing suspend functions
- **OkHttp MockWebServer** - For mocking HTTP server responses
- **Mockito** - For mocking dependencies
- **Robolectric** - For Android framework mocking

## Test Philosophy

These tests follow the principle of testing behavior, not implementation:

1. **Black-box testing**: Tests verify what the client sends/receives, not how
2. **Realistic scenarios**: Uses MockWebServer to simulate actual HTTP communication
3. **Comprehensive coverage**: Tests success, errors, and edge cases
4. **Regression prevention**: Ensures issue #53 fix remains in place

## Continuous Integration

These tests are designed to run in CI/CD pipelines:
- Fast execution (~8 seconds for full suite)
- No external dependencies (uses mock server)
- Deterministic results
- Clear failure messages

## Adding New Tests

When adding new tests:

1. Follow the existing naming convention: `` `description of behavior` ``
2. Use Arrange-Act-Assert pattern
3. Add comments explaining what's being tested
4. Use descriptive assertion messages
5. Test one behavior per test method

## Maintenance

When modifying `FritzBoxClient.kt`:

1. Run tests before making changes (baseline)
2. Update/add tests for new functionality
3. Ensure all tests pass after changes
4. Update this README if test coverage changes
