package com.fritzbox.restart

import android.util.Log
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
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
        .build()

    private val baseUrl = "http://$host:49000"

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
            
            Log.d(TAG, "Connecting to FRITZ!Box at $host")
            Log.d(TAG, "Service: $serviceType, Action: $actionName")
            
            // SOAP envelope for reboot command (matching fritzconnection format)
            val soapBody = """<?xml version="1.0" encoding="utf-8"?><s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body><u:$actionName xmlns:u="$serviceType"></u:$actionName></s:Body></s:Envelope>"""

            Log.d(TAG, "SOAP Request URL: $baseUrl$controlUrl")
            Log.d(TAG, "SOAP Action: $soapAction")
            Log.d(TAG, "SOAP Body: $soapBody")

            val request = Request.Builder()
                .url("$baseUrl$controlUrl")
                .post(soapBody.toRequestBody("text/xml; charset=utf-8".toMediaType()))
                .addHeader("soapaction", soapAction)
                .build()

            Log.d(TAG, "Sending request...")
            val response = client.newCall(request).execute()
            
            response.use {
                val responseBody = it.body?.string() ?: ""
                Log.d(TAG, "Response code: ${it.code}")
                Log.d(TAG, "Response message: ${it.message}")
                Log.d(TAG, "Response body: $responseBody")
                
                when {
                    it.isSuccessful -> {
                        Log.i(TAG, "Reboot command sent successfully")
                        Result.success("Restart command sent successfully! FRITZ!Box is rebooting...")
                    }
                    it.code == 401 -> {
                        Log.e(TAG, "Authentication failed (401)")
                        Result.failure(Exception("Authentication failed. Please check your password."))
                    }
                    it.code == 404 -> {
                        Log.e(TAG, "FRITZ!Box not found (404)")
                        Result.failure(Exception("FRITZ!Box not found at $host. Please check the IP address."))
                    }
                    it.code == 500 -> {
                        Log.e(TAG, "Internal server error (500). Response: $responseBody")
                        Result.failure(Exception("Server error. Please check FRITZ!Box settings and try again."))
                    }
                    else -> {
                        Log.e(TAG, "HTTP error ${it.code}: ${it.message}")
                        Result.failure(Exception("HTTP ${it.code}: ${it.message}"))
                    }
                }
            }
        } catch (e: java.net.UnknownHostException) {
            Log.e(TAG, "Unknown host: $host", e)
            Result.failure(Exception("Cannot reach FRITZ!Box at $host. Please check the IP address."))
        } catch (e: java.net.SocketTimeoutException) {
            Log.e(TAG, "Socket timeout", e)
            Result.failure(Exception("Connection timeout. Please check your network connection."))
        } catch (e: java.net.ConnectException) {
            Log.e(TAG, "Connection refused", e)
            Result.failure(Exception("Connection refused. Please check if FRITZ!Box is accessible."))
        } catch (e: Exception) {
            Log.e(TAG, "Unexpected error", e)
            Result.failure(Exception("Error: ${e.message ?: e.javaClass.simpleName}"))
        }
    }
}
