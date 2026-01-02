# Copilot Instructions for Investment Dashboard

## Architecture Overview
This is a Streamlit-based investment portfolio dashboard with modular views. The app uses Google Sheets as the primary data store via `streamlit_gsheets` connection.

**Key Components:**
- `mydashboard.py`: Main app entry point with tabbed interface
- `views/`: Modular view components (Overview, US_stocks, Funds) each with a `show()` function
- `utils.py`: Shared utilities for portfolio history updates
- Data flows from Google Sheets worksheets: "rebalance", "Buying track", "Portfolio_Hx"

**Data Flow:**
- Load data with `@st.cache_data(ttl=600)` decorated functions
- Update portfolio history via `utils.update_portfolio_hx()`
- Display with Plotly charts and custom CSS styling

## Development Workflow
- **Run locally**: `streamlit run mydashboard.py`
- **Google Sheets setup**: Configure connection in Streamlit secrets with worksheet names
- **Caching**: Use `@st.cache_data(ttl=...)` for data loading (600s for market data, 30s for overview)
- **Error handling**: Wrap view calls in try/except blocks as seen in `mydashboard.py`

## Code Patterns
- **View modules**: Each in `views/` exports a `show()` function for tab content
- **Data loading**: Functions like `load_data()` return DataFrames from Google Sheets
- **Styling**: Custom CSS in `<style>` blocks for metric cards and asset items (see `views/Overview.py`)
- **Formatting**: Use `.style.format()` for DataFrame display with currency symbols
- **Thai language**: Include Thai comments and UI text for localization

## Dependencies & Integration
- **Google Sheets**: Primary data persistence via `st.connection("gsheets")`
- **yfinance**: Fetch benchmark prices (e.g., SPY for S&P 500 comparison)
- **Plotly**: Charts with `px` and `go` for interactive visualizations
- **Date handling**: Parse dates with `pd.to_datetime(df['Date'], format='%d/%m/%Y')`

## Conventions
- Skip rows when reading sheets: `conn.read(worksheet="name", skiprows=N)`
- Filter totals: `df[~df['column'].str.lower().str.contains('total')]`
- Metric display: Custom HTML cards instead of `st.metric()` for enhanced styling
- Background updates: Use `st.toast()` for user feedback during data operations