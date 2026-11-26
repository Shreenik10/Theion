#!/usr/bin/env python3
"""
Test suite for Minimal Saylor Lee LangChain Service - based on SaylorLeeTools.py styling.
Tests individual tools and responses with detailed output.
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.minimal_saylor_lee_langchain_service import MinimalSaylorLeeLangChainService
import json

class MinimalSaylorLeeTester:
    def __init__(self):
        self.service = MinimalSaylorLeeLangChainService()
        self.test_results = []

    async def test_tool_directly(self, tool_name: str, description: str = ""):
        """Test a tool directly by name."""
        print(f"\n{'='*80}")
        print(f"DIRECT TOOL TEST: {tool_name}")
        print(f"Description: {description}")
        print(f"{'='*80}")
        
        try:
            tool = self.service.get_tool_by_name(tool_name)
            if tool:
                response = tool.func()
                print(f"TOOL RESPONSE: {response}")
                self.test_results.append({
                    "test_type": "direct_tool",
                    "tool_name": tool_name,
                    "response": response,
                    "status": "success"
                })
            else:
                print(f"ERROR: Tool '{tool_name}' not found")
                self.test_results.append({
                    "test_type": "direct_tool",
                    "tool_name": tool_name,
                    "response": None,
                    "status": "tool_not_found"
                })
        except Exception as e:
            print(f"ERROR: {str(e)}")
            self.test_results.append({
                "test_type": "direct_tool",
                "tool_name": tool_name,
                "response": None,
                "status": "error",
                "error": str(e)
            })

    async def test_question_with_service(self, question: str, description: str = "", expected_tool: str = ""):
        """Test a question using the full service."""
        print(f"\n{'='*80}")
        print(f"SERVICE TEST: {description or question}")
        print(f"Question: {question}")
        if expected_tool:
            print(f"Expected Tool: {expected_tool}")
        print(f"{'='*80}")
        
        try:
            response = await self.service.chat_with_patient(question)
            print(f"SERVICE RESPONSE: {response}")
            self.test_results.append({
                "test_type": "service_question",
                "question": question,
                "expected_tool": expected_tool,
                "response": response,
                "status": "success"
            })
        except Exception as e:
            print(f"ERROR: {str(e)}")
            self.test_results.append({
                "test_type": "service_question",
                "question": question,
                "expected_tool": expected_tool,
                "response": None,
                "status": "error",
                "error": str(e)
            })

    async def run_direct_tool_tests(self):
        """Test all tools directly."""
        print("🔧 DIRECT TOOL TESTS")
        print("Testing each tool individually")
        
        # Test each tool directly
        await self.test_tool_directly("ConsentCheck", "Consent response")
        await self.test_tool_directly("WellnessResponse", "Wellness greeting response")
        await self.test_tool_directly("PresentingConcern", "Why patient is here today")
        await self.test_tool_directly("NameResponse", "Patient's name")
        await self.test_tool_directly("AgeResponse", "Patient's age")
        await self.test_tool_directly("MedicalHistory", "Medical conditions and history")
        await self.test_tool_directly("Medications", "Current medications")
        await self.test_tool_directly("Allergies", "Food allergies")
        await self.test_tool_directly("FamilyHistory", "Family medical history")
        await self.test_tool_directly("SmokingStatus", "Smoking/vaping status")
        await self.test_tool_directly("AlcoholUse", "Alcohol consumption")
        await self.test_tool_directly("ExerciseActivities", "Physical activities and exercise")
        await self.test_tool_directly("SleepPatterns", "Sleep habits and quality")
        await self.test_tool_directly("DietNutrition", "Diet and nutrition information")
        await self.test_tool_directly("Headaches", "Headache symptoms and HEENT")
        await self.test_tool_directly("Respiratory", "Respiratory health")
        await self.test_tool_directly("AdvancedCarePlanning", "Advanced care planning status")

    async def run_service_question_tests(self):
        """Test questions using the full service."""
        print("\n🤖 SERVICE QUESTION TESTS")
        print("Testing questions through the full LangChain service")
        
        # Basic greeting and introduction
        await self.test_question_with_service("Hello", "Basic greeting", "WellnessResponse")
        await self.test_question_with_service("How are you today?", "How are you question", "WellnessResponse")
        await self.test_question_with_service("What brings you in today?", "Chief complaint question", "PresentingConcern")
        
        # Personal information
        await self.test_question_with_service("What's your name?", "Name question", "NameResponse")
        await self.test_question_with_service("How old are you?", "Age question", "AgeResponse")
        
        # Medical history
        await self.test_question_with_service("Do you have any medical conditions?", "Medical history question", "MedicalHistory")
        await self.test_question_with_service("What medications are you taking?", "Medications question", "Medications")
        await self.test_question_with_service("Do you have any allergies?", "Allergies question", "Allergies")
        
        # Family and social history
        await self.test_question_with_service("Tell me about your family history", "Family history", "FamilyHistory")
        await self.test_question_with_service("Do you smoke or vape?", "Smoking/vaping question", "SmokingStatus")
        await self.test_question_with_service("Do you drink alcohol?", "Alcohol question", "AlcoholUse")
        
        # Lifestyle and activities
        await self.test_question_with_service("Tell me about your exercise routine", "Exercise question", "ExerciseActivities")
        await self.test_question_with_service("How's your sleep?", "Sleep question", "SleepPatterns")
        await self.test_question_with_service("What's your typical daily diet?", "Diet question", "DietNutrition")
        
        # Systems review
        await self.test_question_with_service("Any headaches?", "Headaches question", "Headaches")
        await self.test_question_with_service("Any breathing problems?", "Respiratory question", "Respiratory")
        
        # Advanced care planning
        await self.test_question_with_service("Have you thought about advanced care planning?", "Advanced care planning", "AdvancedCarePlanning")
        
        # Consent
        await self.test_question_with_service("Do you consent to this examination?", "Consent question", "ConsentCheck")

    async def run_consistency_tests(self):
        """Test consistency of responses."""
        print("\n🔄 CONSISTENCY TESTS")
        print("Testing that repeated questions get consistent responses")
        
        # Test repeated questions
        questions = [
            "What's your name?",
            "How old are you?",
            "What medications are you taking?",
            "Do you have any medical conditions?"
        ]
        
        for question in questions:
            print(f"\n--- Testing: {question} ---")
            for i in range(3):
                response = await self.service.chat_with_patient(question)
                print(f"Response {i+1}: {response}")

    async def run_all_tests(self):
        """Run all test suites."""
        print("🧪 MINIMAL SAYLOR LEE LANGCHAIN SERVICE TEST SUITE")
        print("Testing tools and service responses")
        
        # List available tools
        print(f"\n📋 Available Tools ({len(self.service.tools)}):")
        for tool in self.service.list_tools():
            print(f"  - {tool['name']}: {tool['description']}")
        
        # Run test suites
        await self.run_direct_tool_tests()
        await self.run_service_question_tests()
        await self.run_consistency_tests()
        
        # Print summary
        self.print_test_summary()

    def print_test_summary(self):
        """Print a summary of all test results."""
        print(f"\n{'='*80}")
        print("📊 TEST SUMMARY")
        print(f"{'='*80}")
        
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results if r['status'] == 'success'])
        failed_tests = total_tests - successful_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(successful_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ Failed Tests:")
            for result in self.test_results:
                if result['status'] != 'success':
                    print(f"  - {result.get('tool_name', result.get('question', 'Unknown'))}: {result['status']}")
        
        print(f"\n✅ All tests completed!")

async def main():
    tester = MinimalSaylorLeeTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
