#!/usr/bin/env python3
"""
Test minimal endpoint functionality.
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.minimal_langchain_service import MinimalLangChainService

async def test_minimal_endpoint():
    """Test the minimal endpoint functionality."""
    print("🧪 MINIMAL ENDPOINT TEST")
    print("Testing minimal chat functionality")
    
    service = MinimalLangChainService()
    
    # Test a few key questions
    questions = [
        "Hello",
        "What's your name?",
        "How old are you?",
        "What medications are you taking?",
        "Do you have any allergies?"
    ]
    
    for question in questions:
        print(f"\n{'='*60}")
        print(f"QUESTION: {question}")
        print(f"{'='*60}")
        
        try:
            response = await service.chat_with_patient(question)
            print(f"RESPONSE: {response}")
        except Exception as e:
            print(f"ERROR: {str(e)}")
    
    print(f"\n{'='*60}")
    print("✅ MINIMAL ENDPOINT TEST COMPLETED")
    print(f"{'='*60}")

if __name__ == "__main__":
    asyncio.run(test_minimal_endpoint())
