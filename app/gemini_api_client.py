import requests
import base64
import json
from io import BytesIO
from PIL import Image
from .config import settings
from .models import Tag, Department, Priority
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class GeminiAPIClient:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        self.headers = {
            "Content-Type": "application/json",
        }
        
    def analyze_image(self, image_data: str, user_description: str) -> Dict[str, Any]:
        """
        Analyze image using Gemini 2.0 Flash API
        """
        try:
            # Decode base64 image
            image_bytes = base64.b64decode(image_data)
            image = Image.open(BytesIO(image_bytes))
            
            # Convert image to base64 for API
            buffered = BytesIO()
            image.save(buffered, format="JPEG")
            image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            
            # Prepare the prompt
            prompt = self._create_prompt(user_description)
            
            # Prepare the request payload
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt},
                            {
                                "inline_data": {
                                    "mime_type": "image/jpeg",
                                    "data": image_base64
                                }
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.1,
                    "topP": 0.8,
                    "topK": 40,
                    "maxOutputTokens": 2048,
                }
            }
            
            # Make API request
            response = requests.post(
                f"{self.base_url}?key={self.api_key}",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and result['candidates']:
                    text_response = result['candidates'][0]['content']['parts'][0]['text']
                    return self._parse_response(text_response, user_description)
                else:
                    raise Exception("No response from Gemini API")
            else:
                error_msg = f"API Error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            logger.error(f"Error in analyze_image: {str(e)}")
            raise Exception(f"Error analyzing image: {str(e)}")
    
    def analyze_text_only(self, user_description: str) -> Dict[str, Any]:
        """
        Fallback method for text-only analysis
        """
        try:
            prompt = self._create_prompt(user_description)
            
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.1,
                    "topP": 0.8,
                    "topK": 40,
                    "maxOutputTokens": 2048,
                }
            }
            
            response = requests.post(
                f"{self.base_url}?key={self.api_key}",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and result['candidates']:
                    text_response = result['candidates'][0]['content']['parts'][0]['text']
                    return self._parse_response(text_response, user_description)
                else:
                    raise Exception("No response from Gemini API")
            else:
                error_msg = f"API Error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            logger.error(f"Error in analyze_text_only: {str(e)}")
            raise Exception(f"Error analyzing text: {str(e)}")
    
    def _create_prompt(self, user_description: str) -> str:
        return f"""
        Analyze this urban infrastructure image and description, and provide a detailed analysis in the following structured format:

        USER_DESCRIPTION: {user_description}

        Available tags by department:

        WATER DEPARTMENT:
        - Pipe Burst, Low Pressure, Quality Issue, Meter Problem, Billing Issue

        ROADS DEPARTMENT:
        - Pothole, Traffic Signal, Street Light, Road Damage, Drainage

        WASTE MANAGEMENT:
        - Collection Delay, Bin Overflow, Illegal Dumping, Recycling, Hazardous Waste

        ELECTRICITY DEPARTMENT:
        - Power Outage, Voltage Issues, Meter Reading, Billing, Street Light

        Please analyze and respond with EXACTLY this format (no additional text):

        TAGS: [comma-separated list of relevant tags from the above categories]
        DEPARTMENT: [water, roads, waste, electricity, other]
        PRIORITY: [low, medium, high, critical]
        IMAGE_DESCRIPTION: [Detailed professional description of the image content]
        DESCRIPTION_MATCH: [true/false - does the image match the user's description?]
        CONFIDENCE: [0.0-1.0 confidence score]
        SUGGESTED_ACTIONS: [comma-separated list of 2-3 suggested actions]

        Important: The user described: "{user_description}". Compare the image content with this description.
        Consider the severity and urgency when assigning priority.

        Respond ONLY with the structured format above, no additional commentary.
        """

    def _parse_response(self, response_text: str, user_description: str) -> Dict[str, Any]:
        try:
            lines = response_text.strip().split('\n')
            result = {}
            
            for line in lines:
                line = line.strip()
                if line.startswith('TAGS:'):
                    tags_str = line.replace('TAGS:', '').strip().strip('[]')
                    result['tags'] = [self._parse_tag(tag.strip()) for tag in tags_str.split(',') if tag.strip()]
                elif line.startswith('DEPARTMENT:'):
                    dept_str = line.replace('DEPARTMENT:', '').strip()
                    result['department'] = self._parse_department(dept_str)
                elif line.startswith('PRIORITY:'):
                    priority_str = line.replace('PRIORITY:', '').strip()
                    result['priority'] = self._parse_priority(priority_str)
                elif line.startswith('IMAGE_DESCRIPTION:'):
                    result['image_description'] = line.replace('IMAGE_DESCRIPTION:', '').strip()
                elif line.startswith('DESCRIPTION_MATCH:'):
                    match_str = line.replace('DESCRIPTION_MATCH:', '').strip().lower()
                    result['description_match'] = match_str == 'true'
                elif line.startswith('CONFIDENCE:'):
                    try:
                        result['confidence_score'] = float(line.replace('CONFIDENCE:', '').strip())
                    except:
                        result['confidence_score'] = 0.5
                elif line.startswith('SUGGESTED_ACTIONS:'):
                    actions_str = line.replace('SUGGESTED_ACTIONS:', '').strip().strip('[]')
                    result['suggested_actions'] = [action.strip() for action in actions_str.split(',') if action.strip()]
            
            # Validate required fields
            required_fields = ['tags', 'department', 'priority', 'image_description', 'description_match']
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Missing field in response: {field}")
            
            if 'confidence_score' not in result:
                result['confidence_score'] = 0.5
            
            if 'suggested_actions' not in result:
                result['suggested_actions'] = ["Investigate the issue", "Contact relevant department"]
                
            return result
            
        except Exception as e:
            raise ValueError(f"Failed to parse Gemini response: {str(e)}\nResponse: {response_text}")

    def _parse_tag(self, tag_str: str) -> Tag:
        tag_mapping = {
            # Water Department
            'pipe burst': Tag.PIPE_BURST,
            'low pressure': Tag.LOW_PRESSURE,
            'quality issue': Tag.QUALITY_ISSUE,
            'meter problem': Tag.METER_PROBLEM,
            'billing issue': Tag.BILLING_ISSUE,
            
            # Roads Department
            'pothole': Tag.POTHOLE,
            'traffic signal': Tag.TRAFFIC_SIGNAL,
            'street light': Tag.STREET_LIGHT,
            'road damage': Tag.ROAD_DAMAGE,
            'drainage': Tag.DRAINAGE,
            
            # Waste Management
            'collection delay': Tag.COLLECTION_DELAY,
            'bin overflow': Tag.BIN_OVERFLOW,
            'illegal dumping': Tag.ILLEGAL_DUMPING,
            'recycling': Tag.RECYCLING,
            'hazardous waste': Tag.HAZARDOUS_WASTE,
            
            # Electricity Department
            'power outage': Tag.POWER_OUTAGE,
            'voltage issues': Tag.VOLTAGE_ISSUES,
            'meter reading': Tag.METER_READING,
            'billing': Tag.BILLING,
            'street light electricity': Tag.STREET_LIGHT_ELECTRICITY,
        }
        
        cleaned_tag = tag_str.lower().strip()
        return tag_mapping.get(cleaned_tag, Tag.OTHER)

    def _parse_department(self, dept_str: str) -> Department:
        dept_mapping = {
            'water': Department.WATER,
            'roads': Department.ROADS,
            'waste': Department.WASTE,
            'electricity': Department.ELECTRICITY,
            'other': Department.OTHER
        }
        return dept_mapping.get(dept_str.lower(), Department.OTHER)

    def _parse_priority(self, priority_str: str) -> Priority:
        priority_mapping = {
            'low': Priority.LOW,
            'medium': Priority.MEDIUM,
            'high': Priority.HIGH,
            'critical': Priority.CRITICAL
        }
        return priority_mapping.get(priority_str.lower(), Priority.MEDIUM)