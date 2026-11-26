#!/usr/bin/env python3
"""
Minimal test suite for chat service - just prompt and raw LLM response.
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.minimal_chat_service import MinimalChatService

class MinimalChatTester:
    def __init__(self):
        self.chat_dservice = MinimalChatService()

    async def test_question(self, question: str, description: str = ""):
        """Test a single question and print the raw response."""
        print(f"\n{'='*80}")
        print(f"TEST: {description or question}")
        print(f"{'='*80}")
        print(f"QUESTION: {question}")
        print(f"{'='*80}")
        
        try:
            response = await self.chat_service.chat_with_patient(question)
            print(f"PATIENT REPLY: {response}")
            
        except Exception as e:
            print(f"ERROR: {str(e)}")
            import traceback
            traceback.print_exc()

    async def run_all_tests(self):
        """Run all test questions."""
        print("🧪 MINIMAL CHAT SERVICE TEST SUITE")
        print("Testing individual questions with raw LLM response")
        
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
    tester = MinimalChatTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
