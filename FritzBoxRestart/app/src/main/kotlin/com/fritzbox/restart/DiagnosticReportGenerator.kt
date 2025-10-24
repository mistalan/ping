package com.fritzbox.restart

import android.content.Context
import android.util.Log
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.text.SimpleDateFormat
import java.util.*

/**
 * Generates comprehensive diagnostic reports for troubleshooting
 */
object DiagnosticReportGenerator {
    private const val TAG = "DiagnosticReport"
    
    /**
     * Generate a comprehensive diagnostic report
     */
    suspend fun generateReport(context: Context, host: String): String = withContext(Dispatchers.IO) {
        LogManager.log(TAG, "Generating comprehensive diagnostic report", Log.INFO)
        
        val timestamp = SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault()).format(Date())
        val systemInfo = SystemInfoCollector.collectSystemInfo(context)
        val diagnostics = NetworkDiagnostics.runDiagnostics(context, host)
        val logs = LogManager.getLogs()
        
        buildString {
            appendLine("╔═══════════════════════════════════════════════════════════════╗")
            appendLine("║         FRITZ!Box Restart - Diagnostic Report                 ║")
            appendLine("╚═══════════════════════════════════════════════════════════════╝")
            appendLine()
            appendLine("Generated: $timestamp")
            appendLine()
            appendLine("═══════════════════════════════════════════════════════════════")
            appendLine("SYSTEM INFORMATION")
            appendLine("═══════════════════════════════════════════════════════════════")
            appendLine()
            appendLine(systemInfo.toString())
            appendLine()
            appendLine("═══════════════════════════════════════════════════════════════")
            appendLine("NETWORK DIAGNOSTICS")
            appendLine("═══════════════════════════════════════════════════════════════")
            appendLine()
            appendLine(diagnostics.toString())
            appendLine()
            if (diagnostics.hasIssues()) {
                appendLine(diagnostics.getSuggestions())
                appendLine()
            }
            appendLine("═══════════════════════════════════════════════════════════════")
            appendLine("COMPARISON WITH WORKING PYTHON CLIENT")
            appendLine("═══════════════════════════════════════════════════════════════")
            appendLine()
            appendLine("The Python fritzconnection library sends the following:")
            appendLine()
            appendLine("Headers:")
            appendLine("  soapaction: urn:dslforum-org:service:DeviceConfig:1#Reboot")
            appendLine("  content-type: text/xml")
            appendLine("  charset: utf-8")
            appendLine()
            appendLine("SOAP Envelope (single line, no whitespace):")
            appendLine("  <?xml version=\"1.0\" encoding=\"utf-8\"?><s:Envelope...")
            appendLine()
            appendLine("If the Android app sends different headers or envelope format,")
            appendLine("that could explain the HTTP 500 error.")
            appendLine()
            appendLine("═══════════════════════════════════════════════════════════════")
            appendLine("TROUBLESHOOTING CHECKLIST")
            appendLine("═══════════════════════════════════════════════════════════════")
            appendLine()
            appendLine("□ Network connected: ${if (diagnostics.networkConnected) "✓ YES" else "✗ NO"}")
            appendLine("□ DNS resolves host: ${if (diagnostics.dnsResolvable) "✓ YES" else "✗ NO"}")
            appendLine("□ Host reachable: ${if (diagnostics.hostReachable) "✓ YES" else "✗ NO"}")
            appendLine("□ TR-064 port open: ${if (diagnostics.tr064PortOpen) "✓ YES" else "✗ NO"}")
            appendLine("□ HTTP port open: ${if (diagnostics.httpPortOpen) "✓ YES" else "✗ NO"}")
            appendLine()
            appendLine("If all checks pass but HTTP 500 occurs, the issue is likely:")
            appendLine("  1. SOAP envelope format mismatch")
            appendLine("  2. HTTP header format mismatch")
            appendLine("  3. Authentication method mismatch")
            appendLine("  4. FRITZ!Box firmware incompatibility")
            appendLine()
            appendLine("═══════════════════════════════════════════════════════════════")
            appendLine("INFORMATION NEEDED FOR DEBUGGING")
            appendLine("═══════════════════════════════════════════════════════════════")
            appendLine()
            appendLine("Please provide the following when reporting this issue:")
            appendLine()
            appendLine("1. FRITZ!Box Information:")
            appendLine("   - Model: (e.g., FRITZ!Box 7590)")
            appendLine("   - Firmware version: (found in FRITZ!Box web UI)")
            appendLine("   - TR-064 enabled: (System > FRITZ!Box Users > Login to Home Network)")
            appendLine()
            appendLine("2. Network Setup:")
            appendLine("   - Connection type: ${diagnostics.networkType}")
            appendLine("   - Are you on the same network as FRITZ!Box?")
            appendLine("   - Any firewalls or VPNs active?")
            appendLine()
            appendLine("3. Python Client Test:")
            appendLine("   - Does the Python script (fritzbox_restart.py) work?")
            appendLine("   - If yes, this confirms the issue is Android-specific")
            appendLine()
            appendLine("4. Detailed Logs:")
            appendLine("   - See APPLICATION LOGS section below")
            appendLine("   - Look for '=== HTTP REQUEST ===' and '=== HTTP RESPONSE ==='")
            appendLine("   - Compare with Python client's output")
            appendLine()
            appendLine("═══════════════════════════════════════════════════════════════")
            appendLine("NEXT STEPS")
            appendLine("═══════════════════════════════════════════════════════════════")
            appendLine()
            appendLine("1. Review the logs below for HTTP request/response details")
            appendLine("2. Compare the SOAP envelope with Python client (if available)")
            appendLine("3. Check FRITZ!Box logs (System > Events in web UI)")
            appendLine("4. Try the Python script to confirm TR-064 is working")
            appendLine("5. Share this complete report when asking for help")
            appendLine()
            appendLine("═══════════════════════════════════════════════════════════════")
            appendLine("APPLICATION LOGS")
            appendLine("═══════════════════════════════════════════════════════════════")
            appendLine()
            if (logs.isNotEmpty() && logs != "No logs available") {
                appendLine(logs)
            } else {
                appendLine("No logs available. This is the first run or logs were cleared.")
            }
            appendLine()
            appendLine("═══════════════════════════════════════════════════════════════")
            appendLine("END OF DIAGNOSTIC REPORT")
            appendLine("═══════════════════════════════════════════════════════════════")
        }
    }
}
