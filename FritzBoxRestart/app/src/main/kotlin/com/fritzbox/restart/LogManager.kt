package com.fritzbox.restart

import android.content.Context
import android.util.Log
import java.io.File
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

/**
 * Manages application logs for debugging purposes
 */
object LogManager {
    private const val TAG = "LogManager"
    private const val LOG_FILE_NAME = "fritzbox_restart.log"
    private const val MAX_LOG_SIZE = 500 * 1024 // 500 KB
    
    private var logFile: File? = null
    
    /**
     * Initialize the log manager with application context
     * Note: We store the application context, not activity context, to avoid leaks
     */
    fun init(context: Context) {
        // Use application context to avoid memory leaks
        val appContext = context.applicationContext
        logFile = File(appContext.getExternalFilesDir(null), LOG_FILE_NAME)
        
        // Rotate log if it's too large
        logFile?.let { file ->
            if (file.exists() && file.length() > MAX_LOG_SIZE) {
                file.delete()
                log("LogManager", "Log file rotated due to size limit")
            }
        }
        
        log("LogManager", "Log manager initialized")
    }
    
    /**
     * Log a message to both Logcat and file
     */
    fun log(tag: String, message: String, level: Int = Log.DEBUG) {
        // Log to Logcat
        when (level) {
            Log.DEBUG -> Log.d(tag, message)
            Log.INFO -> Log.i(tag, message)
            Log.WARN -> Log.w(tag, message)
            Log.ERROR -> Log.e(tag, message)
            else -> Log.v(tag, message)
        }
        
        // Log to file
        try {
            logFile?.let { file ->
                val timestamp = SimpleDateFormat("yyyy-MM-dd HH:mm:ss.SSS", Locale.getDefault())
                    .format(Date())
                val levelStr = when (level) {
                    Log.DEBUG -> "D"
                    Log.INFO -> "I"
                    Log.WARN -> "W"
                    Log.ERROR -> "E"
                    else -> "V"
                }
                val logEntry = "$timestamp [$levelStr/$tag] $message\n"
                file.appendText(logEntry)
            }
        } catch (e: Exception) {
            Log.e(TAG, "Failed to write to log file", e)
        }
    }
    
    /**
     * Get all logs as a string
     */
    fun getLogs(): String {
        return try {
            logFile?.let { file ->
                if (file.exists()) {
                    file.readText()
                } else {
                    "No logs available"
                }
            } ?: "Log manager not initialized"
        } catch (e: Exception) {
            Log.e(TAG, "Failed to read log file", e)
            "Error reading logs: ${e.message}"
        }
    }
    
    /**
     * Clear all logs
     */
    fun clearLogs() {
        try {
            logFile?.let { file ->
                if (file.exists()) {
                    file.delete()
                }
            }
            log("LogManager", "Logs cleared")
        } catch (e: Exception) {
            Log.e(TAG, "Failed to clear logs", e)
        }
    }
    
    /**
     * Get the log file for sharing
     */
    fun getLogFile(): File? = logFile
}
