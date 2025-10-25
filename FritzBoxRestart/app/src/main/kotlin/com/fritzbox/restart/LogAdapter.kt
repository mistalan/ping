package com.fritzbox.restart

import android.content.res.ColorStateList
import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.fritzbox.restart.databinding.ItemLogEntryBinding

/**
 * Adapter for displaying log entries in a RecyclerView
 */
class LogAdapter : ListAdapter<LogEntry, LogAdapter.LogViewHolder>(LogDiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): LogViewHolder {
        val binding = ItemLogEntryBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return LogViewHolder(binding)
    }

    override fun onBindViewHolder(holder: LogViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    class LogViewHolder(private val binding: ItemLogEntryBinding) :
        RecyclerView.ViewHolder(binding.root) {

        fun bind(logEntry: LogEntry) {
            binding.timestampText.text = logEntry.timestamp
            binding.tagText.text = logEntry.tag
            binding.messageText.text = logEntry.message
            binding.levelChip.text = logEntry.getLevelString()
            
            // Set chip background color based on log level
            val color = ContextCompat.getColor(binding.root.context, logEntry.getLevelColor())
            binding.levelChip.chipBackgroundColor = ColorStateList.valueOf(color)
        }
    }

    private class LogDiffCallback : DiffUtil.ItemCallback<LogEntry>() {
        override fun areItemsTheSame(oldItem: LogEntry, newItem: LogEntry): Boolean {
            return oldItem.timestamp == newItem.timestamp &&
                   oldItem.tag == newItem.tag
        }

        override fun areContentsTheSame(oldItem: LogEntry, newItem: LogEntry): Boolean {
            return oldItem == newItem
        }
    }
}
