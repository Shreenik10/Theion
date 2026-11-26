from SaylorLeeTools import *

def run_sample_conversation():
    # Initial Greeting and Purpose
    print("\nNurse: Hello, I'm the nurse who will be doing your initial assessment today. How are you doing?")
    print("Saylor:", wellness_tool.func())

    print("\nNurse: What brings you in today?")
    print("Saylor:", presenting_concern_tool.func())

    print("\nNurse: Before we begin, I need your consent to proceed with the assessment.")
    print("Saylor:", consent_tool.func())

    # Medical History and Conditions
    print("\nNurse: Let's start with your medical history. Do you have any ongoing medical conditions?")
    print("Saylor:", medical_history_tool.func())

    print("\nNurse: What medications are you currently taking?")
    print("Saylor:", medication_history_tool.func())

    print("\nNurse: Do you take any over-the-counter medications?")
    print("Saylor:", otc_medication_tool.func())

    print("\nNurse: How about any supplements or herbal products?")
    print("Saylor:", supplements_tool.func())

    # Allergies
    print("\nNurse: Do you have any allergies?")
    print("Saylor:", food_allergies_tool.func())

    print("\nNurse: Can you tell me what happens when you have an allergic reaction?")
    print("Saylor:", allergy_reaction_tool.func())

    print("\nNurse: Do you carry an epipen?")
    print("Saylor:", epipen_tool.func())

    print("\nNurse: Any medication allergies?")
    print("Saylor:", medication_allergies_tool.func())

    print("\nNurse: Any environmental allergies?")
    print("Saylor:", environmental_allergies_tool.func())

    # Systems Review
    print("\nNurse: Let's do a review of your body systems. How's your head, eyes, ears, nose, and throat?")
    print("Saylor:", heent_status_tool.func())

    print("\nNurse: How about your breathing?")
    print("Saylor:", respiratory_basic_tool.func())

    print("\nNurse: Any heart problems?")
    print("Saylor:", cardiovascular_tool.func())

    print("\nNurse: Any circulation problems?")
    print("Saylor:", peripheral_vascular_tool.func())

    print("\nNurse: How about your bowel movements and urination?")
    print("Saylor:", elimination_patterns_tool.func())

    print("\nNurse: Any muscle or joint problems?")
    print("Saylor:", musculoskeletal_tool.func())

    print("\nNurse: Any neurological issues?")
    print("Saylor:", neurological_tool.func())

    # Skin Assessment
    print("\nNurse: How's your skin?")
    print("Saylor:", skin_hair_basic_tool.func())

    print("\nNurse: Any numbness or tingling in your feet?")
    print("Saylor:", foot_sensation_tool.func())

    # Mobility
    print("\nNurse: Do you have any mobility issues?")
    print("Saylor:", mobility_status_tool.func())

    print("\nNurse: Do you use any assistive devices?")
    print("Saylor:", assistive_devices_tool.func())

    # Lifestyle and Activities
    print("\nNurse: What physical activities do you do?")
    print("Saylor:", basic_activity_tool.func())

    print("\nNurse: Can you tell me more about your walking routine?")
    print("Saylor:", walking_details_tool.func())

    print("\nNurse: How's your sleep?")
    print("Saylor:", sleep_patterns_tool.func())

    # Substance Use
    print("\nNurse: Do you smoke or use any tobacco products?")
    print("Saylor:", smoking_status_tool.func())

    print("\nNurse: Can you tell me more about your vaping?")
    print("Saylor:", vaping_details_tool.func())

    print("\nNurse: How about alcohol use?")
    print("Saylor:", alcohol_use_tool.func())

    print("\nNurse: Any recreational drug use?")
    print("Saylor:", substance_use_tool.func())

    # Nutrition and Diabetes Management
    print("\nNurse: Let's talk about your diabetes management. How's that going?")
    print("Saylor:", endocrine_basic_tool.func())

    print("\nNurse: Have you had any unintentional weight loss, fever, chills, or night sweats?")
    print("Saylor:", endocrine_symptoms_tool.func())

    print("\nNurse: Tell me about your diet.")
    print("Saylor:", nutrition_info_tool.func())

    print("\nNurse: Can you give me an example of what you eat in a typical day?")
    print("Saylor:", diet_recall_tool.func())

    # Mental Health and Coping
    print("\nNurse: How's your mental health?")
    print("Saylor:", mental_health_tool.func())

    print("\nNurse: How do you manage stress?")
    print("Saylor:", coping_strategies_tool.func())

    # Social History
    print("\nNurse: Tell me about your support system and relationships.")
    print("Saylor:", interpersonal_relationships_tool.func())

    print("\nNurse: Do you have any spiritual resources?")
    print("Saylor:", spiritual_resources_tool.func())

    print("\nNurse: Any financial concerns?")
    print("Saylor:", financial_status_tool.func())

    # Sexual Health
    print("\nNurse: Let me ask about your sexual health.")
    print("Saylor:", sexual_health_tool.func())

    # Family History
    print("\nNurse: What's your family health history?")
    print("Saylor:", family_health_history_tool.func())

    # Past Medical History
    print("\nNurse: Have you had any surgeries?")
    print("Saylor:", surgical_history_tool.func())

    print("\nNurse: Any history of communicable diseases?")
    print("Saylor:", communicable_diseases_tool.func())

    print("\nNurse: Any childhood illnesses?")
    print("Saylor:", childhood_illnesses_tool.func())

    # Health Maintenance
    print("\nNurse: When was your last medical examination?")
    print("Saylor:", recent_medical_exam_tool.func())

    print("\nNurse: Are your immunizations up to date?")
    print("Saylor:", immunization_status_tool.func())

    # Safety
    print("\nNurse: Any environmental hazards at home or work?")
    print("Saylor:", environmental_hazards_tool.func())

    # Advanced Care Planning
    print("\nNurse: Have you done any advanced care planning?")
    print("Saylor:", advanced_care_basic_tool.func())

    print("\nNurse: Thank you for providing all this information. Is there anything else you'd like to discuss?")
    print("Saylor: No, I think we've covered everything. Thank you.")

if __name__ == "__main__":
    print("\n=== Sample Conversation with Saylor Lee ===")
    run_sample_conversation()
    print("\n=== End of Conversation ===\n") 