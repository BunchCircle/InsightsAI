import os
import time
from datetime import datetime, timedelta
import json
from pathlib import Path

CHARTS_DIR = "images/plotly_figures/html"
METADATA_FILE = "images/plotly_figures/metadata.json"
DEFAULT_TTL_HOURS = 0.1  # Time to live in hours

def ensure_dirs():
    """Ensure necessary directories exist"""
    os.makedirs(CHARTS_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(METADATA_FILE), exist_ok=True)

def load_metadata():
    """Load chart metadata from file"""
    if not os.path.exists(METADATA_FILE):
        return {}
    try:
        with open(METADATA_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_metadata(metadata):
    """Save chart metadata to file"""
    with open(METADATA_FILE, 'w') as f:
        json.dump(metadata, f)

def record_chart_creation(filename):
    """Record when a chart is created"""
    metadata = load_metadata()
    metadata[filename] = {
        'created_at': datetime.now().isoformat(),
        'last_accessed': datetime.now().isoformat()
    }
    save_metadata(metadata)

def record_chart_access(filename):
    """Record when a chart is accessed"""
    metadata = load_metadata()
    if filename in metadata:
        metadata[filename]['last_accessed'] = datetime.now().isoformat()
        save_metadata(metadata)

def cleanup_old_charts(ttl_hours=DEFAULT_TTL_HOURS):
    """Remove charts that haven't been accessed in ttl_hours"""
    ensure_dirs()
    metadata = load_metadata()
    current_time = datetime.now()
    files_to_delete = []
    updated_metadata = {}

    # Identify files to delete
    for filename, data in metadata.items():
        try:
            last_accessed = datetime.fromisoformat(data['last_accessed'])
            if current_time - last_accessed > timedelta(hours=ttl_hours):
                file_path = os.path.join(CHARTS_DIR, filename)
                if os.path.exists(file_path):
                    files_to_delete.append(file_path)
            else:
                updated_metadata[filename] = data
        except:
            # If there's any error parsing dates, consider the file for deletion
            file_path = os.path.join(CHARTS_DIR, filename)
            if os.path.exists(file_path):
                files_to_delete.append(file_path)

    # Delete files
    for file_path in files_to_delete:
        try:
            os.remove(file_path)
        except:
            pass  # Ignore errors during deletion

    # Update metadata file
    save_metadata(updated_metadata)

    return len(files_to_delete)

def cleanup_orphaned_files():
    """Remove any files that don't have metadata entries"""
    metadata = load_metadata()
    known_files = set(metadata.keys())
    
    actual_files = set(os.listdir(CHARTS_DIR))
    orphaned_files = actual_files - known_files

    for filename in orphaned_files:
        try:
            os.remove(os.path.join(CHARTS_DIR, filename))
        except:
            pass  # Ignore errors during deletion

    return len(orphaned_files)
