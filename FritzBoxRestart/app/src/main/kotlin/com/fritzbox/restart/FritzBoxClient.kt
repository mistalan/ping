package com.fritzbox.restart

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.Credentials
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
    private val client = OkHttpClient.Builder()
        .connectTimeout(timeout.toLong(), TimeUnit.SECONDS)
        .readTimeout(timeout.toLong(), TimeUnit.SECONDS)
        .writeTimeout(timeout.toLong(), TimeUnit.SECONDS)
        .build()

    private val baseUrl = "http://$host:49000"

    /**
     * Send reboot command to FRITZ!Box
     * @return Result with success message or error
     */
    suspend fun reboot(): Result<String> = withContext(Dispatchers.IO) {
        try {
            val soapAction = "urn:dslforum-org:service:DeviceConfig:1#Reboot"
            val controlUrl = "/upnp/control/deviceconfig"
            
            // SOAP envelope for reboot command
            val soapBody = """
                <?xml version="1.0" encoding="utf-8"?>
                <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
                    <s:Body>
                        <u:Reboot xmlns:u="urn:dslforum-org:service:DeviceConfig:1" />
                    </s:Body>
                </s:Envelope>
            """.trimIndent()

            val credentials = username?.let { 
                Credentials.basic(it, password) 
            } ?: Credentials.basic("", password)

            val request = Request.Builder()
                .url("$baseUrl$controlUrl")
                .post(soapBody.toRequestBody("text/xml; charset=utf-8".toMediaType()))
                .addHeader("Authorization", credentials)
                .addHeader("SOAPAction", soapAction)
                .addHeader("Content-Type", "text/xml; charset=utf-8")
                .build()

            val response = client.newCall(request).execute()
            
            response.use {
                when {
                    it.isSuccessful -> {
                        Result.success("Restart command sent successfully! FRITZ!Box is rebooting...")
                    }
                    it.code == 401 -> {
                        Result.failure(Exception("Authentication failed. Please check your password."))
                    }
                    it.code == 404 -> {
                        Result.failure(Exception("FRITZ!Box not found at $host. Please check the IP address."))
                    }
                    else -> {
                        Result.failure(Exception("HTTP ${it.code}: ${it.message}"))
                    }
                }
            }
        } catch (e: java.net.UnknownHostException) {
            Result.failure(Exception("Cannot reach FRITZ!Box at $host. Please check the IP address."))
        } catch (e: java.net.SocketTimeoutException) {
            Result.failure(Exception("Connection timeout. Please check your network connection."))
        } catch (e: java.net.ConnectException) {
            Result.failure(Exception("Connection refused. Please check if FRITZ!Box is accessible."))
        } catch (e: Exception) {
            Result.failure(Exception("Error: ${e.message ?: e.javaClass.simpleName}"))
        }
    }
}
