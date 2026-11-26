#!/usr/bin/env python3
"""
Comprehensive Test Suite for Minimal Saylor Lee LangChain Service.
Tests all 62 tools with comprehensive coverage and edge cases.
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.minimal_saylor_lee_langchain_service import MinimalSaylorLeeLangChainService
import json

class ComprehensiveSaylorLeeTester:
    def __init__(self):
        self.service = MinimalSaylorLeeLangChainService()
        self.test_results = []
        self.tool_categories = {
            "Basic Info": ["ConsentCheck", "WellnessResponse", "PresentingConcern", "NameResponse", "AgeResponse"],
            "Medical History": ["MedicalHistory", "CholesterolHistory", "SurgicalHistory", "ObstetricalHistory", "RecentMedicalExam"],
            "Medications": ["Medications", "OTCMedications", "Supplements", "NonprescriptionMedications"],
            "Allergies & Safety": ["Allergies", "AllergicReaction", "EpipenInfo", "MedicAlertBracelet", "MedicationAllergies", "EnvironmentalAllergies"],
            "Systems Review": ["Headaches", "Respiratory", "CoughStatus", "Cardiovascular", "PeripheralVascular", "Genitourinary", "Musculoskeletal", "Neurological", "EndocrineGeneral", "EndocrineSymptoms", "Elimination", "SkinHair", "NailClubbing", "FootSensation", "VisionChanges"],
            "Lifestyle": ["DietNutrition", "NutritionGeneral", "DietRecall24hr", "ExerciseActivities", "WalkingDetails", "GolfDetails", "SleepPatterns", "Mobility", "AssistiveDevices"],
            "Social & Mental Health": ["MentalHealthCurrent", "CopingStrategies", "Relationships", "SpiritualResources", "FinancialStatus"],
            "Substances": ["SmokingStatus", "VapingDetails", "AlcoholUse", "Substances"],
            "Health Services": ["ImmunizationStatus", "ImmunizationDetails", "STBBITesting", "CommunicableDiseases", "EnvironmentalHazards", "SexualHealth"],
            "Family & Planning": ["FamilyHistory", "AdvancedCarePlanning", "AdvancedCarePlanningDetails"]
        }

    async def test_tool_directly(self, tool_name: str, description: str = ""):
        """Test a tool directly by name."""
        try:
            tool = self.service.get_tool_by_name(tool_name)
            if tool:
                response = tool.func()
                self.test_results.append({
                    "test_type": "direct_tool",
                    "tool_name": tool_name,
                    "response": response,
                    "status": "success"
                })
                return True
            else:
                self.test_results.append({
                    "test_type": "direct_tool",
                    "tool_name": tool_name,
                    "response": None,
                    "status": "tool_not_found"
                })
                return False
        except Exception as e:
            self.test_results.append({
                "test_type": "direct_tool",
                "tool_name": tool_name,
                "response": None,
                "status": "error",
                "error": str(e)
            })
            return False

    async def test_question_with_service(self, question: str, expected_tool: str = "", description: str = ""):
        """Test a question using the full service."""
        try:
            response = await self.service.chat_with_patient(question)
            self.test_results.append({
                "test_type": "service_question",
                "question": question,
                "expected_tool": expected_tool,
                "response": response,
                "status": "success"
            })
            return True
        except Exception as e:
            self.test_results.append({
                "test_type": "service_question",
                "question": question,
                "expected_tool": expected_tool,
                "response": None,
                "status": "error",
                "error": str(e)
            })
            return False

    async def run_comprehensive_direct_tool_tests(self):
        """Test all 62 tools directly."""
        print("🔧 COMPREHENSIVE DIRECT TOOL TESTS")
        print("Testing all 62 tools individually")
        print("="*80)
        
        total_tools = len(self.service.tools)
        successful_tools = 0
        
        for i, tool in enumerate(self.service.tools, 1):
            success = await self.test_tool_directly(tool.name, tool.description)
            if success:
                successful_tools += 1
            print(f"{i:2d}/{total_tools} - {tool.name}: {'✅' if success else '❌'}")
        
        print(f"\nDirect Tool Tests: {successful_tools}/{total_tools} successful")

    async def run_comprehensive_service_tests(self):
        """Test comprehensive service questions covering all tool categories."""
        print("\n🤖 COMPREHENSIVE SERVICE QUESTION TESTS")
        print("Testing questions through the full LangChain service")
        print("="*80)
        
        test_questions = [
            # Basic Info
            ("Hello", "WellnessResponse", "Basic greeting"),
            ("How are you today?", "WellnessResponse", "Wellness question"),
            ("What brings you in today?", "PresentingConcern", "Chief complaint"),
            ("What's your name?", "NameResponse", "Name question"),
            ("How old are you?", "AgeResponse", "Age question"),
            ("Do you consent to this examination?", "ConsentCheck", "Consent question"),
            
            # Medical History
            ("Do you have any medical conditions?", "MedicalHistory", "Medical history"),
            ("Do you have high cholesterol?", "CholesterolHistory", "Cholesterol question"),
            ("Have you had any surgeries?", "SurgicalHistory", "Surgical history"),
            ("Have you ever been pregnant?", "ObstetricalHistory", "Obstetrical history"),
            ("When was your last medical exam?", "RecentMedicalExam", "Recent exam"),
            
            # Medications
            ("What medications are you taking?", "Medications", "Current medications"),
            ("Do you take any over-the-counter medications?", "OTCMedications", "OTC medications"),
            ("Do you take any supplements?", "Supplements", "Supplements question"),
            ("What non-prescription medications do you take?", "NonprescriptionMedications", "Non-prescription meds"),
            
            # Allergies & Safety
            ("Do you have any allergies?", "Allergies", "Food allergies"),
            ("What happens when you have an allergic reaction?", "AllergicReaction", "Allergic reaction"),
            ("Do you carry an epipen?", "EpipenInfo", "Epipen question"),
            ("Do you wear a medic alert bracelet?", "MedicAlertBracelet", "Medic alert bracelet"),
            ("Do you have any medication allergies?", "MedicationAllergies", "Medication allergies"),
            ("Do you have any environmental allergies?", "EnvironmentalAllergies", "Environmental allergies"),
            
            # Systems Review
            ("Do you get headaches?", "Headaches", "Headaches question"),
            ("Do you have any breathing problems?", "Respiratory", "Respiratory question"),
            ("Do you have a cough?", "CoughStatus", "Cough question"),
            ("Do you have any cardiovascular issues?", "Cardiovascular", "Cardiovascular question"),
            ("Do you have any circulation problems?", "PeripheralVascular", "Peripheral vascular"),
            ("Do you have any urinary issues?", "Genitourinary", "Genitourinary question"),
            ("Do you have any joint or muscle problems?", "Musculoskeletal", "Musculoskeletal question"),
            ("Do you have any neurological issues?", "Neurological", "Neurological question"),
            ("How is your diabetes control?", "EndocrineGeneral", "Endocrine general"),
            ("Have you had any weight loss or fever?", "EndocrineSymptoms", "Endocrine symptoms"),
            ("How are your bowel movements?", "Elimination", "Elimination question"),
            ("Tell me about your skin and hair", "SkinHair", "Skin and hair"),
            ("Do you have any nail clubbing?", "NailClubbing", "Nail clubbing"),
            ("Do you have any foot numbness?", "FootSensation", "Foot sensation"),
            ("How is your vision?", "VisionChanges", "Vision question"),
            
            # Lifestyle
            ("What's your typical diet?", "DietNutrition", "Diet question"),
            ("Tell me about your nutrition changes", "NutritionGeneral", "Nutrition general"),
            ("What did you eat yesterday?", "DietRecall24hr", "24-hour diet recall"),
            ("What exercise do you do?", "ExerciseActivities", "Exercise question"),
            ("Tell me about your walking routine", "WalkingDetails", "Walking details"),
            ("How often do you golf?", "GolfDetails", "Golf details"),
            ("How's your sleep?", "SleepPatterns", "Sleep question"),
            ("Do you have any mobility issues?", "Mobility", "Mobility question"),
            ("Do you need any assistive devices?", "AssistiveDevices", "Assistive devices"),
            
            # Social & Mental Health
            ("How is your mental health?", "MentalHealthCurrent", "Mental health current"),
            ("How do you cope with stress?", "CopingStrategies", "Coping strategies"),
            ("Tell me about your relationships", "Relationships", "Relationships question"),
            ("Do you have any spiritual resources?", "SpiritualResources", "Spiritual resources"),
            ("Do you have any financial issues?", "FinancialStatus", "Financial status"),
            
            # Substances
            ("Do you smoke or vape?", "SmokingStatus", "Smoking/vaping question"),
            ("How much do you vape?", "VapingDetails", "Vaping details"),
            ("Do you drink alcohol?", "AlcoholUse", "Alcohol question"),
            ("Do you use any substances?", "Substances", "Substances question"),
            
            # Health Services
            ("Are your vaccines up to date?", "ImmunizationStatus", "Immunization status"),
            ("When was your last flu shot?", "ImmunizationDetails", "Immunization details"),
            ("Have you been tested for STIs?", "STBBITesting", "STBBI testing"),
            ("Do you have any communicable diseases?", "CommunicableDiseases", "Communicable diseases"),
            ("Do you have any environmental hazards?", "EnvironmentalHazards", "Environmental hazards"),
            ("Tell me about your sexual health", "SexualHealth", "Sexual health"),
            
            # Family & Planning
            ("Tell me about your family history", "FamilyHistory", "Family history"),
            ("Have you thought about advanced care planning?", "AdvancedCarePlanning", "Advanced care planning"),
            ("Who is your power of attorney?", "AdvancedCarePlanningDetails", "Advanced care planning details"),
        ]
        
        successful_questions = 0
        total_questions = len(test_questions)
        
        for i, (question, expected_tool, description) in enumerate(test_questions, 1):
            success = await self.test_question_with_service(question, expected_tool, description)
            if success:
                successful_questions += 1
            print(f"{i:2d}/{total_questions} - {description}: {'✅' if success else '❌'}")
        
        print(f"\nService Question Tests: {successful_questions}/{total_questions} successful")

    async def run_edge_case_tests(self):
        """Test edge cases and boundary conditions."""
        print("\n🧪 EDGE CASE TESTS")
        print("Testing edge cases and boundary conditions")
        print("="*80)
        
        edge_cases = [
            ("", "Empty question"),
            ("   ", "Whitespace only"),
            ("???", "Question marks only"),
            ("I don't understand", "Unclear question"),
            ("Tell me everything", "Vague request"),
            ("What's your favorite color?", "Irrelevant question"),
            ("How many medications do you take?", "Medications count"),
            ("What time do you take your medications?", "Medication timing"),
            ("How long have you had diabetes?", "Condition duration"),
            ("What's your blood pressure?", "Specific medical question"),
        ]
        
        successful_edge_cases = 0
        total_edge_cases = len(edge_cases)
        
        for i, (question, description) in enumerate(edge_cases, 1):
            success = await self.test_question_with_service(question, "", description)
            if success:
                successful_edge_cases += 1
            print(f"{i:2d}/{total_edge_cases} - {description}: {'✅' if success else '❌'}")
        
        print(f"\nEdge Case Tests: {successful_edge_cases}/{total_edge_cases} successful")

    async def run_consistency_tests(self):
        """Test consistency of responses."""
        print("\n🔄 CONSISTENCY TESTS")
        print("Testing that repeated questions get consistent responses")
        print("="*80)
        
        consistency_questions = [
            "What's your name?",
            "How old are you?",
            "What medications are you taking?",
            "Do you have any medical conditions?",
            "Do you have any allergies?",
            "Tell me about your family history",
            "Do you smoke or vape?",
            "Do you drink alcohol?",
            "What's your typical diet?",
            "How's your sleep?",
        ]
        
        consistent_responses = 0
        total_consistency_tests = 0
        
        for question in consistency_questions:
            responses = []
            for i in range(3):
                response = await self.service.chat_with_patient(question)
                responses.append(response)
            
            # Check if all responses are the same
            if all(r == responses[0] for r in responses):
                consistent_responses += 1
                print(f"✅ {question}: Consistent")
            else:
                print(f"❌ {question}: Inconsistent")
                for i, response in enumerate(responses, 1):
                    print(f"   Response {i}: {response}")
            
            total_consistency_tests += 1
        
        print(f"\nConsistency Tests: {consistent_responses}/{total_consistency_tests} consistent")

    async def run_all_tests(self):
        """Run all comprehensive test suites."""
        print("🧪 COMPREHENSIVE SAYLOR LEE LANGCHAIN SERVICE TEST SUITE")
        print("Testing all 62 tools with comprehensive coverage")
        print("="*80)
        
        # List available tools by category
        print(f"\n📋 Available Tools ({len(self.service.tools)}):")
        for category, tools in self.tool_categories.items():
            print(f"\n{category}:")
            for tool_name in tools:
                tool = self.service.get_tool_by_name(tool_name)
                if tool:
                    print(f"  ✅ {tool_name}: {tool.description}")
                else:
                    print(f"  ❌ {tool_name}: NOT FOUND")
        
        # Run all test suites
        await self.run_comprehensive_direct_tool_tests()
        await self.run_comprehensive_service_tests()
        await self.run_edge_case_tests()
        await self.run_consistency_tests()
        
        # Print comprehensive summary
        self.print_comprehensive_summary()

    def print_comprehensive_summary(self):
        """Print a comprehensive summary of all test results."""
        print(f"\n{'='*80}")
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print(f"{'='*80}")
        
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results if r['status'] == 'success'])
        failed_tests = total_tests - successful_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(successful_tests/total_tests)*100:.1f}%")
        
        # Breakdown by test type
        direct_tool_tests = [r for r in self.test_results if r['test_type'] == 'direct_tool']
        service_question_tests = [r for r in self.test_results if r['test_type'] == 'service_question']
        
        print(f"\n📊 Test Breakdown:")
        print(f"  Direct Tool Tests: {len([r for r in direct_tool_tests if r['status'] == 'success'])}/{len(direct_tool_tests)} successful")
        print(f"  Service Question Tests: {len([r for r in service_question_tests if r['status'] == 'success'])}/{len(service_question_tests)} successful")
        
        if failed_tests > 0:
            print(f"\n❌ Failed Tests:")
            for result in self.test_results:
                if result['status'] != 'success':
                    test_name = result.get('tool_name', result.get('question', 'Unknown'))
                    print(f"  - {test_name}: {result['status']}")
        
        print(f"\n✅ Comprehensive testing completed!")

async def main():
    tester = ComprehensiveSaylorLeeTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
