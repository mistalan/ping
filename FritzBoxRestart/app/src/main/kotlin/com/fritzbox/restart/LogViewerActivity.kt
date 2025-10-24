package com.fritzbox.restart

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.view.Menu
import android.view.MenuItem
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.FileProvider
import com.fritzbox.restart.databinding.ActivityLogViewerBinding

class LogViewerActivity : AppCompatActivity() {
    private lateinit var binding: ActivityLogViewerBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityLogViewerBinding.inflate(layoutInflater)
        setContentView(binding.root)

        supportActionBar?.setDisplayHomeAsUpEnabled(true)
        supportActionBar?.title = "Application Logs"

        loadLogs()

        binding.refreshButton.setOnClickListener {
            loadLogs()
        }

        binding.clearButton.setOnClickListener {
            showClearConfirmation()
        }

        binding.shareButton.setOnClickListener {
            shareLogs()
        }

        binding.copyButton.setOnClickListener {
            copyLogsToClipboard()
        }
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
            else -> super.onOptionsItemSelected(item)
        }
    }

    private fun loadLogs() {
        val logs = LogManager.getLogs()
        binding.logTextView.text = logs
        
        // Scroll to bottom
        binding.scrollView.post {
            binding.scrollView.fullScroll(android.view.View.FOCUS_DOWN)
        }
        
        Toast.makeText(this, "Logs loaded", Toast.LENGTH_SHORT).show()
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
}
