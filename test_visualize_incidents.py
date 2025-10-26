#!/usr/bin/env python3
"""
Unit tests for visualize_incidents.py

Run with: pytest test_visualize_incidents.py -v
or: python3 -m pytest test_visualize_incidents.py -v
"""

import pytest
import os
import csv
import tempfile
from datetime import datetime
from unittest.mock import patch, Mock, MagicMock
import visualize_incidents


class TestParseTime:
    """Test the parse_time() function"""
    
    def test_parse_time_valid_format(self):
        """Verify parse_time parses valid timestamp"""
        result = visualize_incidents.parse_time("2025-10-21 12:30:45")
        assert result == datetime(2025, 10, 21, 12, 30, 45)
    
    def test_parse_time_invalid_format(self):
        """Verify parse_time returns None for invalid format"""
        result = visualize_incidents.parse_time("invalid")
        assert result is None
    
    def test_parse_time_empty_string(self):
        """Verify parse_time handles empty string"""
        result = visualize_incidents.parse_time("")
        assert result is None


class TestLoadIncidents:
    """Test the load_incidents() function"""
    
    def test_load_incidents_valid_csv(self):
        """Verify load_incidents reads CSV correctly"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['source', 'type', 'start', 'end', 'duration', 'details'])
            writer.writerow(['PC', 'LATENCY_SPIKE', '2025-10-21 12:00:00', '2025-10-21 12:01:00', '1m 0s', 'Test'])
            writer.writerow(['FRITZ', 'WAN_RECONNECT', '2025-10-21 12:05:00', '2025-10-21 12:05:30', '30s', 'Test2'])
            csv_path = f.name
        
        try:
            incidents = visualize_incidents.load_incidents(csv_path)
            
            assert len(incidents) == 2
            assert incidents[0]['source'] == 'PC'
            assert incidents[0]['type'] == 'LATENCY_SPIKE'
            assert isinstance(incidents[0]['start'], datetime)
            assert isinstance(incidents[0]['end'], datetime)
        finally:
            os.unlink(csv_path)
    
    def test_load_incidents_missing_file(self):
        """Verify load_incidents exits gracefully for missing file"""
        with pytest.raises(SystemExit):
            visualize_incidents.load_incidents('/nonexistent/file.csv')
    
    def test_load_incidents_skips_invalid_timestamps(self):
        """Verify load_incidents skips rows with invalid timestamps"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['source', 'type', 'start', 'end', 'duration', 'details'])
            writer.writerow(['PC', 'TEST', '2025-10-21 12:00:00', '2025-10-21 12:01:00', '1m', 'Valid'])
            writer.writerow(['PC', 'TEST', 'invalid', 'invalid', '1m', 'Invalid'])
            csv_path = f.name
        
        try:
            incidents = visualize_incidents.load_incidents(csv_path)
            
            # Should only load the valid incident
            assert len(incidents) == 1
            assert incidents[0]['details'] == 'Valid'
        finally:
            os.unlink(csv_path)


class TestCreateTimelinePlot:
    """Test the create_timeline_plot() function"""
    
    @patch('visualize_incidents.plt.savefig')
    @patch('visualize_incidents.plt.close')
    @patch('visualize_incidents.plt.subplots')
    def test_create_timeline_plot_creates_file(self, mock_subplots, mock_close, mock_savefig):
        """Verify create_timeline_plot creates output file"""
        # Setup mock
        mock_fig = Mock()
        mock_ax = Mock()
        mock_subplots.return_value = (mock_fig, mock_ax)
        
        incidents = [
            {
                'source': 'PC',
                'type': 'LATENCY_SPIKE',
                'start': datetime(2025, 10, 21, 12, 0, 0),
                'end': datetime(2025, 10, 21, 12, 1, 0),
                'details': 'Test'
            }
        ]
        
        output_path = '/tmp/test_timeline.png'
        visualize_incidents.create_timeline_plot(incidents, output_path)
        
        # Verify savefig was called with correct path
        mock_savefig.assert_called_once_with(output_path, dpi=150, bbox_inches='tight')
        mock_close.assert_called_once()
    
    def test_create_timeline_plot_empty_incidents(self):
        """Verify create_timeline_plot handles empty incident list"""
        incidents = []
        
        output_path = '/tmp/test_timeline.png'
        # Should just print a message and return
        visualize_incidents.create_timeline_plot(incidents, output_path)
        # No exception should be raised
    
    @patch('visualize_incidents.plt.savefig')
    @patch('visualize_incidents.plt.close')
    @patch('visualize_incidents.plt.subplots')
    def test_create_timeline_plot_multiple_types(self, mock_subplots, mock_close, mock_savefig):
        """Verify create_timeline_plot handles multiple incident types"""
        # Setup mock
        mock_fig = Mock()
        mock_ax = Mock()
        mock_subplots.return_value = (mock_fig, mock_ax)
        
        incidents = [
            {
                'source': 'PC',
                'type': 'LATENCY_SPIKE',
                'start': datetime(2025, 10, 21, 12, 0, 0),
                'end': datetime(2025, 10, 21, 12, 1, 0),
                'details': 'Test1'
            },
            {
                'source': 'FRITZ',
                'type': 'WAN_RECONNECT',
                'start': datetime(2025, 10, 21, 12, 5, 0),
                'end': datetime(2025, 10, 21, 12, 5, 30),
                'details': 'Test2'
            }
        ]
        
        output_path = '/tmp/test_timeline.png'
        visualize_incidents.create_timeline_plot(incidents, output_path)
        
        # Should create plot
        mock_savefig.assert_called_once()


class TestCreateSummaryCharts:
    """Test the create_summary_charts() function"""
    
    @patch('visualize_incidents.plt.savefig')
    @patch('visualize_incidents.plt.close')
    @patch('visualize_incidents.plt.subplots')
    @patch('visualize_incidents.plt.cm')
    def test_create_summary_charts_creates_file(self, mock_cm, mock_subplots, mock_close, mock_savefig):
        """Verify create_summary_charts creates output file"""
        # Setup mocks
        mock_fig = Mock()
        mock_ax1 = Mock()
        mock_ax2 = Mock()
        mock_subplots.return_value = (mock_fig, (mock_ax1, mock_ax2))
        
        # Mock the pie chart return value
        mock_ax1.pie.return_value = ([], [], [])
        mock_ax2.bar.return_value = []
        
        # Mock colormap
        mock_cm.tab20.return_value = [[1, 0, 0, 1], [0, 1, 0, 1]]
        
        incidents = [
            {
                'source': 'PC',
                'type': 'LATENCY_SPIKE',
                'start': datetime(2025, 10, 21, 12, 0, 0),
                'end': datetime(2025, 10, 21, 12, 1, 0),
            },
            {
                'source': 'FRITZ',
                'type': 'WAN_RECONNECT',
                'start': datetime(2025, 10, 21, 12, 5, 0),
                'end': datetime(2025, 10, 21, 12, 5, 30),
            }
        ]
        
        output_dir = '/tmp'
        visualize_incidents.create_summary_charts(incidents, output_dir)
        
        # Verify savefig was called
        assert mock_savefig.called
        mock_close.assert_called_once()
    
    def test_create_summary_charts_empty_incidents(self):
        """Verify create_summary_charts handles empty incident list"""
        incidents = []
        
        output_dir = '/tmp'
        # Should just print a message and return
        visualize_incidents.create_summary_charts(incidents, output_dir)
        # No exception should be raised


class TestCreateHtmlReport:
    """Test the create_html_report() function"""
    
    def test_create_html_report_creates_file(self):
        """Verify create_html_report creates HTML file"""
        incidents = [
            {
                'source': 'PC',
                'type': 'LATENCY_SPIKE',
                'start': datetime(2025, 10, 21, 12, 0, 0),
                'end': datetime(2025, 10, 21, 12, 1, 0),
                'duration': '1m 0s',
                'details': 'Test incident'
            }
        ]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'report.html')
            visualize_incidents.create_html_report(incidents, output_path)
            
            # Verify file was created
            assert os.path.exists(output_path)
            
            # Verify file contains expected content
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert 'Network Incidents Report' in content
                assert 'LATENCY_SPIKE' in content
                assert 'Test incident' in content
    
    def test_create_html_report_includes_statistics(self):
        """Verify create_html_report includes statistics"""
        incidents = [
            {
                'source': 'PC',
                'type': 'LATENCY_SPIKE',
                'start': datetime(2025, 10, 21, 12, 0, 0),
                'end': datetime(2025, 10, 21, 12, 1, 0),
                'duration': '1m 0s',
                'details': 'Test1'
            },
            {
                'source': 'FRITZ',
                'type': 'WAN_RECONNECT',
                'start': datetime(2025, 10, 21, 12, 5, 0),
                'end': datetime(2025, 10, 21, 12, 5, 30),
                'duration': '30s',
                'details': 'Test2'
            }
        ]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'report.html')
            visualize_incidents.create_html_report(incidents, output_path)
            
            # Verify statistics are included
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert 'Total Incidents' in content or 'Incidents' in content
    
    def test_create_html_report_empty_incidents(self):
        """Verify create_html_report handles empty incidents"""
        incidents = []
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'report.html')
            # With empty incidents, the function returns early without creating file
            visualize_incidents.create_html_report(incidents, output_path)
            
            # The function prints a message and returns without creating a file
            # This is expected behavior, so we just verify no exception is raised


class TestMainFunction:
    """Test the main() function and CLI"""
    
    @patch('visualize_incidents.create_timeline_plot')
    @patch('visualize_incidents.create_summary_charts')
    @patch('visualize_incidents.create_html_report')
    def test_main_creates_all_outputs(self, mock_html, mock_summary, mock_timeline):
        """Verify main() creates all output files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create input CSV
            input_path = os.path.join(tmpdir, 'incidents.csv')
            with open(input_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['source', 'type', 'start', 'end', 'duration', 'details'])
                writer.writerow(['PC', 'LATENCY_SPIKE', '2025-10-21 12:00:00', '2025-10-21 12:01:00', '1m', 'Test'])
            
            # Run main with arguments
            with patch('sys.argv', [
                'visualize_incidents.py',
                '--input', input_path,
                '--output-dir', tmpdir,
                '--html'
            ]):
                visualize_incidents.main()
            
            # Verify all functions were called
            assert mock_timeline.called
            assert mock_summary.called
            assert mock_html.called
    
    @patch('visualize_incidents.create_timeline_plot')
    @patch('visualize_incidents.create_summary_charts')
    def test_main_respects_no_timeline_flag(self, mock_summary, mock_timeline):
        """Verify main() respects --no-timeline flag"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create input CSV
            input_path = os.path.join(tmpdir, 'incidents.csv')
            with open(input_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['source', 'type', 'start', 'end', 'duration', 'details'])
                writer.writerow(['PC', 'LATENCY_SPIKE', '2025-10-21 12:00:00', '2025-10-21 12:01:00', '1m', 'Test'])
            
            # Run main with --no-timeline
            with patch('sys.argv', [
                'visualize_incidents.py',
                '--input', input_path,
                '--output-dir', tmpdir,
                '--no-timeline'
            ]):
                visualize_incidents.main()
            
            # Timeline should not be created
            mock_timeline.assert_not_called()
            # Summary should still be created
            assert mock_summary.called
    
    @patch('visualize_incidents.create_timeline_plot')
    @patch('visualize_incidents.create_summary_charts')
    def test_main_respects_no_summary_flag(self, mock_summary, mock_timeline):
        """Verify main() respects --no-summary flag"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create input CSV
            input_path = os.path.join(tmpdir, 'incidents.csv')
            with open(input_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['source', 'type', 'start', 'end', 'duration', 'details'])
                writer.writerow(['PC', 'LATENCY_SPIKE', '2025-10-21 12:00:00', '2025-10-21 12:01:00', '1m', 'Test'])
            
            # Run main with --no-summary
            with patch('sys.argv', [
                'visualize_incidents.py',
                '--input', input_path,
                '--output-dir', tmpdir,
                '--no-summary'
            ]):
                visualize_incidents.main()
            
            # Summary should not be created
            mock_summary.assert_not_called()
            # Timeline should still be created
            assert mock_timeline.called
    
    def test_main_requires_input_argument(self):
        """Verify main() requires --input argument"""
        with patch('sys.argv', ['visualize_incidents.py']):
            with pytest.raises(SystemExit):
                visualize_incidents.main()


class TestIntegration:
    """Integration tests for complete workflow"""
    
    def test_full_workflow_creates_all_files(self):
        """Test the complete visualization workflow"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create input CSV with realistic data
            input_path = os.path.join(tmpdir, 'incidents.csv')
            with open(input_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['source', 'type', 'start', 'end', 'duration', 'details'])
                writer.writerow(['PC', 'LATENCY_SPIKE', '2025-10-21 12:00:00', '2025-10-21 12:01:00', '1m 0s', '8.8.8.8: 50ms'])
                writer.writerow(['PC', 'LOSS_SPIKE', '2025-10-21 12:05:00', '2025-10-21 12:05:30', '30s', '8.8.8.8: 5%'])
                writer.writerow(['FRITZ', 'WAN_RECONNECT', '2025-10-21 12:10:00', '2025-10-21 12:10:15', '15s', 'uptime reset'])
            
            # Run main with all outputs enabled
            with patch('sys.argv', [
                'visualize_incidents.py',
                '--input', input_path,
                '--output-dir', tmpdir,
                '--html'
            ]):
                visualize_incidents.main()
            
            # Verify timeline was created
            timeline_path = os.path.join(tmpdir, 'incidents_timeline.png')
            assert os.path.exists(timeline_path)
            
            # Verify summary was created
            summary_path = os.path.join(tmpdir, 'incidents_summary.png')
            assert os.path.exists(summary_path)
            
            # Verify HTML report was created
            html_path = os.path.join(tmpdir, 'incidents_report.html')
            assert os.path.exists(html_path)
            
            # Verify HTML content
            with open(html_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert 'LATENCY_SPIKE' in content
                assert 'LOSS_SPIKE' in content
                assert 'WAN_RECONNECT' in content


if __name__ == "__main__":
    # Allow running directly with: python3 test_visualize_incidents.py
    pytest.main([__file__, "-v"])
