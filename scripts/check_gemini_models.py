"""Check available Google Gemini models."""

import os
import sys
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

load_dotenv()

try:
    import google.generativeai as genai
    
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("No Google API key found in .env file")
    else:
        genai.configure(api_key=api_key)
        
        print("Available Gemini models:")
        print("=" * 60)
        
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                print(f"✓ {model.name}")
                print(f"  Display Name: {model.display_name}")
                print(f"  Description: {model.description[:80]}...")
                print()
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
