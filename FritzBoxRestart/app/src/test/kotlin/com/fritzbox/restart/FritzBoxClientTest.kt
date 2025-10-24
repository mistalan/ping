package com.fritzbox.restart

import kotlinx.coroutines.test.runTest
import okhttp3.mockwebserver.MockResponse
import okhttp3.mockwebserver.MockWebServer
import okhttp3.mockwebserver.RecordedRequest
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

/**
 * Unit tests for FritzBoxClient
 * 
 * These tests verify that the FritzBoxClient correctly:
 * - Sends the required Content-Type header
 * - Sends the correct SOAP envelope
 * - Handles successful responses
 * - Handles error responses (401, 404, 500)
 * - Handles network errors
 */
@RunWith(RobolectricTestRunner::class)
@Config(manifest = Config.NONE, sdk = [28])
class FritzBoxClientTest {

    private lateinit var mockWebServer: MockWebServer
    private lateinit var client: FritzBoxClient

    @Before
    fun setUp() {
        mockWebServer = MockWebServer()
        mockWebServer.start()
        
        // Create client pointing to mock server
        val host = mockWebServer.hostName
        val port = mockWebServer.port
        
        // We need to create a custom client that uses the mock server's port
        // Since FritzBoxClient hardcodes port 49000, we'll test with a modified host
        client = FritzBoxClient(
            host = "$host:$port",
            username = "testuser",
            password = "testpass",
            timeout = 5
        )
    }

    @After
    fun tearDown() {
        mockWebServer.shutdown()
    }

    @Test
    fun `reboot sends content-type header`() = runTest {
        // Arrange
        mockWebServer.enqueue(MockResponse().setResponseCode(200))

        // Act
        client.reboot()

        // Assert
        val request = mockWebServer.takeRequest()
        // Check for lowercase content-type header (matches Python fritzconnection)
        val contentType = request.getHeader("content-type")
        assertNotNull("content-type header should be present", contentType)
        assertEquals(
            "content-type should be text/xml (separate from charset)",
            "text/xml",
            contentType
        )
    }

    @Test
    fun `reboot sends soapaction header`() = runTest {
        // Arrange
        mockWebServer.enqueue(MockResponse().setResponseCode(200))

        // Act
        client.reboot()

        // Assert
        val request = mockWebServer.takeRequest()
        assertEquals(
            "urn:dslforum-org:service:DeviceConfig:1#Reboot",
            request.getHeader("soapaction")
        )
    }

    @Test
    fun `reboot sends charset header`() = runTest {
        // Arrange
        mockWebServer.enqueue(MockResponse().setResponseCode(200))

        // Act
        client.reboot()

        // Assert
        val request = mockWebServer.takeRequest()
        assertEquals("utf-8", request.getHeader("charset"))
    }

    @Test
    fun `reboot sends correct SOAP envelope`() = runTest {
        // Arrange
        mockWebServer.enqueue(MockResponse().setResponseCode(200))

        // Act
        client.reboot()

        // Assert
        val request = mockWebServer.takeRequest()
        val body = request.body.readUtf8()
        
        // Verify SOAP envelope structure
        assertTrue("Body should contain XML declaration", body.startsWith("<?xml version=\"1.0\" encoding=\"utf-8\"?>"))
        assertTrue("Body should contain SOAP envelope", body.contains("<s:Envelope"))
        assertTrue("Body should contain Reboot action", body.contains("<u:Reboot"))
        assertTrue("Body should contain service type", body.contains("urn:dslforum-org:service:DeviceConfig:1"))
        assertTrue("Body should be single line", !body.contains("\n"))
    }

    @Test
    fun `reboot sends POST request to correct URL`() = runTest {
        // Arrange
        mockWebServer.enqueue(MockResponse().setResponseCode(200))

        // Act
        client.reboot()

        // Assert
        val request = mockWebServer.takeRequest()
        assertEquals("POST", request.method)
        assertTrue("URL should contain control URL", request.path?.contains("/upnp/control/deviceconfig") ?: false)
    }

    @Test
    fun `reboot returns success on HTTP 200`() = runTest {
        // Arrange
        mockWebServer.enqueue(MockResponse().setResponseCode(200))

        // Act
        val result = client.reboot()

        // Assert
        assertTrue("Result should be success", result.isSuccess)
        assertTrue(
            "Success message should mention restart",
            result.getOrNull()?.contains("Restart") ?: false
        )
    }

    @Test
    fun `reboot returns failure on HTTP 401`() = runTest {
        // Arrange
        mockWebServer.enqueue(MockResponse().setResponseCode(401))

        // Act
        val result = client.reboot()

        // Assert
        assertTrue("Result should be failure", result.isFailure)
        val exception = result.exceptionOrNull()
        assertNotNull("Exception should be present", exception)
        assertTrue(
            "Error message should mention authentication",
            exception?.message?.contains("Authentication") ?: false
        )
    }

    @Test
    fun `reboot returns failure on HTTP 404`() = runTest {
        // Arrange
        mockWebServer.enqueue(MockResponse().setResponseCode(404))

        // Act
        val result = client.reboot()

        // Assert
        assertTrue("Result should be failure", result.isFailure)
        val exception = result.exceptionOrNull()
        assertNotNull("Exception should be present", exception)
        assertTrue(
            "Error message should mention not found",
            exception?.message?.contains("not found") ?: false
        )
    }

    @Test
    fun `reboot returns failure on HTTP 500 with SOAP fault`() = runTest {
        // Arrange
        val soapFault = """<?xml version="1.0"?>
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
<s:Body>
<s:Fault>
<faultcode>s:Client</faultcode>
<faultstring>UPnPError</faultstring>
<detail>
<UPnPError xmlns="urn:dslforum-org:control-1-0">
<errorCode>606</errorCode>
<errorDescription>Action Not Authorized</errorDescription>
</UPnPError>
</detail>
</s:Fault>
</s:Body>
</s:Envelope>"""
        
        mockWebServer.enqueue(
            MockResponse()
                .setResponseCode(500)
                .setBody(soapFault)
                .setHeader("Content-Type", "text/xml; charset=\"utf-8\"")
        )

        // Act
        val result = client.reboot()

        // Assert
        assertTrue("Result should be failure", result.isFailure)
        val exception = result.exceptionOrNull()
        assertNotNull("Exception should be present", exception)
        
        val errorMessage = exception?.message ?: ""
        assertTrue(
            "Error message should contain SOAP fault details",
            errorMessage.contains("s:Client") || errorMessage.contains("UPnPError")
        )
    }

    @Test
    fun `reboot handles connection timeout gracefully`() = runTest {
        // Arrange
        // Don't enqueue any response - this will cause a timeout
        mockWebServer.shutdown() // Shutdown server to force connection error

        // Act
        val result = client.reboot()

        // Assert
        assertTrue("Result should be failure", result.isFailure)
        assertNotNull("Exception should be present", result.exceptionOrNull())
    }

    @Test
    fun `reboot includes all required headers in single request`() = runTest {
        // Arrange
        mockWebServer.enqueue(MockResponse().setResponseCode(200))

        // Act
        client.reboot()

        // Assert - This is the critical test for the bug fix
        val request = mockWebServer.takeRequest()
        
        // Verify all three headers are present (matching Python fritzconnection format)
        // Python uses: content-type: text/xml, charset: utf-8, soapaction: ...
        val contentType = request.getHeader("content-type")
        val charset = request.getHeader("charset")
        val soapaction = request.getHeader("soapaction")
        
        assertNotNull("content-type header must be present", contentType)
        assertNotNull("soapaction header must be present", soapaction)
        assertNotNull("charset header must be present", charset)
        
        // Verify exact values match Python fritzconnection format
        assertEquals("text/xml", contentType)
        assertEquals("urn:dslforum-org:service:DeviceConfig:1#Reboot", soapaction)
        assertEquals("utf-8", charset)
    }

    @Test
    fun `SOAP envelope matches Python fritzconnection format`() = runTest {
        // Arrange
        mockWebServer.enqueue(MockResponse().setResponseCode(200))

        // Act
        client.reboot()

        // Assert
        val request = mockWebServer.takeRequest()
        val body = request.body.readUtf8()
        
        // The exact format that works with Python fritzconnection
        val expectedPattern = """<?xml version="1.0" encoding="utf-8"?><s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body><u:Reboot xmlns:u="urn:dslforum-org:service:DeviceConfig:1"></u:Reboot></s:Body></s:Envelope>"""
        
        assertEquals("SOAP envelope should match Python format exactly", expectedPattern, body)
    }

    @Test
    fun `parseSOAPFault extracts error details correctly`() = runTest {
        // Arrange
        val soapFault = """<?xml version="1.0"?>
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
<s:Body>
<s:Fault>
<faultcode>s:Client</faultcode>
<faultstring>TestError</faultstring>
<detail>Test Detail</detail>
</s:Fault>
</s:Body>
</s:Envelope>"""
        
        mockWebServer.enqueue(
            MockResponse()
                .setResponseCode(500)
                .setBody(soapFault)
                .setHeader("Content-Type", "text/xml")
        )

        // Act
        val result = client.reboot()

        // Assert
        assertTrue("Result should be failure", result.isFailure)
        val errorMessage = result.exceptionOrNull()?.message ?: ""
        
        // Verify parsing extracted the fault details
        assertTrue("Should contain fault code", errorMessage.contains("s:Client"))
        assertTrue("Should contain fault string", errorMessage.contains("TestError"))
        assertTrue("Should contain detail", errorMessage.contains("Test Detail"))
    }
}
