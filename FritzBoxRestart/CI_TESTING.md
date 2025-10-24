# Android Unit Tests in CI/CD

## Overview

The GitHub Actions CI workflow has been updated to automatically run Android unit tests on every push and pull request.

## CI Workflow Changes

### New Job: `test-android-unit`

A dedicated job has been added to run Android unit tests:

**Job Details:**
- **Name:** Test Android Unit Tests
- **Runs on:** ubuntu-latest
- **Dependencies:** None (runs in parallel with other checks)
- **Runs:** Before the APK build job

**Steps:**
1. Checkout code
2. Set up JDK 17
3. Setup Android SDK
4. Cache Gradle packages
5. Run unit tests (`./gradlew test`)
6. Parse and display test results
7. Upload test results as artifacts
8. Generate test summary in GitHub Actions UI

### Test Results

The job provides:

1. **Test Execution:** Runs all unit tests in `FritzBoxRestart/app/src/test/`
2. **Result Artifacts:** Uploads test results and reports for 30 days
   - XML test results: `app/build/test-results/`
   - HTML test reports: `app/build/reports/tests/`
3. **Summary Report:** Displays test statistics in GitHub Actions summary
   - Total tests count
   - Failures count
   - Errors count
   - Skipped tests count

### Build Job Update

The `build-android-apk` job now:
- **Depends on:** `test-android-unit` (won't run if tests fail)
- **Runs:** Only after tests pass
- **Purpose:** Builds the APK after tests are verified

### All Checks Complete

The final validation job now includes:
- Validate PowerShell Scripts
- Validate Python Scripts (3.12)
- Lint Python Code
- Security Scan
- **Test Android Unit Tests** ← NEW
- Build Android APK

## What This Means

### For Developers

✅ **Automated Testing:** Unit tests run automatically on every push/PR
✅ **Early Detection:** Test failures caught before APK build
✅ **Test Reports:** Detailed test results available as artifacts
✅ **CI Summary:** Quick overview of test results in GitHub UI

### For Pull Requests

When you create or update a PR:
1. CI automatically runs all 13 unit tests
2. Test results appear in the checks section
3. PR cannot be merged if tests fail (optional protection rule)
4. Test reports available for download

### For Main Branch

Every commit to main:
1. Runs full test suite
2. Uploads test results as artifacts
3. Shows test summary in workflow run
4. Only builds APK if tests pass

## Running Tests Locally

Before pushing, run tests locally:

```bash
cd FritzBoxRestart
./gradlew test
```

View test reports:
```bash
open app/build/reports/tests/testDebugUnitTest/index.html
```

## Test Coverage

Current unit test suite (13 tests):
- ✅ HTTP header validation (Content-Type, soapaction, charset)
- ✅ SOAP envelope format
- ✅ Success responses (HTTP 200)
- ✅ Error responses (HTTP 401, 404, 500)
- ✅ SOAP fault parsing
- ✅ Network error handling
- ✅ Request format verification

## CI Workflow Diagram

```
┌─────────────────────────────────────────────┐
│  Push to main / PR to main                  │
└─────────────────┬───────────────────────────┘
                  │
                  ├─► Validate PowerShell
                  ├─► Validate Python
                  ├─► Lint Python
                  ├─► Security Scan
                  ├─► Test Android Unit ───┐
                  │                        │
                  │   (All run in parallel)│
                  │                        │
                  └────────────────────────┼─► All tests pass?
                                           │
                                           ├─► YES ─► Build Android APK
                                           │
                                           └─► NO ──► Fail workflow
```

## Benefits

1. **Quality Assurance:** Every code change is tested automatically
2. **Regression Prevention:** Tests catch breaking changes immediately
3. **Documentation:** Test results show what's working
4. **Confidence:** Merging code that passes all tests
5. **Debugging:** Test reports help identify issues quickly

## Artifact Retention

Test results are kept for **30 days** and include:
- XML test results (machine-readable)
- HTML test reports (human-readable)
- Test summaries

APK artifacts are kept for **90 days**.

## Troubleshooting

### If Tests Fail in CI

1. Check the test job logs in GitHub Actions
2. Download the test results artifact
3. Open the HTML report for detailed failure information
4. Run tests locally to reproduce the issue
5. Fix the failing tests
6. Push the fix

### If Tests Pass Locally but Fail in CI

- Check for environment-specific issues
- Verify all dependencies are declared in `build.gradle`
- Check for time-sensitive or random test failures
- Review CI logs for setup issues

## Future Enhancements

Potential improvements:
- Add code coverage reporting
- Add instrumentation tests (Android UI tests)
- Add performance benchmarks
- Add test result trending
- Add automatic PR comments with test results
