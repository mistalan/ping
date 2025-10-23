#!/usr/bin/env python3
"""
Unit tests for fritzbox_restart.py

Run with: pytest test_fritzbox_restart.py -v
or: python3 -m pytest test_fritzbox_restart.py -v
"""

import pytest
import sys
from unittest.mock import Mock, patch, call
from datetime import datetime
import fritzbox_restart


class TestNowFunction:
    """Test the now() timestamp function"""
    
    def test_now_returns_formatted_timestamp(self):
        """Verify now() returns a properly formatted timestamp"""
        result = fritzbox_restart.now()
        # Should be in format: YYYY-MM-DD HH:MM:SS
        assert len(result) == 19
        assert result[4] == '-'
        assert result[7] == '-'
        assert result[10] == ' '
        assert result[13] == ':'
        assert result[16] == ':'
        
    def test_now_timestamp_is_parseable(self):
        """Verify now() returns a timestamp that can be parsed back"""
        result = fritzbox_restart.now()
        # Should not raise an exception
        parsed = datetime.strptime(result, "%Y-%m-%d %H:%M:%S")
        assert isinstance(parsed, datetime)


class TestRebootFritzbox:
    """Test the reboot_fritzbox() function"""
    
    @patch('fritzbox_restart.FritzConnection')
    @patch('builtins.print')
    def test_reboot_success(self, mock_print, mock_fc_class):
        """Verify reboot_fritzbox successfully sends reboot command"""
        mock_fc = Mock()
        mock_fc_class.return_value = mock_fc
        
        success, message = fritzbox_restart.reboot_fritzbox(
            "192.168.178.1", "testuser", "testpass", timeout=10
        )
        
        # Verify FritzConnection was created with correct params
        mock_fc_class.assert_called_once_with(
            address="192.168.178.1",
            user="testuser",
            password="testpass",
            timeout=10,
            use_cache=False
        )
        
        # Verify reboot action was called
        mock_fc.call_action.assert_called_once_with("DeviceConfig:1", "Reboot")
        
        # Verify success return
        assert success is True
        assert "erfolgreich" in message or "OK" in message
    
    @patch('fritzbox_restart.FritzConnection')
    @patch('builtins.print')
    def test_reboot_with_none_user(self, mock_print, mock_fc_class):
        """Verify reboot_fritzbox works with None user"""
        mock_fc = Mock()
        mock_fc_class.return_value = mock_fc
        
        success, message = fritzbox_restart.reboot_fritzbox(
            "192.168.178.1", None, "testpass"
        )
        
        # Verify user=None was passed
        call_kwargs = mock_fc_class.call_args[1]
        assert call_kwargs['user'] is None
        assert success is True
    
    @patch('fritzbox_restart.FritzConnection')
    @patch('builtins.print')
    def test_reboot_connection_failure(self, mock_print, mock_fc_class):
        """Verify reboot_fritzbox handles connection failures"""
        mock_fc_class.side_effect = Exception("Connection refused")
        
        success, message = fritzbox_restart.reboot_fritzbox(
            "192.168.178.1", None, "wrongpass"
        )
        
        assert success is False
        assert "Fehler" in message
        assert "Connection refused" in message
    
    @patch('fritzbox_restart.FritzConnection')
    @patch('builtins.print')
    def test_reboot_action_failure(self, mock_print, mock_fc_class):
        """Verify reboot_fritzbox handles reboot action failures"""
        mock_fc = Mock()
        mock_fc.call_action.side_effect = Exception("Action not supported")
        mock_fc_class.return_value = mock_fc
        
        success, message = fritzbox_restart.reboot_fritzbox(
            "192.168.178.1", None, "testpass"
        )
        
        assert success is False
        assert "Fehler" in message
        assert "Action not supported" in message
    
    @patch('fritzbox_restart.FritzConnection')
    @patch('builtins.print')
    def test_reboot_custom_timeout(self, mock_print, mock_fc_class):
        """Verify reboot_fritzbox uses custom timeout"""
        mock_fc = Mock()
        mock_fc_class.return_value = mock_fc
        
        fritzbox_restart.reboot_fritzbox(
            "192.168.178.1", None, "testpass", timeout=30
        )
        
        call_kwargs = mock_fc_class.call_args[1]
        assert call_kwargs['timeout'] == 30
    
    @patch('fritzbox_restart.FritzConnection')
    @patch('builtins.print')
    def test_reboot_uses_no_cache(self, mock_print, mock_fc_class):
        """Verify reboot_fritzbox disables caching for admin operations"""
        mock_fc = Mock()
        mock_fc_class.return_value = mock_fc
        
        fritzbox_restart.reboot_fritzbox(
            "192.168.178.1", None, "testpass"
        )
        
        call_kwargs = mock_fc_class.call_args[1]
        assert call_kwargs['use_cache'] is False


class TestMain:
    """Test the main() function and CLI argument parsing"""
    
    @patch('fritzbox_restart.reboot_fritzbox')
    @patch('builtins.input')
    def test_main_with_confirmation_yes(self, mock_input, mock_reboot):
        """Verify main() proceeds when user confirms"""
        mock_input.return_value = "yes"
        mock_reboot.return_value = (True, "Success")
        
        with patch('sys.argv', ['fritzbox_restart.py', '--password', 'test']):
            with pytest.raises(SystemExit) as exc_info:
                fritzbox_restart.main()
            
            assert exc_info.value.code == 0
            assert mock_reboot.called
    
    @patch('fritzbox_restart.reboot_fritzbox')
    @patch('builtins.input')
    def test_main_with_confirmation_no(self, mock_input, mock_reboot):
        """Verify main() cancels when user declines"""
        mock_input.return_value = "no"
        
        with patch('sys.argv', ['fritzbox_restart.py', '--password', 'test']):
            with pytest.raises(SystemExit) as exc_info:
                fritzbox_restart.main()
            
            assert exc_info.value.code == 0
            assert not mock_reboot.called
    
    @patch('fritzbox_restart.reboot_fritzbox')
    def test_main_with_yes_flag_skips_confirmation(self, mock_reboot):
        """Verify main() skips confirmation with --yes flag"""
        mock_reboot.return_value = (True, "Success")
        
        with patch('sys.argv', ['fritzbox_restart.py', '--password', 'test', '--yes']):
            with pytest.raises(SystemExit) as exc_info:
                fritzbox_restart.main()
            
            assert exc_info.value.code == 0
            assert mock_reboot.called
    
    @patch('fritzbox_restart.reboot_fritzbox')
    def test_main_exits_with_error_on_failure(self, mock_reboot):
        """Verify main() exits with error code on reboot failure"""
        mock_reboot.return_value = (False, "Error message")
        
        with patch('sys.argv', ['fritzbox_restart.py', '--password', 'test', '--yes']):
            with pytest.raises(SystemExit) as exc_info:
                fritzbox_restart.main()
            
            assert exc_info.value.code == 1
    
    def test_main_requires_password(self):
        """Verify main() requires --password argument"""
        with patch('sys.argv', ['fritzbox_restart.py']):
            with pytest.raises(SystemExit) as exc_info:
                fritzbox_restart.main()
            
            # argparse exits with code 2 for missing required arguments
            assert exc_info.value.code == 2
    
    @patch('fritzbox_restart.reboot_fritzbox')
    def test_main_uses_default_host(self, mock_reboot):
        """Verify main() uses default host 192.168.178.1"""
        mock_reboot.return_value = (True, "Success")
        
        with patch('sys.argv', ['fritzbox_restart.py', '--password', 'test', '--yes']):
            try:
                fritzbox_restart.main()
            except SystemExit:
                pass
            
            # Check that reboot_fritzbox was called with default host
            assert mock_reboot.called
            call_args = mock_reboot.call_args[0]
            assert call_args[0] == "192.168.178.1"
    
    @patch('fritzbox_restart.reboot_fritzbox')
    def test_main_uses_custom_host(self, mock_reboot):
        """Verify main() uses custom host when provided"""
        mock_reboot.return_value = (True, "Success")
        
        with patch('sys.argv', ['fritzbox_restart.py', '--host', '192.168.1.1', '--password', 'test', '--yes']):
            try:
                fritzbox_restart.main()
            except SystemExit:
                pass
            
            call_args = mock_reboot.call_args[0]
            assert call_args[0] == "192.168.1.1"
    
    @patch('fritzbox_restart.reboot_fritzbox')
    def test_main_passes_user_when_provided(self, mock_reboot):
        """Verify main() passes user when provided"""
        mock_reboot.return_value = (True, "Success")
        
        with patch('sys.argv', ['fritzbox_restart.py', '--user', 'admin', '--password', 'test', '--yes']):
            try:
                fritzbox_restart.main()
            except SystemExit:
                pass
            
            call_args = mock_reboot.call_args[0]
            assert call_args[1] == "admin"
    
    @patch('fritzbox_restart.reboot_fritzbox')
    def test_main_uses_custom_timeout(self, mock_reboot):
        """Verify main() uses custom timeout when provided"""
        mock_reboot.return_value = (True, "Success")
        
        with patch('sys.argv', ['fritzbox_restart.py', '--password', 'test', '--timeout', '30', '--yes']):
            try:
                fritzbox_restart.main()
            except SystemExit:
                pass
            
            call_args = mock_reboot.call_args[0]
            assert call_args[3] == 30
    
    @patch('builtins.input')
    def test_main_handles_keyboard_interrupt_in_confirmation(self, mock_input):
        """Verify main() handles Ctrl+C gracefully during confirmation"""
        mock_input.side_effect = KeyboardInterrupt()
        
        with patch('sys.argv', ['fritzbox_restart.py', '--password', 'test']):
            with pytest.raises(SystemExit) as exc_info:
                fritzbox_restart.main()
            
            assert exc_info.value.code == 0
    
    @patch('builtins.input')
    def test_main_handles_eof_in_confirmation(self, mock_input):
        """Verify main() handles EOF gracefully during confirmation"""
        mock_input.side_effect = EOFError()
        
        with patch('sys.argv', ['fritzbox_restart.py', '--password', 'test']):
            with pytest.raises(SystemExit) as exc_info:
                fritzbox_restart.main()
            
            assert exc_info.value.code == 0


class TestIntegration:
    """Integration tests for complete workflow"""
    
    @patch('fritzbox_restart.FritzConnection')
    def test_full_workflow_success(self, mock_fc_class):
        """Test the complete successful reboot workflow"""
        mock_fc = Mock()
        mock_fc_class.return_value = mock_fc
        
        # Run the reboot function
        success, message = fritzbox_restart.reboot_fritzbox(
            "192.168.178.1",
            "admin",
            "password123",
            timeout=15
        )
        
        # Verify the complete flow
        assert success is True
        assert "OK" in message or "erfolgreich" in message
        mock_fc.call_action.assert_called_once_with("DeviceConfig:1", "Reboot")
    
    def test_help_message_displays(self):
        """Verify help message can be displayed"""
        with patch('sys.argv', ['fritzbox_restart.py', '--help']):
            with pytest.raises(SystemExit) as exc_info:
                fritzbox_restart.main()
            
            # Help exits with code 0
            assert exc_info.value.code == 0


if __name__ == "__main__":
    # Allow running directly with: python3 test_fritzbox_restart.py
    pytest.main([__file__, "-v"])
