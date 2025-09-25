# ---
# lambda-test: false  # auxiliary-file
# ---
# ## Demo Streamlit application.
#
# This application is the example from https://docs.streamlit.io/library/get-started/create-an-app.
#
# Streamlit is designed to run its apps as Python scripts, not functions, so we separate the Streamlit
# code into this module, away from the Modal application code.

def main():
    import numpy as np
    import pandas as pd
    import streamlit as st
    import plotly.express as px
    import plotly.graph_objects as go
    from datetime import datetime
    import os

    st.title("🚗 Enhanced NYC Uber Pickups Dashboard")
    
    # Add SSL fix if needed
    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context

    # ==================== SUPABASE INTEGRATION ====================
    st.sidebar.header("🗄️ Database Options")
    
    # Check if Supabase credentials are available
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if supabase_url and supabase_key:
        try:
            from supabase import create_client, Client
            
            # Create Supabase client
            supabase: Client = create_client(supabase_url, supabase_key)
            
            use_supabase = st.sidebar.checkbox("📊 Use Supabase Data", help="Toggle to switch between Uber data and Supabase data")
            
            if use_supabase:
                st.sidebar.info("🔗 Connected to Supabase!")
                
                # Table selector
                table_name = st.sidebar.text_input("Table name:", value="movies", help="Enter the name of your Supabase table")
                
                if table_name:
                    try:
                        # Fetch data from Supabase
                        response = supabase.table(table_name).select("*").limit(1000).execute()
                        
                        if response.data:
                            supabase_df = pd.DataFrame(response.data)
                            
                            st.subheader(f"📊 Data from Supabase Table: {table_name}")
                            st.info(f"Retrieved {len(supabase_df)} records from {table_name}")
                            
                            # Display data table
                            st.subheader("📋 Data Preview")
                            st.dataframe(supabase_df.head(20), use_container_width=True)
                            
                            # Basic statistics
                            st.subheader("📈 Data Statistics")
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Total Records", len(supabase_df))
                            with col2:
                                st.metric("Columns", len(supabase_df.columns))
                            with col3:
                                st.metric("Data Types", len(supabase_df.dtypes.unique()))
                            
                            # Column analysis
                            st.subheader("📊 Column Analysis")
                            
                            # Select numeric columns for visualization
                            numeric_cols = supabase_df.select_dtypes(include=[np.number]).columns.tolist()
                            categorical_cols = supabase_df.select_dtypes(include=['object']).columns.tolist()
                            
                            if numeric_cols:
                                st.write("**Numeric Columns:**")
                                selected_numeric = st.selectbox("Select numeric column for histogram:", numeric_cols)
                                
                                if selected_numeric:
                                    fig_numeric = px.histogram(
                                        supabase_df, 
                                        x=selected_numeric,
                                        title=f"Distribution of {selected_numeric}",
                                        color_discrete_sequence=['#636EFA']
                                    )
                                    st.plotly_chart(fig_numeric, use_container_width=True)
                            
                            if categorical_cols:
                                st.write("**Categorical Columns:**")
                                selected_categorical = st.selectbox("Select categorical column for pie chart:", categorical_cols)
                                
                                if selected_categorical:
                                    # Get value counts
                                    value_counts = supabase_df[selected_categorical].value_counts().head(10)
                                    
                                    fig_categorical = px.pie(
                                        values=value_counts.values,
                                        names=value_counts.index,
                                        title=f"Distribution of {selected_categorical}",
                                    )
                                    st.plotly_chart(fig_categorical, use_container_width=True)
                            
                            # Download Supabase data
                            csv_supabase = supabase_df.to_csv(index=False)
                            st.download_button(
                                label=f"📥 Download {table_name} data as CSV",
                                data=csv_supabase,
                                file_name=f'{table_name}_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                                mime='text/csv'
                            )
                            
                            return  # Exit early to show only Supabase data
                        else:
                            st.sidebar.warning(f"No data found in table '{table_name}'")
                    
                    except Exception as e:
                        st.sidebar.error(f"Error fetching data from {table_name}: {str(e)}")
        
        except ImportError:
            st.sidebar.warning("Supabase package not available. Install with: pip install supabase")
        except Exception as e:
            st.sidebar.error(f"Supabase connection error: {str(e)}")
    else:
        st.sidebar.info("ℹ️ Set SUPABASE_URL and SUPABASE_KEY environment variables to enable database features")

    # ==================== ORIGINAL UBER DATA ANALYSIS ====================
    st.subheader("🚕 NYC Uber Pickups Analysis")
    
    DATE_COLUMN = "date/time"
    DATA_URL = (
        "https://s3-us-west-2.amazonaws.com/"
        "streamlit-demo-data/uber-raw-data-sep14.csv.gz"
    )

    @st.cache_data
    def load_data(nrows):
        data = pd.read_csv(DATA_URL, nrows=nrows)

        def lowercase(x):
            return str(x).lower()

        data.rename(lowercase, axis="columns", inplace=True)
        data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
        return data

    data_load_state = st.text("Loading data...")
    data = load_data(10000)
    data_load_state.text("Done! (using st.cache_data)")

    if st.checkbox("Show raw data"):
        st.subheader("Raw data")
        st.write(data)

    st.subheader("Number of pickups by hour")
    hist_values = np.histogram(data[DATE_COLUMN].dt.hour, bins=24, range=(0, 24))[0]
    st.bar_chart(hist_values)

    # Some number in the range 0-23
    hour_to_filter = st.slider("hour", 0, 23, 17)
    filtered_data = data[data[DATE_COLUMN].dt.hour == hour_to_filter]

    st.subheader("Map of all pickups at %s:00" % hour_to_filter)
    st.map(filtered_data)

    # ==================== NEW ENHANCED FEATURES ====================
    
    # Sidebar for additional controls
    st.sidebar.header("📊 Dashboard Controls")
    st.sidebar.markdown("---")
    
    # Interactive date range selector
    st.sidebar.subheader("Date Range Filter")
    min_date = data[DATE_COLUMN].min().date()
    max_date = data[DATE_COLUMN].max().date()
    
    date_range = st.sidebar.date_input(
        "Select date range:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Filter data by date range
    if len(date_range) == 2:
        start_date, end_date = date_range
        mask = (data[DATE_COLUMN].dt.date >= start_date) & (data[DATE_COLUMN].dt.date <= end_date)
        filtered_date_data = data.loc[mask]
    else:
        filtered_date_data = data
    
    # Sample size selector
    sample_size = st.sidebar.selectbox(
        "Select sample size for visualizations:",
        [1000, 5000, 10000, len(filtered_date_data)],
        index=2
    )
    
    # Sample the data
    if sample_size < len(filtered_date_data):
        display_data = filtered_date_data.sample(n=sample_size, random_state=42)
    else:
        display_data = filtered_date_data
    
    st.sidebar.info(f"Displaying {len(display_data)} out of {len(filtered_date_data)} total records")
    
    # ==================== NEW CHART 1: Interactive Plotly Histogram ====================
    st.subheader("📈 Interactive Hourly Pickup Distribution")
    
    # Create hourly distribution
    hourly_counts = display_data[DATE_COLUMN].dt.hour.value_counts().sort_index()
    
    fig_hist = px.bar(
        x=hourly_counts.index,
        y=hourly_counts.values,
        labels={'x': 'Hour of Day', 'y': 'Number of Pickups'},
        title="Uber Pickups by Hour (Interactive)",
        color=hourly_counts.values,
        color_continuous_scale='viridis'
    )
    fig_hist.update_layout(
        xaxis_title="Hour of Day",
        yaxis_title="Number of Pickups",
        showlegend=False
    )
    st.plotly_chart(fig_hist, use_container_width=True)
    
    # ==================== NEW CHART 2: Day of Week Analysis ====================
    st.subheader("📅 Pickups by Day of Week")
    
    # Add day of week column
    display_data_copy = display_data.copy()
    display_data_copy['day_of_week'] = display_data_copy[DATE_COLUMN].dt.day_name()
    display_data_copy['weekday_num'] = display_data_copy[DATE_COLUMN].dt.dayofweek
    
    # Group by day of week
    daily_counts = display_data_copy.groupby(['weekday_num', 'day_of_week']).size().reset_index(name='counts')
    daily_counts = daily_counts.sort_values('weekday_num')
    
    fig_daily = px.pie(
        daily_counts,
        values='counts',
        names='day_of_week',
        title="Distribution of Pickups by Day of Week",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_daily.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_daily, use_container_width=True)
    
    # ==================== NEW CHART 3: Heatmap of Pickups ====================
    st.subheader("🗺️ Pickup Density Heatmap")
    
    # Create hour vs day of week heatmap data
    display_data_copy['hour'] = display_data_copy[DATE_COLUMN].dt.hour
    heatmap_data = display_data_copy.groupby(['day_of_week', 'hour']).size().unstack(fill_value=0)
    
    # Reorder days
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    heatmap_data = heatmap_data.reindex(day_order)
    
    fig_heatmap = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale='Blues',
        text=heatmap_data.values,
        texttemplate="%{text}",
        textfont={"size":10},
    ))
    
    fig_heatmap.update_layout(
        title="Pickup Patterns: Hour vs Day of Week",
        xaxis_title="Hour of Day",
        yaxis_title="Day of Week",
        width=800,
        height=400
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # ==================== ENHANCED STATISTICS ====================
    st.subheader("📊 Dataset Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Pickups", f"{len(display_data):,}")
    
    with col2:
        peak_hour = display_data[DATE_COLUMN].dt.hour.mode()[0]
        st.metric("Peak Hour", f"{peak_hour}:00")
    
    with col3:
        avg_per_hour = len(display_data) / 24
        st.metric("Avg/Hour", f"{avg_per_hour:.0f}")
    
    with col4:
        date_span = (display_data[DATE_COLUMN].max() - display_data[DATE_COLUMN].min()).days
        st.metric("Date Span", f"{date_span} days")
    
    # ==================== INTERACTIVE DATA EXPLORATION ====================
    st.subheader("🔍 Interactive Data Explorer")
    
    # Multi-select for columns
    available_columns = ['lat', 'lon', DATE_COLUMN]
    selected_columns = st.multiselect(
        "Select columns to display:",
        available_columns,
        default=available_columns
    )
    
    if selected_columns:
        st.dataframe(
            display_data[selected_columns].head(100),
            use_container_width=True
        )
    
    # Download button for filtered data
    csv = display_data.to_csv(index=False)
    st.download_button(
        label="📥 Download filtered data as CSV",
        data=csv,
        file_name=f'uber_pickups_filtered_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
        mime='text/csv'
    )


if __name__ == "__main__":
    main()