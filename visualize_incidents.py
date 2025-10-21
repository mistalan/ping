#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Visualize network incidents from incidents.csv with interactive charts.
Generates timeline plots, summary charts, and optionally an HTML report.
"""

import argparse
import csv
import sys
import os
from datetime import datetime
from collections import Counter

try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.patches import Rectangle
except ImportError:
    print("ERROR: matplotlib is required. Install with: pip install matplotlib")
    sys.exit(1)

TIME_FMT = "%Y-%m-%d %H:%M:%S"

def parse_time(s):
    """Parse timestamp string to datetime object."""
    try:
        return datetime.strptime(s, TIME_FMT)
    except Exception:
        return None

def load_incidents(csv_path):
    """Load incidents from CSV file."""
    incidents = []
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('start'):
                    row['start'] = parse_time(row['start'])
                if row.get('end'):
                    row['end'] = parse_time(row['end'])
                if row['start'] and row['end']:
                    incidents.append(row)
    except FileNotFoundError:
        print(f"ERROR: File not found: {csv_path}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to load incidents: {e}")
        sys.exit(1)
    
    return incidents

def create_timeline_plot(incidents, output_path):
    """Create a timeline visualization of incidents."""
    if not incidents:
        print("No incidents to plot.")
        return
    
    # Group incidents by type
    incident_types = sorted(set(inc['type'] for inc in incidents))
    type_to_y = {t: i for i, t in enumerate(incident_types)}
    
    # Color map for different incident types
    colors = plt.cm.tab20(range(len(incident_types)))
    type_colors = {t: colors[i] for i, t in enumerate(incident_types)}
    
    fig, ax = plt.subplots(figsize=(14, max(8, len(incident_types) * 0.5)))
    
    # Plot each incident as a horizontal bar
    for inc in incidents:
        y = type_to_y[inc['type']]
        start = inc['start']
        end = inc['end']
        duration = (end - start).total_seconds() / 60  # minutes
        
        # Draw the incident bar
        ax.barh(y, duration / 60, left=mdates.date2num(start), 
                height=0.6, color=type_colors[inc['type']], 
                alpha=0.7, edgecolor='black', linewidth=0.5)
    
    # Format the plot
    ax.set_yticks(range(len(incident_types)))
    ax.set_yticklabels(incident_types)
    ax.set_xlabel('Time', fontsize=12)
    ax.set_ylabel('Incident Type', fontsize=12)
    ax.set_title('Network Incidents Timeline', fontsize=14, fontweight='bold')
    
    # Format x-axis as dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.xticks(rotation=45, ha='right')
    
    # Add grid
    ax.grid(True, axis='x', alpha=0.3, linestyle='--')
    
    # Add source legend
    sources = sorted(set(inc['source'] for inc in incidents))
    legend_elements = [Rectangle((0, 0), 1, 1, fc=type_colors[t], alpha=0.7, edgecolor='black', linewidth=0.5, label=t) 
                      for t in incident_types]
    ax.legend(handles=legend_elements[:10], loc='upper left', bbox_to_anchor=(1.01, 1), 
              fontsize=9, title='Incident Types')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Timeline plot saved to: {output_path}")

def create_summary_charts(incidents, output_dir):
    """Create summary charts: pie chart and bar chart."""
    if not incidents:
        print("No incidents to summarize.")
        return
    
    # Count incidents by type
    type_counts = Counter(inc['type'] for inc in incidents)
    source_counts = Counter(inc['source'] for inc in incidents)
    
    # Create a figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Pie chart for incident types
    if type_counts:
        colors = plt.cm.tab20(range(len(type_counts)))
        wedges, texts, autotexts = ax1.pie(type_counts.values(), labels=type_counts.keys(),
                                            autopct='%1.1f%%', startangle=90, colors=colors)
        for text in texts:
            text.set_fontsize(9)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(9)
        ax1.set_title('Incidents by Type', fontsize=12, fontweight='bold')
    
    # Bar chart for incident sources
    if source_counts:
        sources = list(source_counts.keys())
        counts = list(source_counts.values())
        bars = ax2.bar(sources, counts, color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
        ax2.set_xlabel('Source', fontsize=11)
        ax2.set_ylabel('Count', fontsize=11)
        ax2.set_title('Incidents by Source', fontsize=12, fontweight='bold')
        
        # Add count labels on bars
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width() / 2., height,
                    f'{int(height)}', ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, 'incidents_summary.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Summary charts saved to: {output_path}")

def create_html_report(incidents, output_path):
    """Create an interactive HTML report."""
    if not incidents:
        print("No incidents to report.")
        return
    
    # Count statistics
    total = len(incidents)
    type_counts = Counter(inc['type'] for inc in incidents)
    source_counts = Counter(inc['source'] for inc in incidents)
    
    # Get time range
    start_times = [inc['start'] for inc in incidents if inc['start']]
    end_times = [inc['end'] for inc in incidents if inc['end']]
    time_range = ""
    if start_times and end_times:
        earliest = min(start_times)
        latest = max(end_times)
        time_range = f"{earliest.strftime(TIME_FMT)} to {latest.strftime(TIME_FMT)}"
    
    # Generate HTML
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Network Incidents Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #555;
            margin-top: 30px;
        }}
        .summary {{
            background-color: #e8f5e9;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        .summary-item {{
            background-color: white;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .summary-item .number {{
            font-size: 32px;
            font-weight: bold;
            color: #4CAF50;
        }}
        .summary-item .label {{
            color: #666;
            font-size: 14px;
            margin-top: 5px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #4CAF50;
            color: white;
            font-weight: bold;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .incident-type {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 3px;
            font-size: 12px;
            font-weight: bold;
        }}
        .type-PC {{ background-color: #FF6B6B; color: white; }}
        .type-FRITZ {{ background-color: #4ECDC4; color: white; }}
        .charts {{
            margin: 30px 0;
            text-align: center;
        }}
        .charts img {{
            max-width: 100%;
            height: auto;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 5px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Network Incidents Report</h1>
        <div class="summary">
            <strong>Analysis Period:</strong> {time_range}
            <div class="summary-grid">
                <div class="summary-item">
                    <div class="number">{total}</div>
                    <div class="label">Total Incidents</div>
                </div>
"""
    
    # Add summary items for each source
    for source, count in source_counts.items():
        html += f"""                <div class="summary-item">
                    <div class="number">{count}</div>
                    <div class="label">{source} Incidents</div>
                </div>
"""
    
    html += """            </div>
        </div>
        
        <h2>Incident Type Distribution</h2>
        <table>
            <tr>
                <th>Type</th>
                <th>Count</th>
                <th>Percentage</th>
            </tr>
"""
    
    # Add type distribution rows
    for inc_type, count in type_counts.most_common():
        percentage = (count / total) * 100
        html += f"""            <tr>
                <td>{inc_type}</td>
                <td>{count}</td>
                <td>{percentage:.1f}%</td>
            </tr>
"""
    
    html += """        </table>
        
        <h2>Visualizations</h2>
        <div class="charts">
"""
    
    # Reference images if they exist
    timeline_path = os.path.join(os.path.dirname(output_path), 'incidents_timeline.png')
    summary_path = os.path.join(os.path.dirname(output_path), 'incidents_summary.png')
    
    if os.path.exists(timeline_path):
        html += f"""            <h3>Timeline</h3>
            <img src="{os.path.basename(timeline_path)}" alt="Incidents Timeline">
"""
    
    if os.path.exists(summary_path):
        html += f"""            <h3>Summary</h3>
            <img src="{os.path.basename(summary_path)}" alt="Incidents Summary">
"""
    
    html += """        </div>
        
        <h2>Detailed Incidents</h2>
        <table>
            <tr>
                <th>Source</th>
                <th>Type</th>
                <th>Start</th>
                <th>End</th>
                <th>Duration</th>
                <th>Details</th>
            </tr>
"""
    
    # Add incident rows
    for inc in sorted(incidents, key=lambda x: x['start']):
        source_class = f"type-{inc['source']}"
        html += f"""            <tr>
                <td><span class="incident-type {source_class}">{inc['source']}</span></td>
                <td>{inc['type']}</td>
                <td>{inc['start'].strftime(TIME_FMT)}</td>
                <td>{inc['end'].strftime(TIME_FMT)}</td>
                <td>{inc.get('duration', '')}</td>
                <td>{inc.get('details', '')}</td>
            </tr>
"""
    
    html += """        </table>
    </div>
</body>
</html>
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"HTML report saved to: {output_path}")

def main():
    parser = argparse.ArgumentParser(
        description='Visualize network incidents from incidents.csv',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--input', '-i', required=True,
                       help='Path to incidents.csv file')
    parser.add_argument('--output-dir', '-o', default='.',
                       help='Output directory for visualizations (default: current directory)')
    parser.add_argument('--html', action='store_true',
                       help='Generate HTML report')
    parser.add_argument('--no-timeline', action='store_true',
                       help='Skip timeline plot generation')
    parser.add_argument('--no-summary', action='store_true',
                       help='Skip summary charts generation')
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Load incidents
    print(f"Loading incidents from: {args.input}")
    incidents = load_incidents(args.input)
    
    if not incidents:
        print("No valid incidents found in the CSV file.")
        sys.exit(1)
    
    print(f"Loaded {len(incidents)} incidents")
    
    # Generate visualizations
    if not args.no_timeline:
        timeline_path = os.path.join(args.output_dir, 'incidents_timeline.png')
        create_timeline_plot(incidents, timeline_path)
    
    if not args.no_summary:
        create_summary_charts(incidents, args.output_dir)
    
    if args.html:
        html_path = os.path.join(args.output_dir, 'incidents_report.html')
        create_html_report(incidents, html_path)
    
    print(f"\nVisualization complete! Files saved to: {os.path.abspath(args.output_dir)}")
    
    # Print summary statistics
    print("\n=== Summary ===")
    print(f"Total incidents: {len(incidents)}")
    type_counts = Counter(inc['type'] for inc in incidents)
    print("\nIncidents by type:")
    for inc_type, count in type_counts.most_common():
        print(f"  {inc_type}: {count}")
    
    source_counts = Counter(inc['source'] for inc in incidents)
    print("\nIncidents by source:")
    for source, count in source_counts.most_common():
        print(f"  {source}: {count}")

if __name__ == '__main__':
    main()
