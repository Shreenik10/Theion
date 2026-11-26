from langchain_core.prompts import PromptTemplate
from langchain_community.tools import Tool
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain_core.messages import HumanMessage
from .base_service import BaseLangChainService
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class MinimalSaylorLeeLangChainService(BaseLangChainService):
    """Minimal Saylor Lee service using LangChain tools approach."""
    
    def __init__(self):
        super().__init__()
        
        # Initialize tools
        self.tools = self._initialize_tools()
        
        # Create the agent with proper tool selection
        self.agent_executor = self._create_agent_executor()
        
        logger.info("Minimal Saylor Lee LangChain service initialized with %d tools", len(self.tools))

    def _initialize_tools(self):
        """Initialize all Saylor Lee tools."""
        tools = []
        
        # Consent Tool
        def check_consent(context: str = "") -> str:
            return "Yes, I consent."
        
        tools.append(Tool(
            name="ConsentCheck",
            description="Use when asked for consent or permission",
            func=check_consent,
            return_direct=True
        ))
        
        # Wellness Tool
        def wellness_response(context: str = "") -> str:
            return "I'm doing well, thank you. How are you?"
        
        tools.append(Tool(
            name="WellnessResponse",
            description="Use when asked 'How are you?' or similar wellness questions",
            func=wellness_response,
            return_direct=True
        ))
        
        # Presenting Concern Tool
        def presenting_concern(context: str = "") -> str:
            return "Well, I moved from Ottawa to Montreal about six months ago. I'm new to this clinic and here for an initial check-up."
        
        tools.append(Tool(
            name="PresentingConcern",
            description="Use when asked 'What brings you in today?' or 'Why are you here?'",
            func=presenting_concern,
            return_direct=True
        ))
        
        # Name Tool
        def name_response(context: str = "") -> str:
            return "I'm Saylor Lee."
        
        tools.append(Tool(
            name="NameResponse",
            description="Use when asked for name or 'What's your name?'",
            func=name_response,
            return_direct=True
        
        ))
        
        # Age Tool
        def age_response(context: str = "") -> str:
            return "I'm 62 years old."
        
        tools.append(Tool(
            name="AgeResponse",
            description="Use when asked for age or 'How old are you?'",
            func=age_response,
            return_direct=True
        ))
        
        # Medical History Tool
        def medical_history(context: str = "") -> str:
            return "I was diagnosed with Type 2 Diabetes about 5 years ago. I've also experienced anxiety on and off with major life events and started treatment about 2 years ago. The medication has helped a lot."
        
        tools.append(Tool(
            name="MedicalHistory",
            description="Use when asked about medical history, health conditions, or medical problems",
            func=medical_history,
            return_direct=True
            
        ))
        
        # Medications Tool
        def medications(context: str = "") -> str:
            return "I take Metformin 500 mg twice daily for diabetes and Cipralex 10 mg daily for anxiety."
        
        tools.append(Tool(
            name="Medications",
            description="Use when asked about current medications or prescriptions",
            func=medications,
            return_direct=True
          
        ))
        
        # Allergies Tool
        def allergies(context: str = "") -> str:
            return "I'm allergic to peanuts."
        
        tools.append(Tool(
            name="Allergies",
            description="Use when asked about allergies or food allergies",
            func=allergies,
            return_direct=True
        ))
        
        # Family History Tool
        def family_history(context: str = "") -> str:
            return "My mother lives in Florida and has well-controlled type 2 diabetes. My father passed away 5 years ago from lung cancer. I have one sister around 62 who's healthy; we're close, and I'm close with my nieces and nephews—they get along with my partner. I don't know my grandparents' health history."
        
        tools.append(Tool(
            name="FamilyHistory",
            description="Use when asked about family medical history or family health",
            func=family_history,
            return_direct=True
        ))
        
        # Smoking/Vaping Tool
        def smoking_status(context: str = "") -> str:
            return "I currently vape. I don't have any other smoking history."
        
        tools.append(Tool(
            name="SmokingStatus",
            description="Use when asked about smoking, vaping, or tobacco use",
            func=smoking_status,
            return_direct=True
        ))
        
        # Alcohol Tool
        def alcohol_use(context: str = "") -> str:
            return "I usually have one beer or a glass of wine after work, sometimes two on weekends."
        
        tools.append(Tool(
            name="AlcoholUse",
            description="Use when asked about alcohol consumption or drinking",
            func=alcohol_use,
            return_direct=True
        ))
        
        # Exercise Tool
        def exercise_activities(context: str = "") -> str:
            return "My main physical activities are walking and golf. I used to walk 30 minutes every evening, but since moving into town I haven't walked as much. I'd like to get back to daily walks. I golf every Saturday over the summer months, mostly for networking."
        
        tools.append(Tool(
            name="ExerciseActivities",
            description="Use when asked about exercise, physical activities, or fitness routine",
            func=exercise_activities,
            return_direct=True
        ))
        
        # Sleep Tool
        def sleep_patterns(context: str = "") -> str:
            return "I usually get about 6 hours a night. I don't wake during the night, but I have trouble falling asleep because I make mental to-do lists."
        
        tools.append(Tool(
            name="SleepPatterns",
            description="Use when asked about sleep, sleep habits, or sleep quality",
            func=sleep_patterns,
            return_direct=True
        ))
        
        # Diet Tool
        def diet_nutrition(context: str = "") -> str:
            return "I made drastic changes after my diabetes diagnosis 5 years ago, worked with a diabetes team, and I'm following my partner's vegetarian diet. For breakfast, I had oatmeal with fresh berries. Lunch was lentil soup with a mixed green salad. Dinner was a vegetable stir-fry with tofu. I snack on nuts and fruit throughout the day."
        
        tools.append(Tool(
            name="DietNutrition",
            description="Use when asked about diet, nutrition, or food intake",
            func=diet_nutrition,
            return_direct=True
        ))
        
        # Headaches Tool
        def headaches(context: str = "") -> str:
            return "I get headaches about once per month and take Tylenol. No other head, eye, ear, nose, or throat issues."
        
        tools.append(Tool(
            name="Headaches",
            description="Use when asked about headaches or HEENT symptoms",
            func=headaches,
            return_direct=True
        ))
        
        # Respiratory Tool
        def respiratory(context: str = "") -> str:
            return "I don't have any respiratory issues."
        
        tools.append(Tool(
            name="Respiratory",
            description="Use when asked about breathing, respiratory issues, or lung problems",
            func=respiratory,
            return_direct=True
        ))
        
        # Advanced Care Planning Tool
        def advanced_care_planning(context: str = "") -> str:
            return "No one has ever talked to me about advanced care planning. I'd like more information."
        
        tools.append(Tool(
            name="AdvancedCarePlanning",
            description="Use when asked about advanced care planning or end-of-life planning",
            func=advanced_care_planning,
            return_direct=True
        ))
        
        # Cholesterol Tool (ONLY IF EXPLICITLY ASKED)
        def cholesterol_history(context: str = "") -> str:
            return "I was diagnosed with high cholesterol at the same time as my diabetes."
        
        tools.append(Tool(
            name="CholesterolHistory",
            description="ONLY use when explicitly asked about cholesterol or high cholesterol",
            func=cholesterol_history,
            return_direct=True
        ))
        
        # Surgical History Tool
        def surgical_history(context: str = "") -> str:
            return "I had my appendix removed when I was 20. No complications."
        
        tools.append(Tool(
            name="SurgicalHistory",
            description="Use when asked about surgical history or previous surgeries",
            func=surgical_history,
            return_direct=True
        ))
        
        # Obstetrical History Tool
        def obstetrical_history(context: str = "") -> str:
            return "I've never been pregnant; no miscarriages or abortions."
        
        tools.append(Tool(
            name="ObstetricalHistory",
            description="Use when asked about pregnancy history or obstetrical history",
            func=obstetrical_history,
            return_direct=True
        ))
        
        # Recent Medical Exam Tool
        def recent_medical_exam(context: str = "") -> str:
            return "My last medical exam was 6 months ago for a routine diabetes follow-up. Since moving, I haven't seen anyone here yet."
        
        tools.append(Tool(
            name="RecentMedicalExam",
            description="Use when asked about recent medical exams or access to healthcare",
            func=recent_medical_exam,
            return_direct=True
        ))
        
        # OTC Medications Tool
        def otc_medications(context: str = "") -> str:
            return "I take Tylenol for headaches about once a month—650 mg (two tablets)."
        
        tools.append(Tool(
            name="OTCMedications",
            description="Use when asked about over-the-counter medications or pain relievers",
            func=otc_medications,
            return_direct=True
        ))
        
        # Supplements Tool
        def supplements(context: str = "") -> str:
            return "I don't take any herbal supplements or natural products."
        
        tools.append(Tool(
            name="Supplements",
            description="Use when asked about supplements, vitamins, or herbal products",
            func=supplements,
            return_direct=True
        ))
        
        # Non-prescription Medications Tool (combines OTC + supplements)
        def nonprescription_medications(context: str = "") -> str:
            return "I take Tylenol for headaches about once a month—650 mg (two tablets). I don't take any herbal supplements or natural products."
        
        tools.append(Tool(
            name="NonprescriptionMedications",
            description="Use when asked about non-prescription medications generally",
            func=nonprescription_medications,
            return_direct=True
        ))
        
        # Allergic Reaction Tool (ONLY IF EXPLICITLY ASKED)
        def allergic_reaction(context: str = "") -> str:
            return "My last reaction was a few years ago—facial swelling and difficulty breathing."
        
        tools.append(Tool(
            name="AllergicReaction",
            description="ONLY use when explicitly asked about allergic reaction symptoms",
            func=allergic_reaction,
            return_direct=True
        ))
        
        # Epipen Tool (ONLY IF EXPLICITLY ASKED)
        def epipen_info(context: str = "") -> str:
            return "I don't carry an epi-pen, but I know how to use one—'Orange to the thigh and blue to the sky.'"
        
        tools.append(Tool(
            name="EpipenInfo",
            description="ONLY use when explicitly asked about epipen or auto-injector",
            func=epipen_info,
            return_direct=True
        ))
        
        # Medic Alert Bracelet Tool (ONLY IF EXPLICITLY ASKED)
        def medic_alert_bracelet(context: str = "") -> str:
            return "I don't wear a medic alert bracelet."
        
        tools.append(Tool(
            name="MedicAlertBracelet",
            description="ONLY use when explicitly asked about medic alert bracelet",
            func=medic_alert_bracelet,
            return_direct=True
        ))
        
        # Medication Allergies Tool
        def medication_allergies(context: str = "") -> str:
            return "I don't have any medication allergies."
        
        tools.append(Tool(
            name="MedicationAllergies",
            description="Use when asked about medication allergies or drug allergies",
            func=medication_allergies,
            return_direct=True
        ))
        
        # Environmental Allergies Tool
        def environmental_allergies(context: str = "") -> str:
            return "I don't have any environmental allergies."
        
        tools.append(Tool(
            name="EnvironmentalAllergies",
            description="Use when asked about environmental allergies or seasonal allergies",
            func=environmental_allergies,
            return_direct=True
        ))
        
        # Communicable Diseases Tool
        def communicable_diseases(context: str = "") -> str:
            return "I don't have any history of communicable diseases."
        
        tools.append(Tool(
            name="CommunicableDiseases",
            description="Use when asked about communicable diseases or infectious diseases",
            func=communicable_diseases,
            return_direct=True
        ))
        
        # STBBI Testing Tool (ONLY IF EXPLICITLY ASKED)
        def stbbi_testing(context: str = "") -> str:
            return "My partner and I were tested two years ago, and all results were negative."
        
        tools.append(Tool(
            name="STBBITesting",
            description="ONLY use when explicitly asked about STI/STD/STBBI testing",
            func=stbbi_testing,
            return_direct=True
        ))
        
        # Immunization Status Tool
        def immunization_status(context: str = "") -> str:
            return "I keep my vaccines up to date and plan to get the flu shot this year."
        
        tools.append(Tool(
            name="ImmunizationStatus",
            description="Use when asked about immunization status or vaccines",
            func=immunization_status,
            return_direct=True
        ))
        
        # Immunization Details Tool (ONLY IF EXPLICITLY ASKED)
        def immunization_details(context: str = "") -> str:
            return "My last immunization was the flu vaccine last fall. I'm not sure how to get my vaccines here in Montreal since moving."
        
        tools.append(Tool(
            name="ImmunizationDetails",
            description="ONLY use when explicitly asked about immunization dates or access",
            func=immunization_details,
            return_direct=True
        ))
        
        # Cough Tool (ONLY IF EXPLICITLY ASKED)
        def cough_status(context: str = "") -> str:
            return "No, I don't have a cough."
        
        tools.append(Tool(
            name="CoughStatus",
            description="ONLY use when explicitly asked about cough",
            func=cough_status,
            return_direct=True
        ))
        
        # Cardiovascular Tool
        def cardiovascular(context: str = "") -> str:
            return "I don't have any cardiovascular issues."
        
        tools.append(Tool(
            name="Cardiovascular",
            description="Use when asked about cardiovascular system or heart health",
            func=cardiovascular,
            return_direct=True
        ))
        
        # Peripheral Vascular Tool
        def peripheral_vascular(context: str = "") -> str:
            return "I don't have any peripheral vascular issues."
        
        tools.append(Tool(
            name="PeripheralVascular",
            description="Use when asked about peripheral vascular system or circulation",
            func=peripheral_vascular,
            return_direct=True
        ))
        
        # Genitourinary Tool
        def genitourinary(context: str = "") -> str:
            return "I don't have any genitourinary issues."
        
        tools.append(Tool(
            name="Genitourinary",
            description="Use when asked about genitourinary system or urinary function",
            func=genitourinary,
            return_direct=True
        ))
        
        # Musculoskeletal Tool
        def musculoskeletal(context: str = "") -> str:
            return "I don't have any musculoskeletal issues."
        
        tools.append(Tool(
            name="Musculoskeletal",
            description="Use when asked about musculoskeletal system or bones/joints",
            func=musculoskeletal,
            return_direct=True
        ))
        
        # Neurological Tool
        def neurological(context: str = "") -> str:
            return "I don't have any neurological issues."
        
        tools.append(Tool(
            name="Neurological",
            description="Use when asked about neurological system or nervous system",
            func=neurological,
            return_direct=True
        ))
        
        # Endocrine General Tool
        def endocrine_general(context: str = "") -> str:
            return "I have diabetes, but it's well-controlled."
        
        tools.append(Tool(
            name="EndocrineGeneral",
            description="Use when asked about endocrine system or diabetes status",
            func=endocrine_general,
            return_direct=True
        ))
        
        # Endocrine Symptoms Tool (ONLY IF EXPLICITLY ASKED)
        def endocrine_symptoms(context: str = "") -> str:
            return "No, I haven't had any unintentional weight loss, fever, chills, or night sweats."
        
        tools.append(Tool(
            name="EndocrineSymptoms",
            description="ONLY use when explicitly asked about endocrine symptoms (weight loss, fever, chills, night sweats)",
            func=endocrine_symptoms,
            return_direct=True
        ))
        
        # Elimination Tool
        def elimination(context: str = "") -> str:
            return "I have regular daily bowel movements—formed—with no urinary issues."
        
        tools.append(Tool(
            name="Elimination",
            description="Use when asked about bowel movements or elimination patterns",
            func=elimination,
            return_direct=True
        ))
        
        # Nutrition General Tool
        def nutrition_general(context: str = "") -> str:
            return "I made drastic changes after my diabetes diagnosis 5 years ago, worked with a diabetes team, and I'm following my partner's vegetarian diet."
        
        tools.append(Tool(
            name="NutritionGeneral",
            description="Use when asked about general nutrition or dietary changes",
            func=nutrition_general,
            return_direct=True
        ))
        
        # 24-Hour Diet Recall Tool (ONLY IF EXPLICITLY ASKED)
        def diet_recall_24hr(context: str = "") -> str:
            return "Breakfast: oatmeal with fresh berries. Lunch: lentil soup with a mixed green salad. Dinner: vegetable stir-fry with tofu. Snacks: nuts and fruit."
        
        tools.append(Tool(
            name="DietRecall24hr",
            description="ONLY use when explicitly asked about 24-hour diet recall or food diary",
            func=diet_recall_24hr,
            return_direct=True
        ))
        
        # Walking Details Tool (ONLY IF EXPLICITLY ASKED)
        def walking_details(context: str = "") -> str:
            return "I used to walk 30 minutes every evening, but since moving into town I haven't walked as much. I'd like to get back to daily walks."
        
        tools.append(Tool(
            name="WalkingDetails",
            description="ONLY use when explicitly asked about walking routine or habits",
            func=walking_details,
            return_direct=True
        ))
        
        # Golf Details Tool (ONLY IF EXPLICITLY ASKED)
        def golf_details(context: str = "") -> str:
            return "I golf every Saturday over the summer months, mostly for networking."
        
        tools.append(Tool(
            name="GolfDetails",
            description="ONLY use when explicitly asked about golfing habits",
            func=golf_details,
            return_direct=True
        ))
        
        # Mobility Tool
        def mobility(context: str = "") -> str:
            return "I don't have any mobility issues."
        
        tools.append(Tool(
            name="Mobility",
            description="Use when asked about mobility or movement capabilities",
            func=mobility,
            return_direct=True
        ))
        
        # Assistive Devices Tool
        def assistive_devices(context: str = "") -> str:
            return "I don't need any assistive devices."
        
        tools.append(Tool(
            name="AssistiveDevices",
            description="Use when asked about assistive devices or mobility aids",
            func=assistive_devices,
            return_direct=True
        ))
        
        # Skin/Hair Tool
        def skin_hair(context: str = "") -> str:
            return "I don't have skin issues, but I've noticed a little hair thinning and some hair loss in the shower."
        
        tools.append(Tool(
            name="SkinHair",
            description="Use when asked about skin condition or hair health",
            func=skin_hair,
            return_direct=True
        ))
        
        # Nail Clubbing Tool (ONLY IF EXPLICITLY ASKED)
        def nail_clubbing(context: str = "") -> str:
            return "No, I don't have any nail clubbing."
        
        tools.append(Tool(
            name="NailClubbing",
            description="ONLY use when explicitly asked about nail clubbing",
            func=nail_clubbing,
            return_direct=True
        ))
        
        # Foot Sensation Tool (ONLY IF EXPLICITLY ASKED)
        def foot_sensation(context: str = "") -> str:
            return "No numbness, tingling, or loss of sensation in my feet."
        
        tools.append(Tool(
            name="FootSensation",
            description="ONLY use when explicitly asked about foot sensation or neuropathy",
            func=foot_sensation,
            return_direct=True
        ))
        
        # Vision Changes Tool (ONLY IF EXPLICITLY ASKED)
        def vision_changes(context: str = "") -> str:
            return "I haven't noticed any changes in my vision."
        
        tools.append(Tool(
            name="VisionChanges",
            description="ONLY use when explicitly asked about vision changes",
            func=vision_changes,
            return_direct=True
        ))
        
        # Mental Health Current Tool
        def mental_health_current(context: str = "") -> str:
            return "No other mental health concerns beyond the anxiety I mentioned, which is treated with medication."
        
        tools.append(Tool(
            name="MentalHealthCurrent",
            description="Use when asked about current mental health status",
            func=mental_health_current,
            return_direct=True
        ))
        
        # Coping Strategies Tool
        def coping_strategies(context: str = "") -> str:
            return "I need to use coping strategies more. I used to like going for walks but haven't prioritized that lately. I've heard of journaling but haven't tried it."
        
        tools.append(Tool(
            name="CopingStrategies",
            description="Use when asked about coping strategies or stress management",
            func=coping_strategies,
            return_direct=True
        ))
        
        # Vaping Details Tool (ONLY IF EXPLICITLY ASKED)
        def vaping_details(context: str = "") -> str:
            return "I go through about one nicotine cartridge per day and have been vaping for 5 years. It used to help with stress."
        
        tools.append(Tool(
            name="VapingDetails",
            description="ONLY use when explicitly asked about vaping details or frequency",
            func=vaping_details,
            return_direct=True
        ))
        
        # Substances Tool
        def substances(context: str = "") -> str:
            return "I've never used any substances."
        
        tools.append(Tool(
            name="Substances",
            description="Use when asked about substance use or recreational drugs",
            func=substances,
            return_direct=True
        ))
        
        # Environmental Hazards Tool
        def environmental_hazards(context: str = "") -> str:
            return "I don't have any environmental hazards."
        
        tools.append(Tool(
            name="EnvironmentalHazards",
            description="Use when asked about environmental hazards or exposure risks",
            func=environmental_hazards,
            return_direct=True
        ))
        
        # Sexual Health Tool
        def sexual_health(context: str = "") -> str:
            return "I'm in a monogamous relationship. My last STBBI test was 2 years ago and it was negative. I don't use contraception or protective barriers."
        
        tools.append(Tool(
            name="SexualHealth",
            description="Use when asked about sexual health or relationships",
            func=sexual_health,
            return_direct=True
        ))
        
        # Financial Status Tool
        def financial_status(context: str = "") -> str:
            return "I don't have any financial issues."
        
        tools.append(Tool(
            name="FinancialStatus",
            description="Use when asked about financial situation or economic status",
            func=financial_status,
            return_direct=True
        ))
        
        # Relationships Tool
        def relationships(context: str = "") -> str:
            return "I've been in a committed relationship for about 32 years—it's a good relationship. We have a supportive family, lots of friends and community, and I like my new colleagues. We don't have children."
        
        tools.append(Tool(
            name="Relationships",
            description="Use when asked about relationships or social support",
            func=relationships,
            return_direct=True
        ))
        
        # Spiritual Resources Tool
        def spiritual_resources(context: str = "") -> str:
            return "I don't have any spiritual resources."
        
        tools.append(Tool(
            name="SpiritualResources",
            description="Use when asked about spirituality or religious practices",
            func=spiritual_resources,
            return_direct=True
        ))
        
        # Advanced Care Planning Details Tool (ONLY IF EXPLICITLY ASKED)
        def advanced_care_planning_details(context: str = "") -> str:
            return "I've assumed my partner would be my medical power of attorney. I have an up-to-date will. I don't have any code status established. No other concerns."
        
        tools.append(Tool(
            name="AdvancedCarePlanningDetails",
            description="ONLY use when explicitly asked about specific advanced care planning details",
            func=advanced_care_planning_details,
            return_direct=True
        ))
        
        return tools

    def _create_agent_executor(self):
        """Create an agent executor with proper tool selection."""
        from langchain.agents import create_openai_functions_agent
        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
        
        # Create the system prompt with required variables
        system_prompt = """
        You are Saylor Lee, a 62-year-old patient in a primary care clinic. 
        You are here for an initial check-up after moving from Ottawa to Montreal 6 months ago.
        
        You have access to various tools that contain specific information about your medical history, 
        medications, lifestyle, and other health-related topics. Use the appropriate tool to answer 
        the doctor's questions accurately and consistently.
        
        If a question doesn't match any specific tool, respond naturally as a patient would.
        
        Always respond as Saylor Lee would - be conversational, helpful, and provide accurate 
        information based on your medical profile.
        """
        
        # Create the prompt template with required variables
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create the agent
        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        # Create the agent executor
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,  # This will show tool selection
            return_intermediate_steps=True,  # This will return which tools were called
            handle_parsing_errors=True
        )
        
        return agent_executor

    def _select_tool(self, message: str) -> Optional[Tool]:
        """Select the most appropriate tool based on the message."""
        message_lower = message.lower()
        
        # Tool selection logic based on keywords (order matters - more specific first)
        if any(word in message_lower for word in ['consent', 'permission', 'agree']):
            return self.get_tool_by_name("ConsentCheck")
        elif any(word in message_lower for word in ['what brings you', 'why are you here', 'chief complaint']):
            return self.get_tool_by_name("PresentingConcern")
        elif any(word in message_lower for word in ['family history', 'family medical', 'parents', 'siblings', 'tell me about your family']):
            return self.get_tool_by_name("FamilyHistory")
        elif any(word in message_lower for word in ['breathing problems', 'breathing', 'respiratory', 'lung']):
            return self.get_tool_by_name("Respiratory")
        elif any(word in message_lower for word in ['cough']):
            return self.get_tool_by_name("CoughStatus")
        elif any(word in message_lower for word in ['cholesterol', 'high cholesterol']):
            return self.get_tool_by_name("CholesterolHistory")
        elif any(word in message_lower for word in ['surgical history', 'surgeries', 'surgery', 'appendix']):
            return self.get_tool_by_name("SurgicalHistory")
        elif any(word in message_lower for word in ['pregnancy', 'pregnant', 'obstetrical', 'miscarriage', 'abortion']):
            return self.get_tool_by_name("ObstetricalHistory")
        elif any(word in message_lower for word in ['recent exam', 'last exam', 'medical exam', 'healthcare access']):
            return self.get_tool_by_name("RecentMedicalExam")
        elif any(word in message_lower for word in ['otc', 'over the counter', 'tylenol', 'pain reliever']):
            return self.get_tool_by_name("OTCMedications")
        elif any(word in message_lower for word in ['supplements', 'vitamins', 'herbal', 'natural products']):
            return self.get_tool_by_name("Supplements")
        elif any(word in message_lower for word in ['non-prescription', 'non prescription']):
            return self.get_tool_by_name("NonprescriptionMedications")
        elif any(word in message_lower for word in ['allergic reaction', 'reaction symptoms', 'swelling', 'difficulty breathing']):
            return self.get_tool_by_name("AllergicReaction")
        elif any(word in message_lower for word in ['epipen', 'epi-pen', 'auto-injector', 'injector']):
            return self.get_tool_by_name("EpipenInfo")
        elif any(word in message_lower for word in ['medic alert', 'medical alert', 'bracelet', 'medical id']):
            return self.get_tool_by_name("MedicAlertBracelet")
        elif any(word in message_lower for word in ['medication allergies', 'drug allergies']):
            return self.get_tool_by_name("MedicationAllergies")
        elif any(word in message_lower for word in ['environmental allergies', 'seasonal allergies', 'pollen', 'dust']):
            return self.get_tool_by_name("EnvironmentalAllergies")
        elif any(word in message_lower for word in ['communicable diseases', 'infectious diseases']):
            return self.get_tool_by_name("CommunicableDiseases")
        elif any(word in message_lower for word in ['sti', 'std', 'stbbi', 'sexually transmitted']):
            return self.get_tool_by_name("STBBITesting")
        elif any(word in message_lower for word in ['immunization', 'vaccines', 'vaccination']):
            return self.get_tool_by_name("ImmunizationStatus")
        elif any(word in message_lower for word in ['immunization dates', 'vaccine dates', 'flu shot', 'montreal vaccines']):
            return self.get_tool_by_name("ImmunizationDetails")
        elif any(word in message_lower for word in ['cardiovascular', 'heart', 'cardiac']):
            return self.get_tool_by_name("Cardiovascular")
        elif any(word in message_lower for word in ['peripheral vascular', 'circulation', 'peripheral']):
            return self.get_tool_by_name("PeripheralVascular")
        elif any(word in message_lower for word in ['genitourinary', 'urinary', 'bladder', 'kidney']):
            return self.get_tool_by_name("Genitourinary")
        elif any(word in message_lower for word in ['musculoskeletal', 'bones', 'joints', 'muscles']):
            return self.get_tool_by_name("Musculoskeletal")
        elif any(word in message_lower for word in ['neurological', 'nervous system', 'neurological issues']):
            return self.get_tool_by_name("Neurological")
        elif any(word in message_lower for word in ['endocrine', 'diabetes status', 'diabetes control']):
            return self.get_tool_by_name("EndocrineGeneral")
        elif any(word in message_lower for word in ['weight loss', 'fever', 'chills', 'night sweats', 'endocrine symptoms']):
            return self.get_tool_by_name("EndocrineSymptoms")
        elif any(word in message_lower for word in ['elimination', 'bowel movements', 'urinary issues']):
            return self.get_tool_by_name("Elimination")
        elif any(word in message_lower for word in ['nutrition', 'dietary changes', 'diabetes team', 'vegetarian']):
            return self.get_tool_by_name("NutritionGeneral")
        elif any(word in message_lower for word in ['24 hour recall', 'food diary', 'what did you eat', 'yesterday']):
            return self.get_tool_by_name("DietRecall24hr")
        elif any(word in message_lower for word in ['walking routine', 'walking habits', 'walking details']):
            return self.get_tool_by_name("WalkingDetails")
        elif any(word in message_lower for word in ['golf details', 'golfing habits', 'golf frequency']):
            return self.get_tool_by_name("GolfDetails")
        elif any(word in message_lower for word in ['mobility', 'movement', 'mobility issues']):
            return self.get_tool_by_name("Mobility")
        elif any(word in message_lower for word in ['assistive devices', 'mobility aids', 'support equipment']):
            return self.get_tool_by_name("AssistiveDevices")
        elif any(word in message_lower for word in ['skin', 'hair', 'hair thinning', 'hair loss']):
            return self.get_tool_by_name("SkinHair")
        elif any(word in message_lower for word in ['nail clubbing']):
            return self.get_tool_by_name("NailClubbing")
        elif any(word in message_lower for word in ['foot sensation', 'numbness', 'tingling', 'neuropathy']):
            return self.get_tool_by_name("FootSensation")
        elif any(word in message_lower for word in ['vision', 'visual', 'vision changes', 'visual symptoms']):
            return self.get_tool_by_name("VisionChanges")
        elif any(word in message_lower for word in ['mental health', 'psychological', 'mental health status']):
            return self.get_tool_by_name("MentalHealthCurrent")
        elif any(word in message_lower for word in ['coping', 'stress management', 'coping strategies']):
            return self.get_tool_by_name("CopingStrategies")
        elif any(word in message_lower for word in ['vaping details', 'vaping frequency', 'cartridge', 'nicotine']):
            return self.get_tool_by_name("VapingDetails")
        elif any(word in message_lower for word in ['substances', 'recreational drugs', 'drug use', 'substance use']):
            return self.get_tool_by_name("Substances")
        elif any(word in message_lower for word in ['environmental hazards', 'exposure risks']):
            return self.get_tool_by_name("EnvironmentalHazards")
        elif any(word in message_lower for word in ['sexual health', 'relationships', 'contraception']):
            return self.get_tool_by_name("SexualHealth")
        elif any(word in message_lower for word in ['financial', 'economic', 'financial issues']):
            return self.get_tool_by_name("FinancialStatus")
        elif any(word in message_lower for word in ['relationships', 'social support', 'committed relationship']):
            return self.get_tool_by_name("Relationships")
        elif any(word in message_lower for word in ['spiritual', 'religious', 'spiritual resources']):
            return self.get_tool_by_name("SpiritualResources")
        elif any(word in message_lower for word in ['advanced care planning details', 'power of attorney', 'will', 'code status']):
            return self.get_tool_by_name("AdvancedCarePlanningDetails")
        elif any(word in message_lower for word in ['medical history', 'medical conditions', 'health problems', 'conditions']):
            return self.get_tool_by_name("MedicalHistory")
        elif any(word in message_lower for word in ['medications', 'medicines', 'pills', 'prescriptions']):
            return self.get_tool_by_name("Medications")
        elif any(word in message_lower for word in ['allergies', 'allergic', 'allergy']):
            return self.get_tool_by_name("Allergies")
        elif any(word in message_lower for word in ['smoke', 'smoking', 'vape', 'vaping', 'tobacco']):
            return self.get_tool_by_name("SmokingStatus")
        elif any(word in message_lower for word in ['alcohol', 'drink', 'drinking', 'beer', 'wine']):
            return self.get_tool_by_name("AlcoholUse")
        elif any(word in message_lower for word in ['exercise', 'physical activity', 'walking', 'golf', 'fitness']):
            return self.get_tool_by_name("ExerciseActivities")
        elif any(word in message_lower for word in ['sleep', 'sleeping', 'sleep quality']):
            return self.get_tool_by_name("SleepPatterns")
        elif any(word in message_lower for word in ['diet', 'nutrition', 'food', 'eating', 'meals']):
            return self.get_tool_by_name("DietNutrition")
        elif any(word in message_lower for word in ['headache', 'headaches', 'head pain']):
            return self.get_tool_by_name("Headaches")
        elif any(word in message_lower for word in ['advanced care', 'end of life', 'advanced care planning']):
            return self.get_tool_by_name("AdvancedCarePlanning")
        elif any(word in message_lower for word in ['name', 'what\'s your name', 'who are you']):
            return self.get_tool_by_name("NameResponse")
        elif any(word in message_lower for word in ['age', 'how old', 'old are you']):
            return self.get_tool_by_name("AgeResponse")
        elif any(word in message_lower for word in ['how are you', 'how do you feel', 'hello', 'hi']):
            return self.get_tool_by_name("WellnessResponse")
        
        return None

    async def chat_with_patient(self, message: str, verbose: bool = False) -> str:
        """Chat with patient using LangChain agent with tool selection."""
        try:
            if verbose:
                print(f"🔍 INPUT: '{message}'")
            
            logger.debug("LangChain agent chat request - Message: %s", message)
            
            # Use the agent executor to handle tool selection
            result = await self.agent_executor.ainvoke({
                "input": message
            })
            
            # Extract the response
            response = result.get("output", "")
            
            if verbose:
                # Show which tools were called
                intermediate_steps = result.get("intermediate_steps", [])
                if intermediate_steps:
                    print(f"🛠️  TOOLS CALLED:")
                    for step in intermediate_steps:
                        action = step[0]
                        tool_name = action.tool
                        tool_input = action.tool_input
                        observation = step[1]
                        print(f"   - {tool_name}: {tool_input}")
                        print(f"     Response: {observation}")
                    print(f"✅ RESPONSE SOURCE: LangChain agent with tools")
                else:
                    print(f"🤖 NO TOOLS CALLED: Direct LLM response")
                    print(f"✅ RESPONSE SOURCE: LangChain agent (no tools)")
                
                print(f"💬 FINAL RESPONSE: '{response}'")
            
            return response
                
        except Exception as e:
            logger.error("Error in LangChain agent chat: %s", str(e), exc_info=True)
            if verbose:
                print(f"❌ ERROR: {str(e)}")
            raise

    def get_tool_by_name(self, tool_name: str) -> Optional[Tool]:
        """Get a specific tool by name."""
        for tool in self.tools:
            if tool.name == tool_name:
                return tool
        return None

    def list_tools(self) -> list:
        """List all available tools."""
        return [{"name": tool.name, "description": tool.description} for tool in self.tools]
