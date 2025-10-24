package com.fritzbox.restart

import android.util.Log
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import okhttp3.Response
import java.util.concurrent.TimeUnit

/**
 * Client for communicating with FRITZ!Box router via TR-064 API
 */
class FritzBoxClient(
    private val host: String,
    private val username: String?,
    private val password: String,
    private val timeout: Int = 10
) {
    companion object {
        private const val TAG = "FritzBoxClient"
    }

    private val client = OkHttpClient.Builder()
        .connectTimeout(timeout.toLong(), TimeUnit.SECONDS)
        .readTimeout(timeout.toLong(), TimeUnit.SECONDS)
        .writeTimeout(timeout.toLong(), TimeUnit.SECONDS)
        .authenticator(DigestAuthenticator(username ?: "", password))
        .addInterceptor { chain ->
            val request = chain.request()
            logDetailedRequest(request)
            val startTime = System.currentTimeMillis()
            val response = chain.proceed(request)
            val duration = System.currentTimeMillis() - startTime
            logDetailedResponse(response, duration)
            response
        }
        .build()

    private val baseUrl = "http://$host:49000"
    
    /**
     * Log detailed HTTP request information
     */
    private fun logDetailedRequest(request: Request) {
        val sb = StringBuilder()
        sb.append("=== HTTP REQUEST ===\n")
        sb.append("URL: ${request.url}\n")
        sb.append("Method: ${request.method}\n")
        sb.append("Headers:\n")
        request.headers.forEach { (name, value) ->
            // Don't log password in Authorization header
            if (name.equals("Authorization", ignoreCase = true)) {
                sb.append("  $name: [REDACTED]\n")
            } else {
                sb.append("  $name: $value\n")
            }
        }
        request.body?.let { body ->
            val buffer = okio.Buffer()
            body.writeTo(buffer)
            sb.append("Body (${body.contentLength()} bytes):\n")
            sb.append(buffer.readUtf8())
            sb.append("\n")
        }
        sb.append("===================")
        LogManager.log(TAG, sb.toString(), Log.DEBUG)
    }
    
    /**
     * Log detailed HTTP response information
     */
    private fun logDetailedResponse(response: Response, durationMs: Long) {
        val sb = StringBuilder()
        sb.append("=== HTTP RESPONSE ===\n")
        sb.append("Code: ${response.code}\n")
        sb.append("Message: ${response.message}\n")
        sb.append("Duration: ${durationMs}ms\n")
        sb.append("Protocol: ${response.protocol}\n")
        sb.append("Headers:\n")
        response.headers.forEach { (name, value) ->
            sb.append("  $name: $value\n")
        }
        // Note: We'll read the body in the main reboot() function to avoid consuming it twice
        sb.append("====================")
        LogManager.log(TAG, sb.toString(), Log.DEBUG)
    }

    /**
     * Send reboot command to FRITZ!Box
     * @return Result with success message or error
     */
    suspend fun reboot(): Result<String> = withContext(Dispatchers.IO) {
        try {
            val serviceType = "urn:dslforum-org:service:DeviceConfig:1"
            val actionName = "Reboot"
            val soapAction = "$serviceType#$actionName"
            val controlUrl = "/upnp/control/deviceconfig"
            
            LogManager.log(TAG, "=== STARTING FRITZ!BOX REBOOT REQUEST ===", Log.INFO)
            LogManager.log(TAG, "Target host: $host", Log.INFO)
            LogManager.log(TAG, "Service: $serviceType", Log.INFO)
            LogManager.log(TAG, "Action: $actionName", Log.INFO)
            LogManager.log(TAG, "Control URL: $controlUrl", Log.INFO)
            
            // SOAP envelope for reboot command (matching fritzconnection format)
            val soapBody = """<?xml version="1.0" encoding="utf-8"?><s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body><u:$actionName xmlns:u="$serviceType"></u:$actionName></s:Body></s:Envelope>"""

            LogManager.log(TAG, "SOAP envelope length: ${soapBody.length} bytes", Log.DEBUG)
            LogManager.log(TAG, "SOAP envelope format check:", Log.DEBUG)
            LogManager.log(TAG, "  - Single line: ${!soapBody.contains('\n')}", Log.DEBUG)
            LogManager.log(TAG, "  - Has XML declaration: ${soapBody.startsWith("<?xml")}", Log.DEBUG)
            LogManager.log(TAG, "  - Has closing tag: ${soapBody.contains("</u:$actionName>")}", Log.DEBUG)

            // FRITZ!Box requires separate Content-Type and charset headers (non-standard HTTP)
            // This matches the format used by the Python fritzconnection library
            val request = Request.Builder()
                .url("$baseUrl$controlUrl")
                .post(soapBody.toRequestBody("text/xml".toMediaType()))
                .addHeader("soapaction", soapAction)
                .addHeader("charset", "utf-8")
                .build()

            LogManager.log(TAG, "Request prepared. Sending to FRITZ!Box...", Log.INFO)
            val response = client.newCall(request).execute()
            
            response.use {
                val responseBody = it.body?.string() ?: ""
                LogManager.log(TAG, "Response body (${responseBody.length} bytes):\n$responseBody", Log.DEBUG)
                
                when {
                    it.isSuccessful -> {
                        LogManager.log(TAG, "SUCCESS: Reboot command sent successfully", Log.INFO)
                        Result.success("Restart command sent successfully! FRITZ!Box is rebooting...")
                    }
                    it.code == 401 -> {
                        LogManager.log(TAG, "ERROR: Authentication failed (401)", Log.ERROR)
                        LogManager.log(TAG, "Check if password is correct and TR-064 is enabled", Log.ERROR)
                        Result.failure(Exception("Authentication failed. Please check your password."))
                    }
                    it.code == 404 -> {
                        LogManager.log(TAG, "ERROR: FRITZ!Box not found (404)", Log.ERROR)
                        Result.failure(Exception("FRITZ!Box not found at $host. Please check the IP address."))
                    }
                    it.code == 500 -> {
                        LogManager.log(TAG, "ERROR: Internal server error (500)", Log.ERROR)
                        LogManager.log(TAG, "HTTP 500 Response body: $responseBody", Log.ERROR)
                        
                        // Parse error details if available
                        val errorDetails = parseSOAPFault(responseBody)
                        LogManager.log(TAG, "SOAP Fault Details: $errorDetails", Log.ERROR)
                        
                        val errorMsg = if (errorDetails.isNotEmpty()) {
                            "Server error: $errorDetails"
                        } else {
                            "Server error. Check logs for details."
                        }
                        Result.failure(Exception(errorMsg))
                    }
                    else -> {
                        LogManager.log(TAG, "ERROR: HTTP ${it.code}: ${it.message}", Log.ERROR)
                        Result.failure(Exception("HTTP ${it.code}: ${it.message}"))
                    }
                }
            }
        } catch (e: java.net.UnknownHostException) {
            LogManager.log(TAG, "ERROR: Unknown host: $host - ${e.message}", Log.ERROR)
            Result.failure(Exception("Cannot reach FRITZ!Box at $host. Please check the IP address."))
        } catch (e: java.net.SocketTimeoutException) {
            LogManager.log(TAG, "ERROR: Socket timeout - ${e.message}", Log.ERROR)
            Result.failure(Exception("Connection timeout. Please check your network connection."))
        } catch (e: java.net.ConnectException) {
            LogManager.log(TAG, "ERROR: Connection refused - ${e.message}", Log.ERROR)
            Result.failure(Exception("Connection refused. Please check if FRITZ!Box is accessible."))
        } catch (e: Exception) {
            LogManager.log(TAG, "ERROR: Unexpected error - ${e.javaClass.simpleName}: ${e.message}", Log.ERROR)
            e.printStackTrace()
            val stackTrace = e.stackTraceToString()
            LogManager.log(TAG, "Stack trace:\n$stackTrace", Log.ERROR)
            Result.failure(Exception("Error: ${e.message ?: e.javaClass.simpleName}"))
        }
    }
    
    /**
     * Parse SOAP fault response to extract error details
     */
    private fun parseSOAPFault(responseBody: String): String {
        if (responseBody.isEmpty()) return ""
        
        return try {
            // Simple regex-based parsing for common SOAP fault elements
            val faultStringRegex = """<faultstring>(.*?)</faultstring>""".toRegex(RegexOption.IGNORE_CASE)
            val faultCodeRegex = """<faultcode>(.*?)</faultcode>""".toRegex(RegexOption.IGNORE_CASE)
            val detailRegex = """<detail>(.*?)</detail>""".toRegex(setOf(RegexOption.DOT_MATCHES_ALL, RegexOption.IGNORE_CASE))
            
            val faultString = faultStringRegex.find(responseBody)?.groupValues?.get(1) ?: ""
            val faultCode = faultCodeRegex.find(responseBody)?.groupValues?.get(1) ?: ""
            val detail = detailRegex.find(responseBody)?.groupValues?.get(1) ?: ""
            
            buildString {
                if (faultCode.isNotEmpty()) append("Code: $faultCode ")
                if (faultString.isNotEmpty()) append("Message: $faultString ")
                if (detail.isNotEmpty()) append("Detail: $detail")
            }.trim()
        } catch (e: Exception) {
            LogManager.log(TAG, "Failed to parse SOAP fault: ${e.message}", Log.WARN)
            ""
        }
    }
}
