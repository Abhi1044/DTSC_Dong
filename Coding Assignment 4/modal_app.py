"""
Modal deployment configuration for WSJ Sentiment Analysis Streamlit app
"""

import modal
import os

# Create Modal app
app = modal.App("wsj-sentiment-dashboard")

# Define the Docker image with all dependencies
image = (
    modal.Image.debian_slim()
    .pip_install([
        "streamlit",
        "pandas", 
        "plotly",
        "openai",
        "requests",
        "beautifulsoup4",
        "lxml",
        "supabase",
        "python-dotenv"
    ])
    .apt_install(["git"])
)

# Mount the source code
mount = modal.Mount.from_local_dir("src", remote_path="/app/src")

@app.function(
    image=image,
    mounts=[mount],
    secrets=[
        modal.Secret.from_name("openai-secret"),  # You'll need to create this
        modal.Secret.from_name("supabase-secret")  # You'll need to create this
    ],
    allow_concurrent_inputs=100,
    timeout=60 * 60  # 1 hour timeout
)
@modal.web_server(8000, startup_timeout=60)
def run_streamlit():
    """Run the Streamlit app on Modal"""
    import subprocess
    import sys
    
    # Change to app directory
    os.chdir("/app")
    
    # Add src to Python path
    sys.path.append("/app/src")
    
    # Run Streamlit
    subprocess.run([
        "streamlit", "run", "src/streamlit_app.py",
        "--server.port", "8000",
        "--server.address", "0.0.0.0",
        "--server.headless", "true",
        "--server.fileWatcherType", "none",
        "--browser.gatherUsageStats", "false"
    ])

# Deployment function that can be called from CLI
@app.function(image=image, mounts=[mount])
def deploy():
    """Deploy the Streamlit app"""
    print("Deploying WSJ Sentiment Analysis Dashboard to Modal...")
    return "Deployment complete!"

if __name__ == "__main__":
    # Local development
    print("Running Streamlit app locally...")
    import subprocess
    subprocess.run(["streamlit", "run", "src/streamlit_app.py"])