#!/usr/bin/env python3
"""
Download HK 3D Pedestrian Network GeoJSON from CSDI and prepare for local routing.
Source: https://portal.csdi.gov.hk/geoportal/?datasetId=landsd_rcd_1637222018065_52265&lang=en
"""

import requests
import json
import os
from pathlib import Path

# The actual download URL for the pedestrian network dataset
# This is the REST API endpoint for the CSDI data
CSDI_API_URL = "https://data.gov.hk/api/1.0/datastore/query.json"
DATASET_ID = "landsd_rcd_1637222018065_52265"

# Alternative: Direct GeoJSON download from CSDI portal
# Try to fetch from the data.gov.hk open data portal
DATA_URL = "https://data.gov.hk/resource/landsd_rcd_1637222018065_52265"

def download_pedestrian_network():
    """Download the pedestrian network GeoJSON"""
    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / "hk_pedestrian_network.geojson"
    
    print("Attempting to download HK 3D Pedestrian Network...")
    
    # Try multiple URLs
    urls = [
        "https://data.gov.hk/resource/landsd_rcd_1637222018065_52265.geojson",
        "https://portal.csdi.gov.hk/geoportal/api/download?datasetId=landsd_rcd_1637222018065_52265",
        f"{CSDI_API_URL}?resource_id={DATASET_ID}",
    ]
    
    for url in urls:
        try:
            print(f"Trying: {url}")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Check if response is valid GeoJSON
            data = response.json()
            
            if isinstance(data, dict) and ('type' in data or 'data' in data):
                # Save to file
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f)
                print(f"✓ Successfully downloaded to {output_file}")
                return output_file
        except Exception as e:
            print(f"✗ Failed: {e}")
            continue
    
    print("\nNote: If download fails, manually download from:")
    print("https://portal.csdi.gov.hk/geoportal/?datasetId=landsd_rcd_1637222018065_52265&lang=en")
    print(f"And save to: {output_file}")
    return None

if __name__ == "__main__":
    download_pedestrian_network()
