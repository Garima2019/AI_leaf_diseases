import os
import base64
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class LeafDiseaseAnalyzer:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "meta-llama/llama-4-scout-17b-16e-instruct"
    
    def encode_image(self, image_path):
        """Encode image to base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def analyze_leaf(self, image_path):
        """Analyze leaf image for diseases"""
        
        base64_image = self.encode_image(image_path)
        
        prompt = """You are an expert plant pathologist. Analyze this leaf image and provide:

1. **Disease Identification**: Name the disease(s) if present, or state if the leaf is healthy
2. **Severity Level**: Rate as Low, Moderate, High, or Critical
3. **Symptoms Observed**: List visible symptoms
4. **Possible Causes**: Environmental or pathogenic factors
5. **Treatment Recommendations**: 
   - Immediate actions
   - Chemical treatments (fungicides, pesticides)
   - Organic alternatives
   - Prevention measures
6. **Additional Care**: Long-term plant health advice

Format your response clearly with headers and bullet points."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            return {
                "success": True,
                "analysis": response.choices[0].message.content,
                "model": self.model
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def extract_structured_data(self, analysis_text):
        """Extract structured information from analysis"""
        
        prompt = f"""From the following leaf disease analysis, extract structured data in JSON format:

Analysis:
{analysis_text}

Return a JSON object with these fields:
- disease_name: string (if healthy, write "Healthy" or "No Disease Detected")
- is_diseased: boolean (true if diseased, false if healthy)
- severity: string (Low/Moderate/High/Critical or "None" if healthy)
- confidence: string (percentage estimate)
- symptoms: array of strings
- treatments: array of strings (empty array if healthy)
- prevention: array of strings

Only return valid JSON, no additional text."""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error extracting structured data: {str(e)}"