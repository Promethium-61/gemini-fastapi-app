# Urban Infrastructure Complaint Analyzer

AI-powered system for analyzing urban infrastructure complaints using Gemini API, FastAPI, and Gradio.

## 🚀 Quick Start

## Prerequisites
- Python 3.9+
- Conda/Miniconda
- Gemini API key

## 1. Setup Environment


#### Create conda environment
'''
conda create -n gemini-fastapi python=3.9 -y
conda activate gemini-fastapi'''

### Install dependencies
'''pip install -r requirements.txt'''

### Create .env file according to .penv file

## 2. Run FastAPI Server


### Start the API server
'''uvicorn app.main:app --reload --host 0.0.0.0 --port 8000'''

## 3. Run Gradio Interface (New Terminal)


### Make sure to activate the same environment
'''conda activate gemini-fastapi'''

### Install Gradio if not already installed
'''pip install gradio'''

### Start Gradio interface
'''python gradio_interface.py'''




 
