# Enhanced Streamlit Dashboard with Modal Deployment & Supabase Integration

This project provides an enhanced Streamlit dashboard for NYC Uber pickups data with additional visualizations, interactivity, and Supabase database integration, deployable on Modal.

## 🚀 Features

### Dashboard Enhancements
- **Interactive Plotly Charts**: Enhanced visualizations with better interactivity
- **Day of Week Analysis**: Pie chart showing pickup distribution by day
- **Pickup Density Heatmap**: Hour vs Day of Week patterns
- **Enhanced Controls**: Date range selector, sample size control
- **Data Export**: Download filtered data as CSV
- **Real-time Statistics**: Key metrics display

### Supabase Integration
- **Database Connection**: Read data from Supabase tables
- **Dynamic Visualizations**: Generate charts from your database data
- **Data Preview**: Display and explore your Supabase data
- **Flexible Queries**: Choose tables and columns dynamically

## 📁 Project Structure

```
DTSC_Project/
├── streamlit_run.py          # Local Streamlit app with enhanced features
├── streamlit_modal.py        # Modal deployment configuration
├── .env.example             # Environment variables template
├── pyproject.toml           # Project dependencies
└── README.md               # This file
```

## 🛠️ Setup Instructions

### Part 1: Local Development

1. **Clone and Setup Environment**
   ```bash
   cd /path/to/your/project
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install Dependencies**
   ```bash
   pip install streamlit pandas plotly supabase modal python-dotenv
   ```

3. **Configure Environment Variables (Optional)**
   ```bash
   cp .env.example .env
   # Edit .env file with your Supabase credentials
   ```

4. **Run Locally**
   ```bash
   streamlit run streamlit_run.py
   ```
   
   The app will be available at: `http://localhost:8501`

### Part 2: Modal Deployment

1. **Install and Setup Modal CLI**
   ```bash
   pip install modal
   modal setup
   modal set token
   ```

2. **Deploy to Modal**
   ```bash
   modal deploy streamlit_modal.py
   ```

3. **Access Your Deployed App**
   - Log into your Modal dashboard
   - Find your app and copy the public URL

### Part 3: Supabase Integration

1. **Create Supabase Secrets in Modal Dashboard**
   - Go to Modal Dashboard → Secrets → Create new secret
   - Name it `my-secret`
   - Add key/value pairs:
     - `SUPABASE_URL` = your Supabase URL
     - `SUPABASE_KEY` = your Supabase anon key

2. **For Local Development**
   - Create a `.env` file from `.env.example`
   - Add your Supabase credentials
   - The app will automatically detect and use them

## 🎯 Dashboard Features

### Original Uber Data Analysis
- **Interactive Map**: Filter pickups by hour with slider
- **Hourly Distribution**: Bar chart of pickups by hour
- **Raw Data View**: Toggle to show/hide raw data

### Enhanced Features
- **📈 Interactive Plotly Histogram**: Color-coded hourly distribution
- **📅 Day of Week Pie Chart**: Pickup patterns across the week
- **🗺️ Density Heatmap**: Hour vs Day of Week pickup patterns
- **📊 Real-time Statistics**: Total pickups, peak hour, averages
- **🔍 Data Explorer**: Interactive column selection and filtering
- **📥 Data Export**: Download filtered datasets

### Supabase Integration
- **🗄️ Database Toggle**: Switch between Uber data and Supabase data
- **📊 Dynamic Tables**: Connect to any Supabase table
- **📈 Auto-Visualizations**: Generate charts from your data
- **📋 Data Preview**: Browse your database records
- **📊 Column Analysis**: Automatic numeric and categorical analysis

## 🎮 Interactive Controls

### Sidebar Controls
- **Date Range Picker**: Filter data by date range
- **Sample Size Selector**: Adjust visualization performance
- **Database Options**: Toggle Supabase integration
- **Table Selection**: Choose Supabase tables dynamically

### Main Dashboard
- **Hour Slider**: Filter map by specific hours
- **Column Selector**: Choose data columns to display
- **Chart Interactions**: Zoom, pan, and hover on all charts

## 🔧 Configuration

### Environment Variables
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here
```

### Modal Configuration
The `streamlit_modal.py` file is configured with:
- **Secrets Management**: Automatic Supabase credential handling
- **Package Installation**: All required dependencies
- **Proper Port Configuration**: Streamlit server setup
- **Environment Variables**: Secure credential passing

## 🚨 SSL Fix
If you encounter SSL errors, the app automatically includes this fix:
```python
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
```

## 📊 Sample Supabase Schema

For testing, you can create a simple table in Supabase:
```sql
CREATE TABLE movies (
  id SERIAL PRIMARY KEY,
  title TEXT,
  year INTEGER,
  rating DECIMAL,
  genre TEXT
);

INSERT INTO movies (title, year, rating, genre) VALUES
('The Matrix', 1999, 8.7, 'Sci-Fi'),
('Inception', 2010, 8.8, 'Sci-Fi'),
('The Godfather', 1972, 9.2, 'Crime');
```

## 🔄 Deployment Commands

```bash
# Local development
streamlit run streamlit_run.py

# Modal deployment
modal deploy streamlit_modal.py

# Modal CLI setup
modal setup
modal set token
```

## 🎨 Customization

The dashboard is highly customizable:
- **Add New Charts**: Modify `streamlit_run.py` to include additional visualizations
- **Database Tables**: Connect to different Supabase tables
- **Styling**: Customize colors and themes in Plotly charts
- **Data Sources**: Add new data sources beyond Uber and Supabase

## 🔍 Troubleshooting

### Common Issues
1. **Import Errors**: Ensure all packages are installed in your virtual environment
2. **Supabase Connection**: Verify your credentials and table names
3. **Modal Deployment**: Check that secrets are properly configured in Modal dashboard
4. **SSL Errors**: The app includes automatic SSL fixes

### Performance Optimization
- Use the sample size selector for large datasets
- Enable date range filtering to reduce data load
- Consider pagination for very large Supabase tables

## 📈 Next Steps

Potential enhancements:
- **Real-time Data**: Connect to streaming data sources
- **User Authentication**: Add login functionality
- **Advanced Analytics**: Machine learning predictions
- **Multi-tenancy**: Support multiple databases/schemas
- **Caching**: Implement Redis for better performance

## 🎯 Success Criteria

✅ **Local Setup**: Enhanced Streamlit dashboard running locally  
✅ **Extended Features**: 2+ new charts with interactivity  
✅ **Modal Deployment**: App deployed and accessible via public URL  
✅ **Supabase Integration**: Database connection with data visualization  
✅ **Secrets Management**: Secure credential handling in Modal  

Your enhanced dashboard is now ready for both local development and cloud deployment! 🚀
