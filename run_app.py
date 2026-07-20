import subprocess
import webbrowser
import time
import sys
import os

def launch():
    # Make sure we are in the correct directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)

    print("=========================================")
    print("🚀 Launching Air Quality Dashboard...")
    print("=========================================")

    # Run Streamlit in a subprocess
    # We use sys.executable to ensure we use the same Python interpreter
    cmd = [sys.executable, "-m", "streamlit", "run", "app.py"]
    
    # Start the process
    process = subprocess.Popen(cmd)

    # Wait 2 seconds for the server to spin up
    time.sleep(2)

    # Force open the default web browser
    dashboard_url = "http://localhost:8501"
    print(f"\n🌐 Opening browser automatically at: {dashboard_url}")
    webbrowser.open(dashboard_url)

    print("\n💡 Press Ctrl + C in this terminal to stop the server.\n")

    # Keep the script running to keep the subprocess alive
    try:
        process.wait()
    except KeyboardInterrupt:
        print("\n👋 Stopping the Streamlit server...")
        process.terminate()

if __name__ == "__main__":
    launch()
