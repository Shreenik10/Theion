#!/usr/bin/env python3
"""
Test suite for simple chat service - tests individual questions and prints raw responses.
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.simple_chat_service import SimpleChatService
import json

class SimpleChatTester:
    def __init__(self):
        self.chat_service = SimpleChatService()
        self.test_case_id = "test-case-123"
        self.chat_history = ""

    async def test_question(self, question: str, description: str = ""):
        """Test a single question and print the raw response."""
        print(f"\n{'='*80}")
        print(f"TEST: {description or question}")
        print(f"{'='*80}")
        print(f"QUESTION: {question}")
        print(f"{'='*80}")
        
        try:
            response = await self.chat_service.chat_with_patient(
                case_id=self.test_case_id,
                message=question,
                chat_history=self.chat_history
            )
            
            print(f"RAW RESPONSE OBJECT:")
            print(json.dumps({
                "case_id": response.case_id,
                "message": response.message,
                "is_final": response.is_final,
                "emotion": response.emotion
            }, indent=2))
            
            print(f"\nPATIENT REPLY: {response.message}")
            if response.emotion:
                print(f"EMOTION: {response.emotion}")
            
            # Update chat history for context
            self.chat_history += f"Doctor: {question}\nPatient: {response.message}\n"
            
        except Exception as e:
            print(f"ERROR: {str(e)}")
            import traceback
            traceback.print_exc()

    async def run_all_tests(self):
        """Run all test questions."""
        print("🧪 SIMPLE CHAT SERVICE TEST SUITE")
        print("Testing individual questions with raw response output")
        
        # Basic greeting and introduction
        await self.test_question("Hello", "Basic greeting")
        await self.test_question("How are you today?", "How are you question")
        await self.test_question("What brings you in today?", "Chief complaint question")
        
        # Personal information
        await self.test_question("What's your name?", "Name question")
        await self.test_question("How old are you?", "Age question")
        await self.test_question("What's your gender?", "Gender question")
        
        # Medical history
        await self.test_question("Do you have any medical conditions?", "Medical history question")
        await self.test_question("What medications are you taking?", "Medications question")
        await self.test_question("Do you have any allergies?", "Allergies question")
        
        # Specific medical details
        await self.test_question("Tell me about your diabetes", "Diabetes details")
        await self.test_question("What about your anxiety?", "Anxiety details")
        await self.test_question("Do you have high cholesterol?", "Cholesterol question")
        
        # Family history
        await self.test_question("Tell me about your family history", "Family history")
        
        # Social history
        await self.test_question("Do you smoke or vape?", "Smoking/vaping question")
        await self.test_question("Do you drink alcohol?", "Alcohol question")
        await self.test_question("Tell me about your exercise routine", "Exercise question")
        
        # Systems review
        await self.test_question("Any headaches?", "Headaches question")
        await self.test_question("Any breathing problems?", "Respiratory question")
        await self.test_question("How's your sleep?", "Sleep question")
        
        # Specific detailed questions
        await self.test_question("What's your typical daily diet?", "Diet question")
        await self.test_question("Tell me about your peanut allergy", "Peanut allergy details")
        await self.test_question("Do you carry an epi-pen?", "Epi-pen question")
        
        # Edge cases and consistency tests
        await self.test_question("What medications are you taking?", "Medications repeat (consistency test)")
        await self.test_question("How old are you?", "Age repeat (consistency test)")
        await self.test_question("Do you have any medical conditions?", "Medical history repeat (consistency test)")
        
        # Complex questions
        await self.test_question("Tell me about your reaction to peanuts and whether you carry an epi-pen", "Combined allergy question")
        await self.test_question("What non-prescription medications do you take?", "Non-prescription meds")
        
        # Advanced care planning
        await self.test_question("Have you thought about advanced care planning?", "Advanced care planning")
        
        print(f"\n{'='*80}")
        print("✅ ALL TESTS COMPLETED")
        print(f"{'='*80}")

async def main():
    tester = SimpleChatTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
