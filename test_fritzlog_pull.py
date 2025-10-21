#!/usr/bin/env python3
"""
Unit tests for fritzlog_pull.py

Run with: pytest test_fritzlog_pull.py -v
or: python3 -m pytest test_fritzlog_pull.py -v
"""

import pytest
import os
import tempfile
import csv
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import fritzlog_pull


class TestNowFunction:
    """Test the now() timestamp function"""
    
    def test_now_returns_formatted_timestamp(self):
        """Verify now() returns a properly formatted timestamp"""
        result = fritzlog_pull.now()
        # Should be in format: YYYY-MM-DD HH:MM:SS
        assert len(result) == 19
        assert result[4] == '-'
        assert result[7] == '-'
        assert result[10] == ' '
        assert result[13] == ':'
        assert result[16] == ':'
        
    def test_now_timestamp_is_parseable(self):
        """Verify now() returns a timestamp that can be parsed back"""
        result = fritzlog_pull.now()
        # Should not raise an exception
        parsed = datetime.strptime(result, "%Y-%m-%d %H:%M:%S")
        assert isinstance(parsed, datetime)


class TestGetSafe:
    """Test the get_safe() error handling wrapper"""
    
    def test_get_safe_returns_dict_on_success(self):
        """Verify get_safe returns the action result on success"""
        mock_fc = Mock()
        mock_fc.call_action.return_value = {"NewValue": "test"}
        
        result = fritzlog_pull.get_safe(mock_fc, "TestService", "TestAction")
        
        assert result == {"NewValue": "test"}
        mock_fc.call_action.assert_called_once_with("TestService", "TestAction")
    
    def test_get_safe_returns_error_dict_on_exception(self):
        """Verify get_safe returns error dict when exception occurs"""
        mock_fc = Mock()
        mock_fc.call_action.side_effect = Exception("Connection failed")
        
        result = fritzlog_pull.get_safe(mock_fc, "TestService", "TestAction")
        
        assert "__error__" in result
        assert "Connection failed" in result["__error__"]


class TestFirstOk:
    """Test the first_ok() service discovery function"""
    
    def test_first_ok_returns_first_successful_result(self):
        """Verify first_ok returns the first successful service call"""
        mock_fc = Mock()
        mock_fc.call_action.side_effect = [
            Exception("First service failed"),
            {"NewValue": "success"},
            {"NewValue": "should not reach"},
        ]
        
        candidates = [
            ("Service1", "Action1"),
            ("Service2", "Action2"),
            ("Service3", "Action3"),
        ]
        
        result = fritzlog_pull.first_ok(mock_fc, candidates)
        
        assert result == {"NewValue": "success"}
        assert mock_fc.call_action.call_count == 2
    
    def test_first_ok_returns_error_when_all_fail(self):
        """Verify first_ok returns error dict when all candidates fail"""
        mock_fc = Mock()
        mock_fc.call_action.side_effect = Exception("Always fails")
        
        candidates = [
            ("Service1", "Action1"),
            ("Service2", "Action2"),
        ]
        
        result = fritzlog_pull.first_ok(mock_fc, candidates)
        
        assert "__error__" in result
        assert result["__error__"] == "no candidate succeeded"
    
    def test_first_ok_with_single_candidate(self):
        """Verify first_ok works with a single candidate"""
        mock_fc = Mock()
        mock_fc.call_action.return_value = {"NewStatus": "Connected"}
        
        candidates = [("WANIPConnection1", "GetStatusInfo")]
        
        result = fritzlog_pull.first_ok(mock_fc, candidates)
        
        assert result == {"NewStatus": "Connected"}


class TestEnsureHeader:
    """Test the ensure_header() CSV header initialization"""
    
    def test_ensure_header_creates_file_with_header(self):
        """Verify ensure_header creates a new file with CSV header"""
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "test.csv")
            header = ["col1", "col2", "col3"]
            
            fritzlog_pull.ensure_header(csv_path, header)
            
            with open(csv_path, "r") as f:
                content = f.read()
            
            assert content == "col1,col2,col3\n"
    
    def test_ensure_header_does_not_overwrite_existing(self):
        """Verify ensure_header does not overwrite existing file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "test.csv")
            
            # Create file with existing content
            with open(csv_path, "w") as f:
                f.write("existing,content\n")
            
            header = ["new", "header"]
            fritzlog_pull.ensure_header(csv_path, header)
            
            # Should still have original content
            with open(csv_path, "r") as f:
                content = f.read()
            
            assert content == "existing,content\n"


class TestCollectOnce:
    """Test the collect_once() data collection function"""
    
    def test_collect_once_returns_all_fields(self):
        """Verify collect_once returns all expected data fields"""
        mock_fc = Mock()
        
        # Mock successful responses for all service calls
        mock_fc.call_action.side_effect = [
            # WAN Status
            {"NewConnectionStatus": "Connected", "NewUptime": "12345", "NewLastConnectionError": "ERROR_NONE"},
            # External IP
            {"NewExternalIPAddress": "1.2.3.4"},
            # Common (traffic)
            {"NewTotalBytesSent": "1000000", "NewTotalBytesReceived": "2000000",
             "NewByteSendRate": "5000", "NewByteReceiveRate": "10000"},
            # Link properties
            {"NewWANAccessType": "DSL", "NewPhysicalLinkStatus": "Up",
             "NewLayer1UpstreamMaxBitRate": "10000000", "NewLayer1DownstreamMaxBitRate": "50000000"},
            # DSL link
            {"NewLinkStatus": "Up"},
            # DSL info
            {"NewUpstreamCurrRate": "9500000", "NewDownstreamCurrRate": "48000000"},
            # DSL stats
            {"NewFECErrors": "0", "NewCRCErrors": "5", "NewHECErrors": "0",
             "NewErroredSecs": "10", "NewSeverelyErroredSecs": "0",
             "NewLinkRetrain": "2", "NewInitErrors": "0", "NewInitTimeouts": "0",
             "NewATUC_FECErrors": "0", "NewATUC_CRCErrors": "3", "NewATUC_HECErrors": "0"},
        ]
        
        result = fritzlog_pull.collect_once(mock_fc)
        
        # Verify all expected fields are present
        expected_fields = [
            "timestamp",
            "wan_connection_status", "wan_uptime_s", "wan_external_ip", "wan_last_error",
            "common_bytes_sent", "common_bytes_recv", "common_rate_send_bps", "common_rate_recv_bps",
            "access_type", "phys_link_status", "l1_up_max_bps", "l1_down_max_bps",
            "dsl_link_status", "dsl_curr_up_bps", "dsl_curr_down_bps",
            "dsl_fec_errors", "dsl_crc_errors", "dsl_hec_errors",
            "dsl_errored_secs", "dsl_severely_errored_secs",
            "dsl_link_retrain", "dsl_init_errors", "dsl_init_timeouts",
            "dsl_atuc_fec_errors", "dsl_atuc_crc_errors", "dsl_atuc_hec_errors",
        ]
        
        for field in expected_fields:
            assert field in result, f"Missing field: {field}"
        
        # Verify some values
        assert result["wan_connection_status"] == "Connected"
        assert result["wan_external_ip"] == "1.2.3.4"
        assert result["common_bytes_sent"] == "1000000"
        assert result["dsl_crc_errors"] == "5"
    
    def test_collect_once_handles_errors_gracefully(self):
        """Verify collect_once handles service errors gracefully"""
        mock_fc = Mock()
        
        # All calls fail
        mock_fc.call_action.side_effect = Exception("Service unavailable")
        
        result = fritzlog_pull.collect_once(mock_fc)
        
        # Should return dict with timestamp and empty values
        assert "timestamp" in result
        assert result["wan_connection_status"] == ""
        assert result["wan_external_ip"] == ""
        assert result["dsl_link_status"] == ""
    
    def test_collect_once_uses_fallback_services(self):
        """Verify collect_once tries fallback service names"""
        mock_fc = Mock()
        
        # First WAN service fails, second succeeds
        call_count = [0]
        def mock_call_action(service, action):
            call_count[0] += 1
            if call_count[0] == 1:
                # First call (WANIPConnection1) fails
                raise Exception("Service not found")
            elif call_count[0] == 2:
                # Second call (WANPPPConnection1) succeeds
                return {"NewConnectionStatus": "Connected", "NewUptime": "999", "NewLastConnectionError": "NONE"}
            else:
                # Subsequent calls return empty/error
                return {}
        
        mock_fc.call_action.side_effect = mock_call_action
        
        result = fritzlog_pull.collect_once(mock_fc)
        
        # Should have gotten the status from the fallback service
        assert result["wan_connection_status"] == "Connected"


class TestOpenFc:
    """Test the open_fc() FritzConnection wrapper"""
    
    @patch('fritzlog_pull.FritzConnection')
    def test_open_fc_creates_connection_with_params(self, mock_fc_class):
        """Verify open_fc creates FritzConnection with correct parameters"""
        mock_instance = Mock()
        mock_fc_class.return_value = mock_instance
        
        result = fritzlog_pull.open_fc("192.168.178.1", "testuser", "testpass", timeout=10)
        
        mock_fc_class.assert_called_once_with(
            address="192.168.178.1",
            user="testuser",
            password="testpass",
            timeout=10,
            use_cache=True
        )
        assert result == mock_instance
    
    @patch('fritzlog_pull.FritzConnection')
    def test_open_fc_with_none_user(self, mock_fc_class):
        """Verify open_fc works with None user (common for older setups)"""
        mock_instance = Mock()
        mock_fc_class.return_value = mock_instance
        
        result = fritzlog_pull.open_fc("192.168.178.1", None, "testpass")
        
        mock_fc_class.assert_called_once_with(
            address="192.168.178.1",
            user=None,
            password="testpass",
            timeout=5,
            use_cache=True
        )


class TestMain:
    """Test the main() function and CLI argument parsing"""
    
    @patch('fritzlog_pull.open_fc')
    @patch('fritzlog_pull.collect_once')
    @patch('builtins.open', create=True)
    @patch('fritzlog_pull.ensure_header')
    @patch('time.sleep')
    def test_main_creates_csv_with_correct_header(self, mock_sleep, mock_ensure, mock_open, mock_collect, mock_open_fc):
        """Verify main() creates CSV with correct header"""
        mock_fc = Mock()
        mock_open_fc.return_value = mock_fc
        mock_collect.return_value = {
            "timestamp": "2025-10-21 12:00:00",
            "wan_connection_status": "Connected",
            # ... other fields with empty values
        }
        
        # Make sleep raise KeyboardInterrupt to exit the loop
        mock_sleep.side_effect = KeyboardInterrupt()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "test.csv")
            
            # Mock sys.argv for argument parsing
            with patch('sys.argv', ['fritzlog_pull.py', '--password', 'test', '--out', csv_path, '--interval', '1']):
                try:
                    fritzlog_pull.main()
                except SystemExit:
                    pass
        
        # Verify ensure_header was called with correct header
        assert mock_ensure.called
        call_args = mock_ensure.call_args[0]
        header = call_args[1]
        
        # Verify header has all 27 expected columns
        assert len(header) == 27
        assert header[0] == "timestamp"
        assert "wan_connection_status" in header
        assert "dsl_fec_errors" in header
        assert "dsl_atuc_hec_errors" in header
    
    @patch('fritzlog_pull.open_fc')
    def test_main_exits_on_connection_failure(self, mock_open_fc):
        """Verify main() exits with error message on connection failure"""
        mock_open_fc.side_effect = Exception("Connection refused")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "test.csv")
            
            with patch('sys.argv', ['fritzlog_pull.py', '--password', 'test', '--out', csv_path]):
                with pytest.raises(SystemExit) as exc_info:
                    fritzlog_pull.main()
                
                assert "Verbindung zur FRITZ!Box fehlgeschlagen" in str(exc_info.value)
    
    def test_main_requires_password_argument(self):
        """Verify main() requires --password argument"""
        with patch('sys.argv', ['fritzlog_pull.py']):
            with pytest.raises(SystemExit):
                fritzlog_pull.main()
    
    def test_main_uses_default_host(self):
        """Verify main() uses default host 192.168.178.1"""
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "test.csv")
            
            with patch('fritzlog_pull.open_fc') as mock_open_fc:
                mock_open_fc.side_effect = SystemExit(0)  # Exit immediately
                
                with patch('sys.argv', ['fritzlog_pull.py', '--password', 'test', '--out', csv_path]):
                    try:
                        fritzlog_pull.main()
                    except SystemExit:
                        pass
                
                # Check that open_fc was called with default host
                assert mock_open_fc.called
                call_args = mock_open_fc.call_args[0]
                assert call_args[0] == "192.168.178.1"


class TestIntegration:
    """Integration tests for the complete workflow"""
    
    def test_csv_output_format(self):
        """Test that CSV output is properly formatted"""
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "test_output.csv")
            
            header = ["timestamp", "wan_connection_status", "wan_uptime_s"]
            fritzlog_pull.ensure_header(csv_path, header)
            
            # Simulate writing a data row
            with open(csv_path, "a", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["2025-10-21 12:00:00", "Connected", "12345"])
            
            # Read back and verify
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                rows = list(reader)
            
            assert len(rows) == 2  # Header + 1 data row
            assert rows[0] == ["timestamp", "wan_connection_status", "wan_uptime_s"]
            assert rows[1] == ["2025-10-21 12:00:00", "Connected", "12345"]
    
    def test_all_27_columns_in_header(self):
        """Verify that all 27 columns from extended version are present"""
        expected_columns = [
            "timestamp",
            "wan_connection_status", "wan_uptime_s", "wan_external_ip", "wan_last_error",
            "common_bytes_sent", "common_bytes_recv", "common_rate_send_bps", "common_rate_recv_bps",
            "access_type", "phys_link_status", "l1_up_max_bps", "l1_down_max_bps",
            "dsl_link_status", "dsl_curr_up_bps", "dsl_curr_down_bps",
            "dsl_fec_errors", "dsl_crc_errors", "dsl_hec_errors",
            "dsl_errored_secs", "dsl_severely_errored_secs",
            "dsl_link_retrain", "dsl_init_errors", "dsl_init_timeouts",
            "dsl_atuc_fec_errors", "dsl_atuc_crc_errors", "dsl_atuc_hec_errors",
        ]
        
        # This is the header defined in main()
        with patch('sys.argv', ['fritzlog_pull.py', '--help']):
            # Just verify we can parse arguments (will exit with help)
            try:
                fritzlog_pull.main()
            except SystemExit:
                pass
        
        # Verify the header in the actual code matches expected
        import inspect
        source = inspect.getsource(fritzlog_pull.main)
        
        # All expected columns should be in the source
        for col in expected_columns:
            assert col in source, f"Column '{col}' not found in header definition"


class TestExtendedFunctionalityPresence:
    """Verify all extended functionality from fritzlog_pull_extended is included"""
    
    def test_first_ok_function_exists(self):
        """Verify first_ok() helper function exists (new in extended version)"""
        assert hasattr(fritzlog_pull, 'first_ok')
        assert callable(fritzlog_pull.first_ok)
    
    def test_extended_services_are_checked(self):
        """Verify extended service names are tried (e.g., WANIPConn1, WANPPPConn1)"""
        import inspect
        source = inspect.getsource(fritzlog_pull.collect_once)
        
        # Check for extended service name variants
        assert "WANIPConn1" in source or "WANPPPConn1" in source
        assert "WANCommonInterfaceConfig1" in source
        assert "WANDSLLinkConfig1" in source or "WANDSLLinkConfig" in source
        assert "WANDSLInterfaceConfig1" in source or "WANDSLInterfaceConfig" in source
    
    def test_dsl_statistics_collected(self):
        """Verify DSL statistics are collected (new in extended version)"""
        import inspect
        source = inspect.getsource(fritzlog_pull.collect_once)
        
        # Check for DSL statistics calls
        assert "GetStatisticsTotal" in source
        assert "GetCommonLinkProperties" in source
    
    def test_all_dsl_error_fields_present(self):
        """Verify all DSL error fields from extended version are collected"""
        mock_fc = Mock()
        mock_fc.call_action.side_effect = Exception("Not testing actual calls")
        
        result = fritzlog_pull.collect_once(mock_fc)
        
        # All these fields should exist (from extended version)
        extended_fields = [
            "dsl_fec_errors", "dsl_crc_errors", "dsl_hec_errors",
            "dsl_errored_secs", "dsl_severely_errored_secs",
            "dsl_link_retrain", "dsl_init_errors", "dsl_init_timeouts",
            "dsl_atuc_fec_errors", "dsl_atuc_crc_errors", "dsl_atuc_hec_errors",
        ]
        
        for field in extended_fields:
            assert field in result, f"Extended field '{field}' missing"
    
    def test_rate_fields_present(self):
        """Verify rate fields from extended version are collected"""
        mock_fc = Mock()
        mock_fc.call_action.side_effect = Exception("Not testing actual calls")
        
        result = fritzlog_pull.collect_once(mock_fc)
        
        # These rate fields are from extended version
        assert "common_rate_send_bps" in result
        assert "common_rate_recv_bps" in result
        assert "dsl_curr_up_bps" in result
        assert "dsl_curr_down_bps" in result
    
    def test_link_properties_fields_present(self):
        """Verify link properties from extended version are collected"""
        mock_fc = Mock()
        mock_fc.call_action.side_effect = Exception("Not testing actual calls")
        
        result = fritzlog_pull.collect_once(mock_fc)
        
        # These fields are from GetCommonLinkProperties (extended version)
        assert "access_type" in result
        assert "phys_link_status" in result
        assert "l1_up_max_bps" in result
        assert "l1_down_max_bps" in result


if __name__ == "__main__":
    # Allow running directly with: python3 test_fritzlog_pull.py
    pytest.main([__file__, "-v"])
