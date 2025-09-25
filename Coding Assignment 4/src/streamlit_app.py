"""
Streamlit Dashboard for WSJ Sentiment Analysis
Displays articles, sentiment analysis, and visualizations
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import sys

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__)))

try:
    from loader import SupabaseLoader, load_from_json_file
except ImportError:
    st.error("Could not import loader module. Make sure you're running from the correct directory.")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="WSJ Sentiment Analysis Dashboard",
    page_icon="�",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_data():
    """Load data from Supabase or fallback to JSON/CSV"""
    loader = SupabaseLoader()
    
    # Try to load from Supabase first
    if loader.supabase:
        try:
            articles = loader.query_recent_articles(limit=100)
            if articles:
                df = pd.DataFrame(articles)
                df['extracted_at'] = pd.to_datetime(df['extracted_at'])
                return df, "supabase"
        except Exception as e:
            st.warning(f"Could not load from Supabase: {e}")
    
    # Fallback to JSON file
    try:
        structured_data = load_from_json_file("data/structured_articles.json")
        if structured_data:
            df = loader.json_to_dataframe(structured_data)
            return df, "json"
    except Exception:
        pass
    
    # Fallback to CSV backup
    try:
        df = pd.read_csv("data/articles_backup.csv")
        df['extracted_at'] = pd.to_datetime(df['extracted_at'])
        return df, "csv"
    except Exception:
        pass
    
    return pd.DataFrame(), "none"

def create_sentiment_gauge(avg_sentiment_score):
    """Create a sentiment gauge visualization"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = avg_sentiment_score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Average Sentiment Score"},
        delta = {'reference': 0},
        gauge = {
            'axis': {'range': [-1, 1]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [-1, -0.5], 'color': "red"},
                {'range': [-0.5, 0], 'color': "orange"},
                {'range': [0, 0.5], 'color': "lightgreen"},
                {'range': [0.5, 1], 'color': "green"}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': 0
            }
        }
    ))
    
    fig.update_layout(height=300)
    return fig

def create_sentiment_distribution(df):
    """Create sentiment distribution chart"""
    sentiment_counts = df['sentiment'].value_counts()
    
    colors = {
        'very_positive': '#2E8B57',
        'positive': '#90EE90', 
        'neutral': '#FFD700',
        'negative': '#FFA500',
        'very_negative': '#FF4500'
    }
    
    fig = px.bar(
        x=sentiment_counts.index,
        y=sentiment_counts.values,
        color=sentiment_counts.index,
        color_discrete_map=colors,
        title="Sentiment Distribution",
        labels={'x': 'Sentiment', 'y': 'Number of Articles'}
    )
    
    fig.update_layout(showlegend=False)
    return fig

def create_market_impact_chart(df):
    """Create market impact distribution chart"""
    impact_counts = df['market_impact'].value_counts()
    
    colors = {
        'bullish': '#00FF00',
        'neutral': '#FFD700', 
        'bearish': '#FF0000',
        'mixed': '#FFA500'
    }
    
    fig = px.pie(
        values=impact_counts.values,
        names=impact_counts.index,
        title="Market Impact Distribution",
        color=impact_counts.index,
        color_discrete_map=colors
    )
    
    return fig

def create_sentiment_timeline(df):
    """Create sentiment over time chart"""
    if len(df) < 2:
        return None
    
    # Group by date and calculate average sentiment
    df['date'] = df['extracted_at'].dt.date
    daily_sentiment = df.groupby('date')['sentiment_score'].mean().reset_index()
    
    fig = px.line(
        daily_sentiment,
        x='date',
        y='sentiment_score',
        title='Sentiment Score Over Time',
        labels={'sentiment_score': 'Average Sentiment Score', 'date': 'Date'}
    )
    
    fig.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="Neutral")
    
    return fig

def display_article_card(article):
    """Display an individual article card"""
    sentiment_color = {
        'very_positive': 'Very Positive',
        'positive': 'Positive', 
        'neutral': 'Neutral',
        'negative': 'Negative',
        'very_negative': 'Very Negative'
    }
    
    market_impact_display = {
        'bullish': 'Bullish',
        'bearish': 'Bearish',
        'neutral': 'Neutral',
        'mixed': 'Mixed'
    }
    
    with st.container():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.subheader(article['title'])
            st.write(article['summary'])
            
            # Topics
            if isinstance(article['key_topics'], list):
                topics = article['key_topics']
            else:
                topics = eval(article['key_topics']) if isinstance(article['key_topics'], str) else []
            
            if topics:
                topic_tags = " ".join([f"`{topic}`" for topic in topics[:5]])
                st.markdown(f"**Topics:** {topic_tags}")
        
        with col2:
            st.markdown(f"**Sentiment:** {sentiment_color.get(article['sentiment'], 'Unknown')}")
            st.markdown(f"**Score:** {article['sentiment_score']:.2f}")
            st.markdown(f"**Market Impact:** {market_impact_display.get(article['market_impact'], 'Unknown')}")
            
            if article['source_url'] != 'unknown':
                st.markdown(f"[Read Original]({article['source_url']})")
        
        st.markdown("---")

def main():
    st.title("WSJ Sentiment Analysis Dashboard")
    st.markdown("Real-time sentiment analysis of Wall Street Journal articles using AI")
    
    # Load data
    with st.spinner("Loading data..."):
        df, data_source = load_data()
    
    if df.empty:
        st.error("No data available. Please run the pipeline first to collect and process articles.")
        st.info("Run: `python pipeline.py run` to collect articles")
        return
    
    # Data source indicator
    source_indicators = {
        "supabase": "Live Database",
        "json": "Local JSON File", 
        "csv": "CSV Backup",
        "none": "No Data"
    }
    
    st.sidebar.markdown(f"**Data Source:** {source_indicators.get(data_source, 'Unknown')}")
    st.sidebar.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Date range filter
    if not df.empty:
        min_date = df['extracted_at'].min().date()
        max_date = df['extracted_at'].max().date()
        
        date_range = st.sidebar.date_input(
            "Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        # Sentiment filter
        sentiments = st.sidebar.multiselect(
            "Sentiment",
            options=df['sentiment'].unique(),
            default=df['sentiment'].unique()
        )
        
        # Market impact filter
        impacts = st.sidebar.multiselect(
            "Market Impact",
            options=df['market_impact'].unique(),
            default=df['market_impact'].unique()
        )
        
        # Apply filters
        filtered_df = df[
            (df['extracted_at'].dt.date >= date_range[0]) &
            (df['extracted_at'].dt.date <= date_range[1]) &
            (df['sentiment'].isin(sentiments)) &
            (df['market_impact'].isin(impacts))
        ]
    else:
        filtered_df = df
    
    # Main dashboard
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Articles", len(filtered_df))
    
    with col2:
        if not filtered_df.empty:
            avg_sentiment = filtered_df['sentiment_score'].mean()
            st.metric("Avg Sentiment", f"{avg_sentiment:.2f}")
        else:
            st.metric("Avg Sentiment", "N/A")
    
    with col3:
        if not filtered_df.empty:
            positive_articles = len(filtered_df[filtered_df['sentiment_score'] > 0])
            st.metric("Positive Articles", positive_articles)
        else:
            st.metric("Positive Articles", 0)
    
    with col4:
        if not filtered_df.empty:
            bullish_articles = len(filtered_df[filtered_df['market_impact'] == 'bullish'])
            st.metric("Bullish Articles", bullish_articles)
        else:
            st.metric("Bullish Articles", 0)
    
    if not filtered_df.empty:
        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(create_sentiment_distribution(filtered_df), use_container_width=True)
        
        with col2:
            st.plotly_chart(create_market_impact_chart(filtered_df), use_container_width=True)
        
        # Sentiment gauge
        col1, col2 = st.columns([1, 1])
        
        with col1:
            avg_sentiment_score = filtered_df['sentiment_score'].mean()
            st.plotly_chart(create_sentiment_gauge(avg_sentiment_score), use_container_width=True)
        
        with col2:
            timeline_chart = create_sentiment_timeline(filtered_df)
            if timeline_chart:
                st.plotly_chart(timeline_chart, use_container_width=True)
            else:
                st.info("Not enough data points for timeline chart")
        
        # Articles table/cards
        st.header("Recent Articles")
        
        # Toggle between table and card view
        view_type = st.radio("View Type", ["Cards", "Table"], horizontal=True)
        
        if view_type == "Cards":
            # Card view
            for _, article in filtered_df.head(10).iterrows():
                display_article_card(article)
        else:
            # Table view
            display_columns = ['title', 'sentiment', 'sentiment_score', 'market_impact', 'extracted_at']
            st.dataframe(
                filtered_df[display_columns].head(20),
                use_container_width=True,
                hide_index=True
            )
    
    # Refresh button
    if st.sidebar.button("Refresh Data"):
        st.cache_data.clear()
        st.rerun()

if __name__ == "__main__":
    main()