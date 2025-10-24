package com.fritzbox.restart

import okhttp3.Authenticator
import okhttp3.Request
import okhttp3.Response
import okhttp3.Route
import java.security.MessageDigest

/**
 * HTTP Digest Authentication implementation for OkHttp
 * Based on RFC 2617
 */
class DigestAuthenticator(
    private val username: String,
    private val password: String
) : Authenticator {
    
    override fun authenticate(route: Route?, response: Response): Request? {
        // Only attempt digest auth once to avoid infinite loops
        if (responseCount(response) >= 3) {
            return null
        }
        
        val authHeader = response.header("WWW-Authenticate") ?: return null
        
        if (!authHeader.startsWith("Digest ", ignoreCase = true)) {
            return null
        }
        
        val digestParams = parseDigestParams(authHeader)
        val realm = digestParams["realm"] ?: return null
        val nonce = digestParams["nonce"] ?: return null
        val qop = digestParams["qop"]
        val opaque = digestParams["opaque"]
        
        val method = response.request.method
        val uri = response.request.url.encodedPath
        
        // Generate response hash according to RFC 2617
        val ha1 = md5("$username:$realm:$password")
        val ha2 = md5("$method:$uri")
        
        val cnonce = generateCnonce()
        val nc = "00000001" // Request count
        
        val responseHash = if (qop != null) {
            md5("$ha1:$nonce:$nc:$cnonce:$qop:$ha2")
        } else {
            md5("$ha1:$nonce:$ha2")
        }
        
        // Build authorization header
        val authValue = buildString {
            append("Digest username=\"$username\"")
            append(", realm=\"$realm\"")
            append(", nonce=\"$nonce\"")
            append(", uri=\"$uri\"")
            append(", response=\"$responseHash\"")
            if (qop != null) {
                append(", qop=$qop")
                append(", nc=$nc")
                append(", cnonce=\"$cnonce\"")
            }
            if (opaque != null) {
                append(", opaque=\"$opaque\"")
            }
        }
        
        return response.request.newBuilder()
            .header("Authorization", authValue)
            .build()
    }
    
    private fun parseDigestParams(header: String): Map<String, String> {
        val params = mutableMapOf<String, String>()
        val digestPrefix = "Digest "
        val paramsString = if (header.startsWith(digestPrefix, ignoreCase = true)) {
            header.substring(digestPrefix.length)
        } else {
            header
        }
        
        // Parse key="value" pairs
        val regex = """(\w+)="?([^",]+)"?""".toRegex()
        regex.findAll(paramsString).forEach { match ->
            val key = match.groupValues[1]
            val value = match.groupValues[2]
            params[key] = value
        }
        
        return params
    }
    
    private fun md5(input: String): String {
        val md = MessageDigest.getInstance("MD5")
        val digest = md.digest(input.toByteArray())
        return digest.joinToString("") { "%02x".format(it) }
    }
    
    private fun generateCnonce(): String {
        // Generate a random client nonce
        val random = java.util.Random()
        val bytes = ByteArray(16)
        random.nextBytes(bytes)
        return bytes.joinToString("") { "%02x".format(it) }
    }
    
    private fun responseCount(response: Response): Int {
        var count = 1
        var priorResponse = response.priorResponse
        while (priorResponse != null) {
            count++
            priorResponse = priorResponse.priorResponse
        }
        return count
    }
}
