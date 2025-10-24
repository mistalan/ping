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
        
        // Initialize LogManager
        LogManager.init(this)
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
            val password = binding.passwordInput.text?.toString()?.trim() ?: ""

            if (validateInputs(host, password)) {
                showConfirmationDialog(host, password)
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

    private fun showConfirmationDialog(host: String, password: String) {
        AlertDialog.Builder(this)
            .setTitle(R.string.confirm_restart_title)
            .setMessage(getString(R.string.confirm_restart_message, host))
            .setPositiveButton(R.string.yes) { _, _ ->
                performRestart(host, password)
            }
            .setNegativeButton(R.string.no, null)
            .setIcon(android.R.drawable.ic_dialog_alert)
            .show()
    }

    private fun performRestart(host: String, password: String) {
        LogManager.log("MainActivity", "Starting restart operation for host: $host", android.util.Log.INFO)
        
        lifecycleScope.launch {
            setLoading(true)
            updateStatus(getString(R.string.status_connecting), android.R.color.holo_blue_dark)

            try {
                LogManager.log("MainActivity", "Creating FritzBoxClient", android.util.Log.DEBUG)
                
                // Create FritzBox client
                val client = FritzBoxClient(
                    host = host,
                    username = null, // Username is optional, most setups don't need it
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
                        updateStatus(getString(R.string.status_error, errorMessage), android.R.color.holo_red_dark)
                        Toast.makeText(
                            this@MainActivity,
                            errorMessage,
                            Toast.LENGTH_LONG
                        ).show()
                    }
                )
            } catch (e: Exception) {
                val errorMessage = e.message ?: getString(R.string.error_network)
                LogManager.log("MainActivity", "Exception during restart: $errorMessage", android.util.Log.ERROR)
                updateStatus(getString(R.string.status_error, errorMessage), android.R.color.holo_red_dark)
                Toast.makeText(
                    this@MainActivity,
                    errorMessage,
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
        binding.passwordInput.isEnabled = !isLoading
        binding.progressBar.visibility = if (isLoading) View.VISIBLE else View.GONE
    }

    private fun updateStatus(message: String, colorResId: Int) {
        binding.statusText.text = message
        binding.statusText.setTextColor(getColor(colorResId))
    }
}
