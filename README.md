# Options Guru - Professional Options Trading Analysis and Visualization Tool

Options Guru is a powerful Streamlit application designed for professional options trading analysis and visualization. It provides a comprehensive suite of tools to help you make informed decisions, including real-time market data, advanced options pricing models, and interactive visualizations.

## Features

- **Interactive Options Calculator:** Calculate option prices, Greeks, and other key metrics in real time.
- **Multiple Data Sources:** Choose from Yahoo Finance, Polygon.io, and Alpaca for market data.
- **Advanced Visualizations:** Explore 3D option surfaces, heatmaps, and strategy comparison charts.
- **Comprehensive Greeks Analysis:** Understand the risk and sensitivity of your options positions.
- **Strategy Comparison:** Compare different options strategies side by side to find the best fit for your market outlook.
- **Real-time Market Data:** Get a snapshot of the market with major indices and stock data.

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/kaljuvee/options-guru.git
   cd options-guru
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install the required packages:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your API keys:**
   Create a `.env` file in the root directory of the project and add your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   ALPACA_PAPER_API_KEY=your_alpaca_paper_api_key
   ALPACA_PAPER_SECRET_KEY=your_alpaca_paper_secret_key
   POLYGON_API_KEY=your_polygon_api_key
   ```

## Running the Application

To run the Options Guru application, use the following command:

```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501` in your web browser.

## Running Unit Tests

To run the unit tests, use the following command:

```bash
python -m pytest tests/
```

## Project Structure

```
options-guru/
├── app.py                  # Main Streamlit application
├── pages/                  # Additional Streamlit pages
│   └── 01_Advanced_Visualizations.py
├── utils/                  # Utility modules
│   ├── __init__.py
│   ├── alpaca_utils.py
│   ├── black_scholes.py
│   ├── data_provider.py
│   ├── polygon_utils.py
│   ├── visualization.py
│   └── yfinance_utils.py
├── data/                   # Directory for storing results
├── test-data/              # Directory for test data
│   ├── sample_market_data.csv
│   └── sample_options_data.csv
├── tests/                  # Unit tests
│   ├── test_black_scholes.py
│   └── test_data_providers.py
├── .env                    # API keys (create this file)
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue to discuss any changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.


