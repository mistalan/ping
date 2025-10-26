package com.fritzbox.restart

import android.content.Intent
import android.os.Bundle
import android.view.Menu
import android.view.MenuItem
import android.view.View
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.google.android.material.textfield.TextInputEditText
import kotlinx.coroutines.launch
import com.fritzbox.restart.databinding.ActivityMainBinding

class MainActivity : AppCompatActivity() {
    private lateinit var binding: ActivityMainBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // LogManager is now initialized in FritzBoxApplication
        LogManager.log("MainActivity", "App started", android.util.Log.INFO)
        
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setupUI()
    }
    
    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        menuInflater.inflate(R.menu.main_menu, menu)
        return true
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        return when (item.itemId) {
            R.id.action_view_logs -> {
                val intent = Intent(this, LogViewerActivity::class.java)
                startActivity(intent)
                true
            }
            else -> super.onOptionsItemSelected(item)
        }
    }

    private fun setupUI() {
        binding.restartButton.setOnClickListener {
            val host = binding.hostInput.text?.toString()?.trim() ?: ""
            val username = binding.usernameInput.text?.toString()?.trim()
            val password = binding.passwordInput.text?.toString()?.trim() ?: ""

            if (validateInputs(host, password)) {
                showConfirmationDialog(host, username, password)
            }
        }
    }

    private fun validateInputs(host: String, password: String): Boolean {
        return when {
            host.isEmpty() -> {
                binding.statusText.text = getString(R.string.error_empty_host)
                binding.statusText.setTextColor(getColor(android.R.color.holo_red_dark))
                false
            }
            password.isEmpty() -> {
                binding.statusText.text = getString(R.string.error_empty_password)
                binding.statusText.setTextColor(getColor(android.R.color.holo_red_dark))
                false
            }
            else -> true
        }
    }

    private fun showConfirmationDialog(host: String, username: String?, password: String) {
        AlertDialog.Builder(this)
            .setTitle(R.string.confirm_restart_title)
            .setMessage(getString(R.string.confirm_restart_message, host))
            .setPositiveButton(R.string.yes) { _, _ ->
                performRestart(host, username, password)
            }
            .setNegativeButton(R.string.no, null)
            .setIcon(android.R.drawable.ic_dialog_alert)
            .show()
    }

    private fun performRestart(host: String, username: String?, password: String) {
        LogManager.log("MainActivity", "Starting restart operation for host: $host", android.util.Log.INFO)
        
        // Collect system information
        val systemInfo = SystemInfoCollector.collectSystemInfo(this)
        LogManager.log("MainActivity", systemInfo.toString(), android.util.Log.INFO)
        
        lifecycleScope.launch {
            setLoading(true)
            updateStatus(getString(R.string.status_connecting), android.R.color.holo_blue_dark)

            try {
                // Run network diagnostics first
                LogManager.log("MainActivity", "Running network diagnostics...", android.util.Log.INFO)
                val diagnostics = NetworkDiagnostics.runDiagnostics(this@MainActivity, host)
                LogManager.log("MainActivity", diagnostics.toString(), android.util.Log.INFO)
                
                // Check for network issues
                if (diagnostics.hasIssues()) {
                    LogManager.log("MainActivity", "Network diagnostics found issues", android.util.Log.WARN)
                    LogManager.log("MainActivity", diagnostics.getSuggestions(), android.util.Log.WARN)
                    
                    // Still continue with the request, but log the warnings
                    updateStatus("Network issues detected. Check logs for details.", android.R.color.holo_orange_dark)
                } else {
                    LogManager.log("MainActivity", "Network diagnostics: All checks passed", android.util.Log.INFO)
                }
                
                LogManager.log("MainActivity", "Creating FritzBoxClient", android.util.Log.DEBUG)
                
                // Create FritzBox client with username if provided
                val client = FritzBoxClient(
                    host = host,
                    username = if (username.isNullOrBlank()) null else username,
                    password = password,
                    timeout = 10
                )

                updateStatus(getString(R.string.status_sending_command), android.R.color.holo_blue_dark)

                // Send reboot command
                val result = client.reboot()

                result.fold(
                    onSuccess = { message ->
                        LogManager.log("MainActivity", "Restart successful: $message", android.util.Log.INFO)
                        updateStatus(getString(R.string.status_success), android.R.color.holo_green_dark)
                        Toast.makeText(
                            this@MainActivity,
                            getString(R.string.status_restarting),
                            Toast.LENGTH_LONG
                        ).show()
                    },
                    onFailure = { exception ->
                        val errorMessage = exception.message ?: getString(R.string.error_connection)
                        LogManager.log("MainActivity", "Restart failed: $errorMessage", android.util.Log.ERROR)
                        
                        // Log additional troubleshooting information
                        LogManager.log("MainActivity", "=== TROUBLESHOOTING INFO ===", android.util.Log.ERROR)
                        LogManager.log("MainActivity", "Network diagnostics: ${if (diagnostics.hasIssues()) "ISSUES FOUND" else "OK"}", android.util.Log.ERROR)
                        if (diagnostics.hasIssues()) {
                            LogManager.log("MainActivity", diagnostics.getSuggestions(), android.util.Log.ERROR)
                        }
                        LogManager.log("MainActivity", "============================", android.util.Log.ERROR)
                        
                        updateStatus(getString(R.string.status_error, errorMessage), android.R.color.holo_red_dark)
                        
                        // Show detailed error with suggestion to check logs
                        val fullMessage = buildString {
                            append(errorMessage)
                            append("\n\nTap ℹ️ in menu to view detailed logs.")
                            if (diagnostics.hasIssues()) {
                                append("\n\nNetwork issues detected - check logs for troubleshooting.")
                            }
                        }
                        
                        Toast.makeText(
                            this@MainActivity,
                            fullMessage,
                            Toast.LENGTH_LONG
                        ).show()
                    }
                )
            } catch (e: Exception) {
                val errorMessage = e.message ?: getString(R.string.error_network)
                LogManager.log("MainActivity", "Exception during restart: $errorMessage", android.util.Log.ERROR)
                val stackTrace = e.stackTraceToString()
                LogManager.log("MainActivity", "Stack trace:\n$stackTrace", android.util.Log.ERROR)
                
                updateStatus(getString(R.string.status_error, errorMessage), android.R.color.holo_red_dark)
                Toast.makeText(
                    this@MainActivity,
                    "$errorMessage\n\nTap ℹ️ to view logs.",
                    Toast.LENGTH_LONG
                ).show()
            } finally {
                setLoading(false)
            }
        }
    }

    private fun setLoading(isLoading: Boolean) {
        binding.restartButton.isEnabled = !isLoading
        binding.hostInput.isEnabled = !isLoading
        binding.usernameInput.isEnabled = !isLoading
        binding.passwordInput.isEnabled = !isLoading
        binding.progressBar.visibility = if (isLoading) View.VISIBLE else View.GONE
    }

    private fun updateStatus(message: String, colorResId: Int) {
        binding.statusText.text = message
        binding.statusText.setTextColor(getColor(colorResId))
    }
}
