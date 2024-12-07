# hledger-blue-rates

A Python script that generates [hledger](https://hledger.org/) compatible price directives for the Argentine “Blue Dollar” (black market exchange rate) based on the average between “buy” and “sell” prices listed by the [Bluelytics](https://github.com/Bluelytics) API.
The script was created to automate my own personal workflow, and so is rather rudimentary and lacks extensibility, but suggestions and improvements are welcome.

## Installation

1. Clone this repository:

```
git clone https://github.com/felipetappata/hledger-blue-rates.git
```

2. Navigate to the project directory:

```
cd hledger-blue-rates
```

3. Install the required dependencies:

```
pip install -r requirements.txt
```

## Usage

Call from the terminal with the following command:

```
python get-blue-rates.py YYYY-MM-DD
```

Where `YYYY-MM-DD` is the date from which you want to start generating price directives.
The script will generate a file called `blue-rates.journal` containing price directives from the specified date to the current date.
The generated file can be included in your hledger journal file using the `include` directive:

```
!include blue-rates.journal
```

It assumes that amounts denominated in dollars are in the `USD` currency and amounts denominated in Argentine Pesos are in the `ARS` currency.

## Requirements

- Python 3.6 or later
- `requests` library

## Example Output

```
; Blue Dollar rates retrieved by hledger-blue-rates
; Retrieved on: 2024-12-07 07:55:21
; Source: https://api.bluelytics.com.ar/v2/evolution.json
; Date range: 2007-01-01 to 2024-12-07
; Total rates: 4173
; Missing dates: 2378
; Rate statistics (ARS/USD): Min: 4.00, Max: 1500.00, Mean: 156.24, Median: 18.00, SD: 307.13

P 2011-01-03 ARS 0.2500000000 USD ; USD 4.00 ARS
P 2011-01-04 ARS 0.2500000000 USD ; USD 4.00 ARS
P 2011-01-05 ARS 0.2500000000 USD ; USD 4.00 ARS
P 2011-01-06 ARS 0.2500000000 USD ; USD 4.00 ARS
```

## Credits

This tool relies on the [Bluelytics](https://github.com/Bluelytics) API created by Pablo Seibelt. The API provides Argentine Blue Dollar exchange rate data and is available under the GNU Affero General Public License v3.0 (AGPL-3.0).

## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0) to maintain compatibility with the Bluelytics API license. See the LICENSE file for details.
