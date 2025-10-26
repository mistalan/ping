#!/usr/bin/env python3
"""
Unit tests for analyze_netlogs.py

Run with: pytest test_analyze_netlogs.py -v
or: python3 -m pytest test_analyze_netlogs.py -v
"""

import pytest
import os
import csv
import tempfile
from datetime import datetime, timedelta
from unittest.mock import patch, Mock
import analyze_netlogs


class TestParseTime:
    """Test the parse_time() function"""
    
    def test_parse_time_standard_format(self):
        """Verify parse_time parses standard format correctly"""
        result = analyze_netlogs.parse_time("2025-10-21 12:30:45")
        assert result == datetime(2025, 10, 21, 12, 30, 45)
    
    def test_parse_time_german_format(self):
        """Verify parse_time parses German format correctly"""
        result = analyze_netlogs.parse_time("21.10.2025 12:30:45")
        assert result == datetime(2025, 10, 21, 12, 30, 45)
    
    def test_parse_time_iso_format(self):
        """Verify parse_time parses ISO format correctly"""
        result = analyze_netlogs.parse_time("2025-10-21T12:30:45")
        assert result == datetime(2025, 10, 21, 12, 30, 45)
    
    def test_parse_time_invalid_returns_none(self):
        """Verify parse_time returns None for invalid input"""
        result = analyze_netlogs.parse_time("invalid timestamp")
        assert result is None
    
    def test_parse_time_empty_string(self):
        """Verify parse_time handles empty string"""
        result = analyze_netlogs.parse_time("")
        assert result is None


class TestToFloat:
    """Test the to_float() conversion function"""
    
    def test_to_float_valid_number(self):
        """Verify to_float converts valid numbers"""
        assert analyze_netlogs.to_float("10.5") == 10.5
        assert analyze_netlogs.to_float("100") == 100.0
        assert analyze_netlogs.to_float(42) == 42.0
    
    def test_to_float_none(self):
        """Verify to_float returns NaN for None"""
        import math
        result = analyze_netlogs.to_float(None)
        assert math.isnan(result)
    
    def test_to_float_empty_string(self):
        """Verify to_float returns NaN for empty string"""
        import math
        result = analyze_netlogs.to_float("")
        assert math.isnan(result)
    
    def test_to_float_invalid_string(self):
        """Verify to_float returns NaN for invalid input"""
        import math
        result = analyze_netlogs.to_float("not a number")
        assert math.isnan(result)


class TestHumanDuration:
    """Test the human_duration() formatting function"""
    
    def test_human_duration_seconds(self):
        """Verify human_duration formats seconds correctly"""
        delta = timedelta(seconds=45)
        result = analyze_netlogs.human_duration(delta)
        assert result == "45s"
    
    def test_human_duration_minutes(self):
        """Verify human_duration formats minutes correctly"""
        delta = timedelta(seconds=150)  # 2m 30s
        result = analyze_netlogs.human_duration(delta)
        assert result == "2m 30s"
    
    def test_human_duration_hours(self):
        """Verify human_duration formats hours correctly"""
        delta = timedelta(seconds=7260)  # 2h 1m
        result = analyze_netlogs.human_duration(delta)
        assert result == "2h 1m"
    
    def test_human_duration_zero(self):
        """Verify human_duration handles zero duration"""
        delta = timedelta(seconds=0)
        result = analyze_netlogs.human_duration(delta)
        assert result == "0s"
    
    def test_human_duration_exactly_one_minute(self):
        """Verify human_duration formats exactly 1 minute"""
        delta = timedelta(seconds=60)
        result = analyze_netlogs.human_duration(delta)
        assert result == "1m 0s"


class TestExtractDetailsKey:
    """Test the extract_details_key() helper function"""
    
    def test_extract_details_key_with_colon(self):
        """Verify extract_details_key extracts key before colon"""
        result = analyze_netlogs.extract_details_key("target: 8.8.8.8")
        assert result == "target"
    
    def test_extract_details_key_with_arrow(self):
        """Verify extract_details_key extracts key before arrow"""
        result = analyze_netlogs.extract_details_key("old -> new")
        assert result == "old"
    
    def test_extract_details_key_no_separator(self):
        """Verify extract_details_key returns full string if no separator"""
        result = analyze_netlogs.extract_details_key("simple text")
        assert result == "simple text"
    
    def test_extract_details_key_empty_string(self):
        """Verify extract_details_key handles empty string"""
        result = analyze_netlogs.extract_details_key("")
        assert result == ""


class TestDetectNetwatchIncidents:
    """Test the detect_netwatch_incidents() function"""
    
    def test_detect_dns_failure(self):
        """Verify DNS failure detection"""
        data = [
            {"timestamp": datetime(2025, 10, 21, 12, 0, 0), "dns_ok": "0", "dns_ms": ""},
        ]
        incidents = analyze_netlogs.detect_netwatch_incidents(data, 20, 1.0)
        
        dns_fails = [i for i in incidents if i["type"] == "DNS_FAIL"]
        assert len(dns_fails) == 1
        assert dns_fails[0]["source"] == "PC"
    
    def test_detect_adapter_change(self):
        """Verify adapter status change detection"""
        data = [
            {"timestamp": datetime(2025, 10, 21, 12, 0, 0), "adapter": "Ethernet"},
            {"timestamp": datetime(2025, 10, 21, 12, 1, 0), "adapter": "WiFi"},
        ]
        incidents = analyze_netlogs.detect_netwatch_incidents(data, 20, 1.0)
        
        adapter_changes = [i for i in incidents if i["type"] == "ADAPTER_CHANGE"]
        assert len(adapter_changes) == 1
        assert "Ethernet -> WiFi" in adapter_changes[0]["details"]
    
    def test_detect_media_status_change(self):
        """Verify media status change detection"""
        data = [
            {"timestamp": datetime(2025, 10, 21, 12, 0, 0), "media_status": "Connected"},
            {"timestamp": datetime(2025, 10, 21, 12, 1, 0), "media_status": "Disconnected"},
        ]
        incidents = analyze_netlogs.detect_netwatch_incidents(data, 20, 1.0)
        
        status_changes = [i for i in incidents if i["type"] == "MEDIA_STATUS_CHANGE"]
        assert len(status_changes) == 1
        assert "Connected -> Disconnected" in status_changes[0]["details"]
    
    def test_detect_latency_spike(self):
        """Verify latency spike detection"""
        data = [
            {
                "timestamp": datetime(2025, 10, 21, 12, 0, 0),
                "ping_8.8.8.8_avg_ms": "50",
            }
        ]
        incidents = analyze_netlogs.detect_netwatch_incidents(data, 20, 1.0)
        
        latency_spikes = [i for i in incidents if i["type"] == "LATENCY_SPIKE"]
        assert len(latency_spikes) == 1
        assert "8.8.8.8" in latency_spikes[0]["details"]
        assert "50" in latency_spikes[0]["details"]
    
    def test_detect_loss_spike(self):
        """Verify packet loss spike detection"""
        data = [
            {
                "timestamp": datetime(2025, 10, 21, 12, 0, 0),
                "ping_8.8.8.8_avg_ms": "10",
                "ping_8.8.8.8_loss_pct": "5.0",
            }
        ]
        incidents = analyze_netlogs.detect_netwatch_incidents(data, 20, 1.0)
        
        loss_spikes = [i for i in incidents if i["type"] == "LOSS_SPIKE"]
        assert len(loss_spikes) == 1
        assert "8.8.8.8" in loss_spikes[0]["details"]
        assert "5.0" in loss_spikes[0]["details"]
    
    def test_no_incidents_when_below_threshold(self):
        """Verify no incidents when values are below thresholds"""
        data = [
            {
                "timestamp": datetime(2025, 10, 21, 12, 0, 0),
                "dns_ok": "1",
                "ping_8.8.8.8_avg_ms": "10",
                "ping_8.8.8.8_loss_pct": "0.5",
            }
        ]
        incidents = analyze_netlogs.detect_netwatch_incidents(data, 20, 1.0)
        
        assert len(incidents) == 0
    
    def test_multiple_ping_targets(self):
        """Verify detection works with multiple ping targets"""
        data = [
            {
                "timestamp": datetime(2025, 10, 21, 12, 0, 0),
                "ping_8.8.8.8_avg_ms": "50",
                "ping_1.1.1.1_avg_ms": "30",
                "ping_192.168.178.1_avg_ms": "5",
            }
        ]
        incidents = analyze_netlogs.detect_netwatch_incidents(data, 20, 1.0)
        
        latency_spikes = [i for i in incidents if i["type"] == "LATENCY_SPIKE"]
        assert len(latency_spikes) == 2  # 8.8.8.8 and 1.1.1.1 exceed threshold


class TestDetectFritzIncidents:
    """Test the detect_fritz_incidents() function"""
    
    def test_detect_wan_reconnect(self):
        """Verify WAN reconnect detection based on uptime reset"""
        data = [
            {"timestamp": datetime(2025, 10, 21, 12, 0, 0), "wan_uptime_s": "1000"},
            {"timestamp": datetime(2025, 10, 21, 12, 1, 0), "wan_uptime_s": "10"},
        ]
        incidents = analyze_netlogs.detect_fritz_incidents(data)
        
        reconnects = [i for i in incidents if i["type"] == "WAN_RECONNECT"]
        assert len(reconnects) == 1
        assert "1000" in reconnects[0]["details"]
        assert "10" in reconnects[0]["details"]
    
    def test_detect_wan_status_change(self):
        """Verify WAN status change detection"""
        data = [
            {"timestamp": datetime(2025, 10, 21, 12, 0, 0), "wan_connection_status": "Connected"},
            {"timestamp": datetime(2025, 10, 21, 12, 1, 0), "wan_connection_status": "Disconnected"},
        ]
        incidents = analyze_netlogs.detect_fritz_incidents(data)
        
        status_changes = [i for i in incidents if i["type"] == "WAN_STATUS_CHANGE"]
        assert len(status_changes) == 1
        assert "Connected -> Disconnected" in status_changes[0]["details"]
    
    def test_detect_external_ip_change(self):
        """Verify external IP change detection"""
        data = [
            {"timestamp": datetime(2025, 10, 21, 12, 0, 0), "wan_external_ip": "1.2.3.4"},
            {"timestamp": datetime(2025, 10, 21, 12, 1, 0), "wan_external_ip": "5.6.7.8"},
        ]
        incidents = analyze_netlogs.detect_fritz_incidents(data)
        
        ip_changes = [i for i in incidents if i["type"] == "EXTERNAL_IP_CHANGE"]
        assert len(ip_changes) == 1
        assert "1.2.3.4 -> 5.6.7.8" in ip_changes[0]["details"]
    
    def test_detect_dsl_link_abnormal(self):
        """Verify DSL link abnormality detection"""
        data = [
            {"timestamp": datetime(2025, 10, 21, 12, 0, 0), "dsl_link_status": "Down"},
        ]
        incidents = analyze_netlogs.detect_fritz_incidents(data)
        
        dsl_abnormal = [i for i in incidents if i["type"] == "DSL_LINK_ABNORMAL"]
        assert len(dsl_abnormal) == 1
        assert "Down" in dsl_abnormal[0]["details"]
    
    def test_no_incidents_when_stable(self):
        """Verify no incidents when connection is stable"""
        data = [
            {
                "timestamp": datetime(2025, 10, 21, 12, 0, 0),
                "wan_connection_status": "Connected",
                "wan_uptime_s": "1000",
                "wan_external_ip": "1.2.3.4",
                "dsl_link_status": "Up",
            },
            {
                "timestamp": datetime(2025, 10, 21, 12, 1, 0),
                "wan_connection_status": "Connected",
                "wan_uptime_s": "1060",
                "wan_external_ip": "1.2.3.4",
                "dsl_link_status": "Up",
            },
        ]
        incidents = analyze_netlogs.detect_fritz_incidents(data)
        
        assert len(incidents) == 0


class TestAggregateBursts:
    """Test the aggregate_bursts() function"""
    
    def test_aggregate_close_incidents(self):
        """Verify incidents close in time are aggregated"""
        start = datetime(2025, 10, 21, 12, 0, 0)
        incidents = [
            {
                "source": "PC",
                "type": "LATENCY_SPIKE",
                "start": start,
                "end": start,
                "details": "8.8.8.8: 50ms",
            },
            {
                "source": "PC",
                "type": "LATENCY_SPIKE",
                "start": start + timedelta(seconds=30),
                "end": start + timedelta(seconds=30),
                "details": "8.8.8.8: 55ms",
            },
        ]
        
        aggregated = analyze_netlogs.aggregate_bursts(incidents, min_span_seconds=60)
        
        # Should be combined into one burst
        assert len(aggregated) == 1
        assert aggregated[0]["start"] == start
        assert aggregated[0]["end"] == start + timedelta(seconds=30)
    
    def test_no_aggregation_for_distant_incidents(self):
        """Verify distant incidents are not aggregated"""
        start = datetime(2025, 10, 21, 12, 0, 0)
        incidents = [
            {
                "source": "PC",
                "type": "LATENCY_SPIKE",
                "start": start,
                "end": start,
                "details": "8.8.8.8: 50ms",
            },
            {
                "source": "PC",
                "type": "LATENCY_SPIKE",
                "start": start + timedelta(minutes=10),
                "end": start + timedelta(minutes=10),
                "details": "8.8.8.8: 55ms",
            },
        ]
        
        aggregated = analyze_netlogs.aggregate_bursts(incidents, min_span_seconds=60)
        
        # Should remain separate
        assert len(aggregated) == 2
    
    def test_different_types_not_aggregated(self):
        """Verify different incident types are not aggregated"""
        start = datetime(2025, 10, 21, 12, 0, 0)
        incidents = [
            {
                "source": "PC",
                "type": "LATENCY_SPIKE",
                "start": start,
                "end": start,
                "details": "8.8.8.8: 50ms",
            },
            {
                "source": "PC",
                "type": "LOSS_SPIKE",
                "start": start + timedelta(seconds=30),
                "end": start + timedelta(seconds=30),
                "details": "8.8.8.8: 5%",
            },
        ]
        
        aggregated = analyze_netlogs.aggregate_bursts(incidents, min_span_seconds=60)
        
        # Different types should not be aggregated
        assert len(aggregated) == 2


class TestLoadCsv:
    """Test the load_csv() function"""
    
    def test_load_csv_with_valid_data(self):
        """Verify load_csv reads CSV files correctly"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'value'])
            writer.writerow(['2025-10-21 12:00:00', '100'])
            writer.writerow(['2025-10-21 12:01:00', '200'])
            csv_path = f.name
        
        try:
            data, columns = analyze_netlogs.load_csv(csv_path)
            
            # Verify data was loaded
            assert len(data) >= 2
            assert 'timestamp' in columns
            assert 'value' in columns
            
            # Verify timestamps were parsed
            if hasattr(data, '__getitem__'):
                first_row = data[0] if isinstance(data, list) else data.iloc[0]
                assert isinstance(first_row['timestamp'], datetime) or first_row['timestamp'] is not None
        finally:
            os.unlink(csv_path)
    
    def test_load_csv_handles_missing_file(self):
        """Verify load_csv handles missing file gracefully"""
        with pytest.raises(FileNotFoundError):
            analyze_netlogs.load_csv('/nonexistent/path/file.csv')


class TestMainFunction:
    """Test the main() function and CLI"""
    
    def test_main_creates_output_file(self):
        """Verify main() creates incidents CSV file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create input files
            netwatch_path = os.path.join(tmpdir, 'netwatch.csv')
            fritz_path = os.path.join(tmpdir, 'fritz.csv')
            output_path = os.path.join(tmpdir, 'incidents.csv')
            
            # Create minimal netwatch CSV
            with open(netwatch_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'adapter', 'dns_ok', 'ping_8.8.8.8_avg_ms'])
                writer.writerow(['2025-10-21 12:00:00', 'Ethernet', '1', '10'])
            
            # Create minimal fritz CSV
            with open(fritz_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'wan_connection_status', 'wan_uptime_s'])
                writer.writerow(['2025-10-21 12:00:00', 'Connected', '1000'])
            
            # Run main with arguments
            with patch('sys.argv', [
                'analyze_netlogs.py',
                '--netwatch', netwatch_path,
                '--fritz', fritz_path,
                '--out', output_path
            ]):
                analyze_netlogs.main()
            
            # Verify output file was created
            assert os.path.exists(output_path)
            
            # Verify output has correct header
            with open(output_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader)
                assert header == ['source', 'type', 'start', 'end', 'duration', 'details']
    
    def test_main_with_latency_threshold(self):
        """Verify main() respects latency threshold parameter"""
        with tempfile.TemporaryDirectory() as tmpdir:
            netwatch_path = os.path.join(tmpdir, 'netwatch.csv')
            fritz_path = os.path.join(tmpdir, 'fritz.csv')
            output_path = os.path.join(tmpdir, 'incidents.csv')
            
            # Create netwatch CSV with high latency
            with open(netwatch_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'ping_8.8.8.8_avg_ms'])
                writer.writerow(['2025-10-21 12:00:00', '50'])
            
            # Create empty fritz CSV
            with open(fritz_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'wan_uptime_s'])
                writer.writerow(['2025-10-21 12:00:00', '1000'])
            
            # Run with high threshold - should not detect spike
            with patch('sys.argv', [
                'analyze_netlogs.py',
                '--netwatch', netwatch_path,
                '--fritz', fritz_path,
                '--out', output_path,
                '--latency', '100'
            ]):
                analyze_netlogs.main()
            
            # Verify no incidents detected
            with open(output_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # skip header
                rows = list(reader)
                assert len(rows) == 0


if __name__ == "__main__":
    # Allow running directly with: python3 test_analyze_netlogs.py
    pytest.main([__file__, "-v"])
