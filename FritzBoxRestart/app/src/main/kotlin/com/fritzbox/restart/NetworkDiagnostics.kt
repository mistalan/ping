package com.fritzbox.restart

import android.content.Context
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.os.Build
import android.util.Log
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.net.InetAddress
import java.net.Socket

/**
 * Network diagnostics utility for troubleshooting connection issues
 */
object NetworkDiagnostics {
    private const val TAG = "NetworkDiagnostics"
    
    /**
     * Run comprehensive network diagnostics
     */
    suspend fun runDiagnostics(context: Context, host: String): DiagnosticReport = withContext(Dispatchers.IO) {
        LogManager.log(TAG, "Starting network diagnostics for host: $host", Log.INFO)
        
        val report = DiagnosticReport(
            timestamp = System.currentTimeMillis(),
            targetHost = host,
            networkConnected = isNetworkConnected(context),
            networkType = getNetworkType(context),
            dnsResolvable = canResolveDns(host),
            hostReachable = canPingHost(host),
            tr064PortOpen = isPortOpen(host, 49000),
            httpPortOpen = isPortOpen(host, 80),
            httpsPortOpen = isPortOpen(host, 443)
        )
        
        LogManager.log(TAG, "Network diagnostics completed: $report", Log.INFO)
        return@withContext report
    }
    
    /**
     * Check if network is connected
     */
    private fun isNetworkConnected(context: Context): Boolean {
        return try {
            val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                val network = connectivityManager.activeNetwork ?: return false
                val capabilities = connectivityManager.getNetworkCapabilities(network) ?: return false
                capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
            } else {
                @Suppress("DEPRECATION")
                val networkInfo = connectivityManager.activeNetworkInfo
                @Suppress("DEPRECATION")
                networkInfo?.isConnected == true
            }
        } catch (e: Exception) {
            LogManager.log(TAG, "Error checking network connection: ${e.message}", Log.ERROR)
            false
        }
    }
    
    /**
     * Get network type (WiFi, Cellular, etc.)
     */
    private fun getNetworkType(context: Context): String {
        return try {
            val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                val network = connectivityManager.activeNetwork ?: return "None"
                val capabilities = connectivityManager.getNetworkCapabilities(network) ?: return "Unknown"
                when {
                    capabilities.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) -> "WiFi"
                    capabilities.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR) -> "Cellular"
                    capabilities.hasTransport(NetworkCapabilities.TRANSPORT_ETHERNET) -> "Ethernet"
                    else -> "Other"
                }
            } else {
                @Suppress("DEPRECATION")
                val networkInfo = connectivityManager.activeNetworkInfo
                @Suppress("DEPRECATION")
                networkInfo?.typeName ?: "Unknown"
            }
        } catch (e: Exception) {
            LogManager.log(TAG, "Error getting network type: ${e.message}", Log.ERROR)
            "Error"
        }
    }
    
    /**
     * Check if DNS can resolve the host
     */
    private fun canResolveDns(host: String): Boolean {
        return try {
            val address = InetAddress.getByName(host)
            LogManager.log(TAG, "DNS resolved $host to ${address.hostAddress}", Log.DEBUG)
            true
        } catch (e: Exception) {
            LogManager.log(TAG, "DNS resolution failed for $host: ${e.message}", Log.WARN)
            false
        }
    }
    
    /**
     * Check if host is reachable (ping)
     */
    private fun canPingHost(host: String, timeoutMs: Int = 2000): Boolean {
        return try {
            val address = InetAddress.getByName(host)
            val reachable = address.isReachable(timeoutMs)
            LogManager.log(TAG, "Host $host reachable: $reachable", Log.DEBUG)
            reachable
        } catch (e: Exception) {
            LogManager.log(TAG, "Ping failed for $host: ${e.message}", Log.WARN)
            false
        }
    }
    
    /**
     * Check if a specific port is open on the host
     */
    private fun isPortOpen(host: String, port: Int, timeoutMs: Int = 2000): Boolean {
        return try {
            Socket().use { socket ->
                socket.connect(java.net.InetSocketAddress(host, port), timeoutMs)
                LogManager.log(TAG, "Port $port is open on $host", Log.DEBUG)
                true
            }
        } catch (e: Exception) {
            LogManager.log(TAG, "Port $port is closed on $host: ${e.message}", Log.DEBUG)
            false
        }
    }
}

/**
 * Network diagnostic report
 */
data class DiagnosticReport(
    val timestamp: Long,
    val targetHost: String,
    val networkConnected: Boolean,
    val networkType: String,
    val dnsResolvable: Boolean,
    val hostReachable: Boolean,
    val tr064PortOpen: Boolean,
    val httpPortOpen: Boolean,
    val httpsPortOpen: Boolean
) {
    override fun toString(): String {
        return """
            |Network Diagnostics Report
            |========================
            |Target Host: $targetHost
            |Network Connected: $networkConnected
            |Network Type: $networkType
            |DNS Resolvable: $dnsResolvable
            |Host Reachable (ping): $hostReachable
            |TR-064 Port (49000): ${if (tr064PortOpen) "OPEN" else "CLOSED"}
            |HTTP Port (80): ${if (httpPortOpen) "OPEN" else "CLOSED"}
            |HTTPS Port (443): ${if (httpsPortOpen) "OPEN" else "CLOSED"}
        """.trimMargin()
    }
    
    fun hasIssues(): Boolean {
        return !networkConnected || !dnsResolvable || !hostReachable || !tr064PortOpen
    }
    
    fun getSuggestions(): String {
        val suggestions = mutableListOf<String>()
        
        if (!networkConnected) {
            suggestions.add("• No network connection detected. Please check WiFi/data connection.")
        }
        if (!dnsResolvable) {
            suggestions.add("• Cannot resolve host '$targetHost'. Check IP address or hostname.")
        }
        if (!hostReachable) {
            suggestions.add("• Host is not reachable. Ensure FRITZ!Box is on and connected to same network.")
        }
        if (!tr064PortOpen) {
            suggestions.add("• TR-064 port (49000) is not accessible. Check FRITZ!Box TR-064 settings.")
        }
        
        return if (suggestions.isNotEmpty()) {
            "Troubleshooting Suggestions:\n" + suggestions.joinToString("\n")
        } else {
            "Network appears healthy. Issue may be with authentication or SOAP format."
        }
    }
}
