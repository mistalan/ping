package com.fritzbox.restart

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.view.Menu
import android.view.MenuItem
import android.view.View
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.FileProvider
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import com.fritzbox.restart.databinding.ActivityLogViewerBinding
import com.google.android.material.bottomsheet.BottomSheetDialog
import com.google.android.material.chip.Chip
import kotlinx.coroutines.launch
import java.io.File
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

class LogViewerActivity : AppCompatActivity() {
    private lateinit var binding: ActivityLogViewerBinding
    private lateinit var logAdapter: LogAdapter
    private var allLogs: List<LogEntry> = emptyList()
    private var lastHost: String = "192.168.178.1" // Default host
    private val selectedFilters = mutableSetOf<Int>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityLogViewerBinding.inflate(layoutInflater)
        setContentView(binding.root)

        supportActionBar?.setDisplayHomeAsUpEnabled(true)
        supportActionBar?.title = "Application Logs"

        setupRecyclerView()
        setupFilters()
        setupFab()
        
        loadLogs()
    }

    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        menuInflater.inflate(R.menu.log_viewer_menu, menu)
        return true
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        return when (item.itemId) {
            android.R.id.home -> {
                finish()
                true
            }
            R.id.action_refresh -> {
                loadLogs()
                true
            }
            R.id.action_share -> {
                shareLogs()
                true
            }
            R.id.action_clear -> {
                showClearConfirmation()
                true
            }
            R.id.action_diagnostic -> {
                generateDiagnosticReport()
                true
            }
            else -> super.onOptionsItemSelected(item)
        }
    }

    private fun setupRecyclerView() {
        logAdapter = LogAdapter()
        binding.logsRecyclerView.apply {
            layoutManager = LinearLayoutManager(this@LogViewerActivity)
            adapter = logAdapter
        }
    }

    private fun setupFilters() {
        // Set up filter chips
        binding.filterAll.setOnCheckedChangeListener { _, isChecked ->
            if (isChecked) {
                // Uncheck all other filters
                binding.filterDebug.isChecked = false
                binding.filterInfo.isChecked = false
                binding.filterWarning.isChecked = false
                binding.filterError.isChecked = false
                selectedFilters.clear()
                applyFilters()
            }
        }

        binding.filterDebug.setOnCheckedChangeListener { _, isChecked ->
            handleFilterChange(Log.DEBUG, isChecked)
        }

        binding.filterInfo.setOnCheckedChangeListener { _, isChecked ->
            handleFilterChange(Log.INFO, isChecked)
        }

        binding.filterWarning.setOnCheckedChangeListener { _, isChecked ->
            handleFilterChange(Log.WARN, isChecked)
        }

        binding.filterError.setOnCheckedChangeListener { _, isChecked ->
            handleFilterChange(Log.ERROR, isChecked)
        }
    }

    private fun handleFilterChange(level: Int, isChecked: Boolean) {
        // Uncheck "All" when any specific filter is selected
        binding.filterAll.isChecked = false
        
        if (isChecked) {
            selectedFilters.add(level)
        } else {
            selectedFilters.remove(level)
        }
        
        // If no filters are selected, check "All"
        if (selectedFilters.isEmpty()) {
            binding.filterAll.isChecked = true
        } else {
            applyFilters()
        }
    }

    private fun applyFilters() {
        val filteredLogs = if (selectedFilters.isEmpty()) {
            allLogs
        } else {
            allLogs.filter { it.level in selectedFilters }
        }
        
        logAdapter.submitList(filteredLogs)
        updateEmptyState(filteredLogs.isEmpty())
    }

    private fun setupFab() {
        binding.fab.setOnClickListener {
            showActionsBottomSheet()
        }
    }

    private fun showActionsBottomSheet() {
        val bottomSheetDialog = BottomSheetDialog(this)
        val view = layoutInflater.inflate(R.layout.bottom_sheet_actions, null)
        
        view.findViewById<View>(R.id.actionRefresh).setOnClickListener {
            bottomSheetDialog.dismiss()
            loadLogs()
        }
        
        view.findViewById<View>(R.id.actionCopy).setOnClickListener {
            bottomSheetDialog.dismiss()
            copyLogsToClipboard()
        }
        
        view.findViewById<View>(R.id.actionShare).setOnClickListener {
            bottomSheetDialog.dismiss()
            shareLogs()
        }
        
        view.findViewById<View>(R.id.actionClear).setOnClickListener {
            bottomSheetDialog.dismiss()
            showClearConfirmation()
        }
        
        view.findViewById<View>(R.id.actionDiagnostic).setOnClickListener {
            bottomSheetDialog.dismiss()
            generateDiagnosticReport()
        }
        
        bottomSheetDialog.setContentView(view)
        bottomSheetDialog.show()
    }

    private fun loadLogs() {
        binding.progressBar.visibility = View.VISIBLE
        
        val logText = LogManager.getLogs()
        allLogs = parseLogText(logText)
        
        applyFilters()
        
        binding.progressBar.visibility = View.GONE
        
        // Scroll to bottom
        binding.logsRecyclerView.post {
            if (logAdapter.itemCount > 0) {
                binding.logsRecyclerView.smoothScrollToPosition(logAdapter.itemCount - 1)
            }
        }
        
        Toast.makeText(this, "Logs loaded", Toast.LENGTH_SHORT).show()
    }

    private fun parseLogText(logText: String): List<LogEntry> {
        if (logText == "No logs available" || logText == "Log manager not initialized") {
            return emptyList()
        }

        val entries = mutableListOf<LogEntry>()
        val lines = logText.split("\n")
        
        for (line in lines) {
            if (line.isBlank()) continue
            
            // Parse log format: "2025-10-25 16:33:17.123 [D/TAG] message"
            val regex = """^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}) \[([DIWEV])/([^\]]+)\] (.+)$""".toRegex()
            val match = regex.find(line)
            
            if (match != null) {
                val (timestamp, levelChar, tag, message) = match.destructured
                val level = when (levelChar) {
                    "D" -> Log.DEBUG
                    "I" -> Log.INFO
                    "W" -> Log.WARN
                    "E" -> Log.ERROR
                    else -> Log.VERBOSE
                }
                
                entries.add(LogEntry(timestamp, level, tag, message))
            }
        }
        
        return entries
    }

    private fun updateEmptyState(isEmpty: Boolean) {
        binding.emptyStateLayout.visibility = if (isEmpty) View.VISIBLE else View.GONE
        binding.logsRecyclerView.visibility = if (isEmpty) View.GONE else View.VISIBLE
    }

    private fun showClearConfirmation() {
        AlertDialog.Builder(this)
            .setTitle("Clear Logs?")
            .setMessage("Are you sure you want to clear all logs? This action cannot be undone.")
            .setPositiveButton("Clear") { _, _ ->
                LogManager.clearLogs()
                loadLogs()
                Toast.makeText(this, "Logs cleared", Toast.LENGTH_SHORT).show()
            }
            .setNegativeButton("Cancel", null)
            .show()
    }

    private fun shareLogs() {
        val logFile = LogManager.getLogFile()
        if (logFile == null || !logFile.exists()) {
            Toast.makeText(this, "No logs available to share", Toast.LENGTH_SHORT).show()
            return
        }

        try {
            val uri = FileProvider.getUriForFile(
                this,
                "${applicationContext.packageName}.fileprovider",
                logFile
            )

            val shareIntent = Intent(Intent.ACTION_SEND).apply {
                type = "text/plain"
                putExtra(Intent.EXTRA_STREAM, uri)
                putExtra(Intent.EXTRA_SUBJECT, "FRITZ!Box Restart App Logs")
                putExtra(Intent.EXTRA_TEXT, "Debug logs from FRITZ!Box Restart app")
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            }

            startActivity(Intent.createChooser(shareIntent, "Share logs via"))
        } catch (e: Exception) {
            Toast.makeText(this, "Error sharing logs: ${e.message}", Toast.LENGTH_LONG).show()
        }
    }

    private fun copyLogsToClipboard() {
        val logs = LogManager.getLogs()
        val clipboard = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
        val clip = ClipData.newPlainText("FRITZ!Box Restart Logs", logs)
        clipboard.setPrimaryClip(clip)
        Toast.makeText(this, "Logs copied to clipboard", Toast.LENGTH_SHORT).show()
    }
    
    private fun generateDiagnosticReport() {
        // Show dialog to enter host
        val input = android.widget.EditText(this)
        input.setText(lastHost)
        input.hint = "FRITZ!Box IP address"
        
        AlertDialog.Builder(this)
            .setTitle("Generate Diagnostic Report")
            .setMessage("Enter your FRITZ!Box IP address to run network diagnostics:")
            .setView(input)
            .setPositiveButton("Generate") { _, _ ->
                val host = input.text.toString().trim()
                if (host.isNotEmpty()) {
                    lastHost = host
                    generateReportForHost(host)
                } else {
                    Toast.makeText(this, "Please enter a valid host", Toast.LENGTH_SHORT).show()
                }
            }
            .setNegativeButton("Cancel", null)
            .show()
    }
    
    private fun generateReportForHost(host: String) {
        binding.progressBar.visibility = View.VISIBLE
        Toast.makeText(this, "Generating diagnostic report...", Toast.LENGTH_SHORT).show()
        
        lifecycleScope.launch {
            try {
                val report = DiagnosticReportGenerator.generateReport(this@LogViewerActivity, host)
                
                // Save report to file
                val reportFile = File(getExternalFilesDir(null), "diagnostic_report.txt")
                reportFile.writeText(report)
                
                binding.progressBar.visibility = View.GONE
                
                // Show options dialog
                AlertDialog.Builder(this@LogViewerActivity)
                    .setTitle("Diagnostic Report Generated")
                    .setMessage("The diagnostic report has been generated. What would you like to do?")
                    .setPositiveButton("View") { _, _ ->
                        viewDiagnosticReport(report)
                    }
                    .setNeutralButton("Share") { _, _ ->
                        shareReport(reportFile)
                    }
                    .setNegativeButton("Close", null)
                    .show()
                    
            } catch (e: Exception) {
                binding.progressBar.visibility = View.GONE
                Toast.makeText(
                    this@LogViewerActivity, 
                    "Error generating report: ${e.message}", 
                    Toast.LENGTH_LONG
                ).show()
            }
        }
    }
    
    private fun viewDiagnosticReport(report: String) {
        // Parse the diagnostic report and display it in the log viewer
        val timestamp = SimpleDateFormat("yyyy-MM-dd HH:mm:ss.SSS", Locale.getDefault())
            .format(Date())
        val entries = mutableListOf<LogEntry>()
        
        // Add report as a single info entry
        entries.add(LogEntry(timestamp, Log.INFO, "DiagnosticReport", report))
        
        allLogs = entries
        applyFilters()
        
        binding.logsRecyclerView.post {
            binding.logsRecyclerView.smoothScrollToPosition(0)
        }
    }
    
    private fun shareReport(reportFile: File) {
        try {
            val uri = FileProvider.getUriForFile(
                this,
                "${applicationContext.packageName}.fileprovider",
                reportFile
            )

            val shareIntent = Intent(Intent.ACTION_SEND).apply {
                type = "text/plain"
                putExtra(Intent.EXTRA_STREAM, uri)
                putExtra(Intent.EXTRA_SUBJECT, "FRITZ!Box Restart - Diagnostic Report")
                putExtra(
                    Intent.EXTRA_TEXT, 
                    "Diagnostic report for FRITZ!Box restart issue. " +
                    "This report contains system info, network diagnostics, and application logs."
                )
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            }

            startActivity(Intent.createChooser(shareIntent, "Share diagnostic report via"))
        } catch (e: Exception) {
            Toast.makeText(this, "Error sharing report: ${e.message}", Toast.LENGTH_LONG).show()
        }
    }
}
