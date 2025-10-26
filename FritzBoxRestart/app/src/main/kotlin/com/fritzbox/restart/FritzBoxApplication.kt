package com.fritzbox.restart

import android.app.Application
import android.util.Log

/**
 * Custom Application class to initialize app-wide components
 * This ensures LogManager is initialized before any activity starts
 */
class FritzBoxApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        
        // Initialize LogManager at app startup
        // This ensures logs are available regardless of which activity is launched
        LogManager.init(this)
        LogManager.log("FritzBoxApplication", "Application started", Log.INFO)
    }
}
