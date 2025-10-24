package com.fritzbox.restart

import android.content.Context
import android.content.pm.PackageManager
import android.os.Build
import android.util.Log

/**
 * Collects system information for diagnostic reports
 */
object SystemInfoCollector {
    private const val TAG = "SystemInfoCollector"
    
    /**
     * Collect comprehensive system information
     */
    fun collectSystemInfo(context: Context): SystemInfo {
        LogManager.log(TAG, "Collecting system information", Log.DEBUG)
        
        val versionName = try {
            val packageInfo = context.packageManager.getPackageInfo(context.packageName, 0)
            packageInfo.versionName
        } catch (e: PackageManager.NameNotFoundException) {
            "Unknown"
        }
        
        return SystemInfo(
            appVersion = versionName,
            androidVersion = Build.VERSION.RELEASE,
            androidSdk = Build.VERSION.SDK_INT,
            deviceManufacturer = Build.MANUFACTURER,
            deviceModel = Build.MODEL,
            deviceBrand = Build.BRAND,
            deviceBoard = Build.BOARD,
            deviceHardware = Build.HARDWARE,
            buildTime = Build.TIME,
            abis = Build.SUPPORTED_ABIS.joinToString(", ")
        )
    }
}

/**
 * System information data class
 */
data class SystemInfo(
    val appVersion: String,
    val androidVersion: String,
    val androidSdk: Int,
    val deviceManufacturer: String,
    val deviceModel: String,
    val deviceBrand: String,
    val deviceBoard: String,
    val deviceHardware: String,
    val buildTime: Long,
    val abis: String
) {
    override fun toString(): String {
        return """
            |System Information
            |==================
            |App Version: $appVersion
            |Android Version: $androidVersion (SDK $androidSdk)
            |Device: $deviceManufacturer $deviceModel
            |Brand: $deviceBrand
            |Board: $deviceBoard
            |Hardware: $deviceHardware
            |Build Time: ${java.util.Date(buildTime)}
            |ABIs: $abis
        """.trimMargin()
    }
}
