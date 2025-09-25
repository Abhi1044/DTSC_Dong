import shlex
import subprocess
from pathlib import Path
import os
# Comment out dotenv to avoid errors in Modal
# from dotenv import load_dotenv

import modal

# Comment out load_dotenv for Modal deployment
# load_dotenv()

streamlit_script_local_path = Path(__file__).parent / "streamlit_run.py"
streamlit_script_remote_path = "/root/streamlit_run.py"

# Configure Modal image with all required packages
image = (
    modal.Image.debian_slim(python_version="3.9")
    .pip_install("streamlit", "supabase", "pandas", "plotly", "python-dotenv")
    .env({"FORCE_REBUILD": "true"})  # Force rebuild for updates
    .add_local_file(streamlit_script_local_path, streamlit_script_remote_path)
)

# Create Modal app with image only (secrets will be added when available)
app = modal.App(
    name="enhanced-streamlit-dashboard", 
    image=image
)

if not streamlit_script_local_path.exists():
    raise RuntimeError(
        "Hey your starter streamlit isnt working"
    )

@app.function()
@modal.web_server(8000)
def run():
    target = shlex.quote(streamlit_script_remote_path)
    cmd = f"streamlit run {target} --server.port 8000 --server.enableCORS=false --server.enableXsrfProtection=false"
    
    # Build environment variables for Supabase integration, filtering out None values
    env_vars = {}
    if os.getenv("SUPABASE_KEY"):
        env_vars["SUPABASE_KEY"] = os.getenv("SUPABASE_KEY")
    if os.getenv("SUPABASE_URL"):
        env_vars["SUPABASE_URL"] = os.getenv("SUPABASE_URL")
    
    # Include current environment to ensure PATH and other essential vars are available
    env_vars.update(os.environ)
    
    # Start Streamlit with proper environment variables
    subprocess.Popen(cmd, shell=True, env=env_vars)