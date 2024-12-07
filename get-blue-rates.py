#!/usr/bin/env python3

# Copyright (C) 2024 Felipe Tappata
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import requests
import sys
from datetime import datetime, timedelta
from statistics import mean, median, stdev
import time

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)

def calculate_stats(rates):
    values = [rate for _, rate in rates]
    return {
        'min': min(values),
        'max': max(values),
        'mean': mean(values),
        'median': median(values),
        'sd': stdev(values),
        'count': len(values)
    }

def find_missing_dates(rates, start_date, end_date):
    rate_dates = {datetime.strptime(date, '%Y-%m-%d').date() for date, _ in rates}
    all_dates = {d.date() for d in daterange(start_date, end_date)}
    return sorted(all_dates - rate_dates)

def get_rates(days):
    url = f"https://api.bluelytics.com.ar/v2/evolution.json?days={days*2}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error fetching data: {response.status_code}")
        return None
    return response.json()

def format_rate(date, rate):
    # Convert rate from ARS/USD to USD/ARS for hledger
    usd_per_ars = 1 / rate
    return f"P {date} ARS {usd_per_ars:.10f} USD ; USD {rate:.2f} ARS\n"

def main():
    start_time = time.time()
    
    if len(sys.argv) != 2:
        print("Usage: python get-blue-rates.py YYYY-MM-DD")
        sys.exit(1)

    try:
        start_date = datetime.strptime(sys.argv[1], "%Y-%m-%d")
    except ValueError:
        print("Invalid date format. Use YYYY-MM-DD")
        sys.exit(1)

    end_date = datetime.now()
    days = (end_date - start_date).days
    if days < 0:
        print("Start date must be in the past")
        sys.exit(1)

    print(f"Fetching data from {start_date.date()} to {end_date.date()}...")
    data = get_rates(days)
    if not data:
        sys.exit(1)

    # Filter blue rates only and sort by date
    blue_rates = [(item["date"], (item["value_sell"] + item["value_buy"]) / 2)
                 for item in data 
                 if item["source"] == "Blue"]
    blue_rates.sort()
    
    # Filter rates from start_date
    blue_rates = [(date, rate) for date, rate in blue_rates 
                 if datetime.strptime(date, '%Y-%m-%d') >= start_date]

    # Calculate statistics
    stats = calculate_stats(blue_rates)
    missing_dates = find_missing_dates(blue_rates, start_date, end_date)
    execution_time = time.time() - start_time

    # Print report
    print("\nData Retrieval Report:")
    print(f"Time elapsed: {execution_time:.2f} seconds")
    print(f"Date range: {start_date.date()} to {end_date.date()}")
    print(f"Total rates found: {stats['count']}")
    print("\nRate statistics (ARS/USD):")
    print(f"  Min:    {stats['min']:>8.2f}")
    print(f"  Max:    {stats['max']:>8.2f}")
    print(f"  Mean:   {stats['mean']:>8.2f}")
    print(f"  Median: {stats['median']:>8.2f}")
    print(f"  SD:     {stats['sd']:>8.2f}")
    
    print(f"\nMissing dates: {len(missing_dates)}")
    if len(missing_dates) <= 10 and len(missing_dates) > 0:
        print("Missing dates list:")
        for date in missing_dates:
            print(f"  {date}")

    # Write rates to file with metadata
    filename = "blue-rates.journal"
    with open(filename, "w") as f:
        f.write("; Blue Dollar rates retrieved by hledger-dollar\n")
        f.write(f"; Retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("; Source: https://api.bluelytics.com.ar/v2/evolution.json\n")
        f.write(f"; Date range: {start_date.date()} to {end_date.date()}\n")
        f.write(f"; Total rates: {stats['count']}\n")
        f.write(f"; Missing dates: {len(missing_dates)}\n")
        f.write(f"; Rate statistics (ARS/USD): Min: {stats['min']:.2f}, Max: {stats['max']:.2f}, Mean: {stats['mean']:.2f}, Median: {stats['median']:.2f}, SD: {stats['sd']:.2f}\n")
        f.write("\n")
        for date, rate in blue_rates:
            f.write(format_rate(date, rate))

if __name__ == "__main__":
    main()
