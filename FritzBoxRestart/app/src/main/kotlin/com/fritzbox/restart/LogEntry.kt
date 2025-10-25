package com.fritzbox.restart

import android.util.Log

/**
 * Represents a single log entry
 */
data class LogEntry(
    val timestamp: String,
    val level: Int,
    val tag: String,
    val message: String
) {
    /**
     * Get the log level as a string
     */
    fun getLevelString(): String {
        return when (level) {
            Log.DEBUG -> "DEBUG"
            Log.INFO -> "INFO"
            Log.WARN -> "WARN"
            Log.ERROR -> "ERROR"
            else -> "VERBOSE"
        }
    }
    
    /**
     * Get the color resource for this log level
     */
    fun getLevelColor(): Int {
        return when (level) {
            Log.DEBUG -> R.color.log_debug
            Log.INFO -> R.color.log_info
            Log.WARN -> R.color.log_warning
            Log.ERROR -> R.color.log_error
            else -> R.color.log_debug
        }
    }
}
