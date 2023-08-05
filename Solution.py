import os
import zipfile
import numpy as np
import pandas as pd
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2
from flask import Flask, request, jsonify, send_file
import csv

app = Flask(__name__)

def unzip_and_read_files(zip_path):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall('unzipped_data')
        
    trail_data = {}
    for filename in os.listdir('unzipped_data/EOL-dump'):
        if filename.endswith(".csv"):
            df = pd.read_csv(os.path.join('unzipped_data/EOL-dump', filename))
            trail_data[filename] = df
    return trail_data

def read_trip_info(trip_csv):
    trip_df = pd.read_csv(trip_csv)
    return trip_df

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  
    
    lat1_rad = np.radians(lat1) 
    lon1_rad = np.radians(lon1)
    lat2_rad = np.radians(lat2)
    lon2_rad = np.radians(lon2)
    
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    
    a = np.sin(dlat / 2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    
    distance = R * c
    return distance

def generate_asset_report(start_time, end_time, trail_data, trip_df):
    asset_report = []
    

    for filename, df in trail_data.items():
        total_distance = 0
        total_speed_violations = 0
        start_ts = pd.Timestamp(start_time, unit='s')
        end_ts = pd.Timestamp(end_time, unit='s')

        df['tis'] = pd.to_datetime(df['tis'], unit='s')
        
        df = df[(df['tis'] >= start_ts ) & (df['tis'] <= end_ts )]

        for i in range(len(df.index)-1):
            lat1, lon1 = df['lat'].iloc[i], df['lon'].iloc[i]
            lat2, lon2 = df['lat'].iloc[i + 1], df['lon'].iloc[i + 1]
            distance = haversine_distance(lat1, lon1, lat2, lon2)
            total_distance += distance
        if df.empty:
            continue
        lic_plate_no = df['lic_plate_no'].iloc[0]

        trip_info = trip_df[trip_df['vehicle_number'] == lic_plate_no]

        if not trip_info.empty:
            transporter_name = trip_info['transporter_name'].values[0]
            num_trips_completed = len(trip_info.index)
        else:
            transporter_name = "N/A"
            num_trips_completed = 0
        print(f"index length: {len(df.index)}")

        

        total_speed_violations = df['osf'].sum()
        average_speed = df['spd'].mean()
        print(total_distance,total_speed_violations)

        asset_report.append({
            'License plate number': lic_plate_no,
            'Distance': total_distance,
            'Number of Trips Completed': num_trips_completed,
            'Average Speed': average_speed,
            'Transporter Name': transporter_name,
            'Number of Speed Violations': total_speed_violations
        })

    return asset_report

def generate_csv_report(data):
    output_path = 'Asset_Report.csv'
    with open(output_path, 'w', newline='') as csvfile:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for row in data:
            writer.writerow(row)

    return output_path

@app.route('/generate_report', methods=['POST'])
def generate_report():
    try:
        start_time = request.json['start_time']
        end_time = request.json['end_time']
        print(start_time,end_time)
        trail_data = unzip_and_read_files('NU-raw-location-dump.zip')
        trip_df = read_trip_info('Trip-Info.csv')
        asset_report = generate_asset_report(start_time, end_time, trail_data, trip_df)
        csv_path = generate_csv_report(asset_report)
        
        return send_file(csv_path, as_attachment=True)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)