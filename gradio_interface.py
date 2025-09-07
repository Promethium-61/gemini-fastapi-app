import gradio as gr
import requests
import base64
import os
from PIL import Image
import io
import json

# API configuration
API_URL = "http://localhost:8000"

def analyze_complaint(image, description):
    """
    Send image and description to the FastAPI endpoint for analysis
    """
    try:
        # Convert image to base64
        if image is None:
            return "Please upload an image", "", "", "", "", ""
        
        # Convert PIL Image to bytes
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_bytes = buffered.getvalue()
        
        # Encode to base64
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        img_data_uri = f"data:image/jpeg;base64,{img_base64}"
        
        # Prepare payload
        payload = {
            "description": description,
            "image_data": img_data_uri
        }
        
        # Send request to FastAPI
        response = requests.post(f"{API_URL}/analyze-complaint", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            
            # Format the response
            tags = ", ".join(result['tags'])
            department = result['department'].upper()
            priority = result['priority'].upper()
            description_match = "✅ MATCHES" if result['description_match'] else "❌ DOES NOT MATCH"
            confidence = f"{result['confidence_score'] * 100:.1f}%"
            image_desc = result['image_description']
            suggested_actions = "\n".join([f"• {action}" for action in result['suggested_actions']])
            
            # Create formatted output
            output = f"""
            🏷️ **TAGS**: {tags}
            
            🏢 **DEPARTMENT**: {department}
            
            ⚡ **PRIORITY**: {priority}
            
            📝 **DESCRIPTION MATCH**: {description_match}
            
            🎯 **CONFIDENCE**: {confidence}
            
            📋 **IMAGE DESCRIPTION**:
            {image_desc}
            
            🚀 **SUGGESTED ACTIONS**:
            {suggested_actions}
            """
            
            return output, tags, department, priority, description_match, confidence
            
        else:
            error_msg = f"Error: {response.status_code} - {response.text}"
            return error_msg, "", "", "", "", ""
            
    except Exception as e:
        error_msg = f"Connection error: {str(e)}. Make sure the FastAPI server is running on {API_URL}"
        return error_msg, "", "", "", "", ""

def test_connection():
    """
    Test connection to the FastAPI server
    """
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            return "✅ Connected successfully to FastAPI server!"
        else:
            return f"❌ Connection failed: {response.status_code}"
    except Exception as e:
        return f"❌ Cannot connect to FastAPI server: {str(e)}"

def get_sample_descriptions():
    """
    Return sample descriptions for quick testing
    """
    samples = [
        "Large pothole on the road causing traffic issues",
        "Water pipe burst flooding the street",
        "Garbage bin overflowing with trash",
        "Street light not working at night",
        "Power outage in the neighborhood",
        "Sewage water leaking onto the road",
        "Traffic signal malfunctioning",
        "Illegal dumping of construction waste"
    ]
    return samples

# Create Gradio interface
with gr.Blocks(title="Urban Infrastructure Analyzer", theme="soft") as demo:
    gr.Markdown("# 🏙️ Urban Infrastructure Complaint Analyzer")
    gr.Markdown("Upload an image and describe the infrastructure issue. The AI will analyze it and route to the appropriate department.")
    
    # Connection status
    with gr.Row():
        status = gr.Textbox(label="Connection Status", value=test_connection(), interactive=False)
        refresh_btn = gr.Button("🔄 Refresh Connection")
    
    with gr.Row():
        with gr.Column():
            # Image input
            image_input = gr.Image(
                label="Upload Infrastructure Image", 
                type="pil",
                sources=["upload", "webcam", "clipboard"],
                height=300
            )
            
            # Description input
            description_input = gr.Textbox(
                label="Issue Description", 
                placeholder="Describe the infrastructure issue...",
                lines=3
            )
            
            # Sample descriptions dropdown
            sample_dropdown = gr.Dropdown(
                label="Quick Examples",
                choices=get_sample_descriptions(),
                value="Large pothole on the road causing traffic issues"
            )
            
            # Analyze button
            analyze_btn = gr.Button("🔍 Analyze Complaint", variant="primary")
        
        with gr.Column():
            # Main output
            output_text = gr.Markdown(
                label="Analysis Results",
                value="### Results will appear here after analysis..."
            )
            
            # Detailed outputs in an accordion
            with gr.Accordion("📊 Detailed Results", open=False):
                with gr.Row():
                    tags_output = gr.Textbox(label="Tags", interactive=False)
                    dept_output = gr.Textbox(label="Department", interactive=False)
                with gr.Row():
                    priority_output = gr.Textbox(label="Priority", interactive=False)
                    match_output = gr.Textbox(label="Description Match", interactive=False)
                confidence_output = gr.Textbox(label="Confidence Score", interactive=False)
    
    # Footer
    gr.Markdown("---")
    gr.Markdown("**Built with FastAPI + Gemini AI + Gradio** • [API Docs](http://localhost:8000/docs)")
    
    # Event handlers
    def update_description(description):
        return description
    
    def refresh_connection():
        return test_connection()
    
    # Connect events
    sample_dropdown.change(
        fn=update_description,
        inputs=[sample_dropdown],
        outputs=[description_input]
    )
    
    refresh_btn.click(
        fn=refresh_connection,
        outputs=[status]
    )
    
    analyze_btn.click(
        fn=analyze_complaint,
        inputs=[image_input, description_input],
        outputs=[output_text, tags_output, dept_output, priority_output, match_output, confidence_output]
    )

# Instructions for running
if __name__ == "__main__":
    print("Starting Gradio interface...")
    print("Make sure your FastAPI server is running on http://localhost:8000")
    print("You can start it with: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    print("\nThe Gradio interface will be available at http://localhost:7860")
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )