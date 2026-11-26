from SaylorLeeTools import *

def run_sample_conversation():
    print("\nNurse: Hi there! I'll be conducting your intake assessment today. How's your day going?")
    print("Saylor:", wellness_tool.func())

    print("\nNurse: Could you tell me what made you decide to come to our clinic?")
    print("Saylor:", presenting_concern_tool.func())

    print("\nNurse: I'll need your permission to go ahead with the assessment - is that okay?")
    print("Saylor:", consent_tool.func())

    print("\nNurse: Could you walk me through any health conditions you're managing right now? I see you have diabetes - how's that going, and do you have any symptoms like unexplained weight loss, fevers, night sweats, or other concerns?")
    print("Saylor:", medical_history_tool.func())
    print("Saylor:", endocrine_symptoms_tool.func())

    print("\nNurse: What medications do you take regularly, including any over-the-counter medicines or supplements?")
    print("Saylor:", medication_history_tool.func())
    print("Saylor:", otc_medication_tool.func())
    print("Saylor:", supplements_tool.func())

    print("\nNurse: Regarding allergies - do you have any food allergies, and if so, have you had any severe reactions? Do you carry an epipen or wear a medical alert bracelet?")
    print("Saylor:", food_allergies_tool.func())
    print("Saylor:", allergy_reaction_tool.func())
    print("Saylor:", epipen_tool.func())
    print("Saylor:", medic_alert_tool.func())

    print("\nNurse: Any other allergies we should know about - medications or environmental triggers?")
    print("Saylor:", medication_allergies_tool.func())
    print("Saylor:", environmental_allergies_tool.func())

    print("\nNurse: Let's check your general health. Any issues with headaches, vision changes, or other concerns with your head and neck? Also, do you have any nail clubbing or foot numbness we should know about?")
    print("Saylor:", heent_status_tool.func())
    print("Saylor:", nail_clubbing_tool.func())
    print("Saylor:", foot_sensation_tool.func())

    print("\nNurse: How's your breathing and heart health? Any coughing or circulation problems?")
    print("Saylor:", respiratory_basic_tool.func())
    print("Saylor:", cough_status_tool.func())
    print("Saylor:", cardiovascular_tool.func())
    print("Saylor:", peripheral_vascular_tool.func())

    print("\nNurse: Tell me about your bathroom habits - any concerns with bowel movements or urination?")
    print("Saylor:", elimination_patterns_tool.func())

    print("\nNurse: Do you have any problems with your muscles, joints, or nervous system?")
    print("Saylor:", musculoskeletal_tool.func())
    print("Saylor:", neurological_tool.func())

    print("\nNurse: I notice some hair changes - can you tell me about your skin and hair health?")
    print("Saylor:", skin_hair_basic_tool.func())

    print("\nNurse: How do you get around? Any mobility issues or need for assistive devices?")
    print("Saylor:", mobility_status_tool.func())
    print("Saylor:", assistive_devices_tool.func())

    print("\nNurse: Tell me about your exercise routine. I understand you enjoy walking and golf - could you elaborate on both?")
    print("Saylor:", walking_golf_tool.func())

    print("\nNurse: How's your sleep pattern? And what about stress management?")
    print("Saylor:", sleep_patterns_tool.func())
    print("Saylor:", coping_strategies_tool.func())

    print("\nNurse: Regarding lifestyle habits - do you use any tobacco products or vape? How often? And what about alcohol consumption?")
    print("Saylor:", smoking_status_tool.func())
    print("Saylor:", vaping_details_tool.func())
    print("Saylor:", alcohol_use_tool.func())

    print("\nNurse: Any use of recreational substances?")
    print("Saylor:", substance_use_tool.func())

    print("\nNurse: Let's talk about your diet. What changes have you made since your diabetes diagnosis, and could you describe a typical day's meals?")
    print("Saylor:", nutrition_info_tool.func())
    print("Saylor:", diet_recall_tool.func())

    print("\nNurse: How are you doing emotionally? Any concerns beyond the anxiety you mentioned?")
    print("Saylor:", mental_health_tool.func())

    print("\nNurse: Tell me about your personal life - your relationship, support system, and any spiritual or financial resources?")
    print("Saylor:", interpersonal_relationships_tool.func())
    print("Saylor:", spiritual_resources_tool.func())
    print("Saylor:", financial_status_tool.func())

    print("\nNurse: Regarding sexual health - when was your last STBBI screening, and do you have any concerns in this area?")
    print("Saylor:", sexual_health_tool.func())

    print("\nNurse: Could you share your family's medical history? Any patterns of illness we should be aware of?")
    print("Saylor:", family_health_history_tool.func())

    print("\nNurse: What about your own medical history - any surgeries, communicable diseases, or significant childhood illnesses?")
    print("Saylor:", surgical_history_tool.func())
    print("Saylor:", communicable_diseases_tool.func())
    print("Saylor:", childhood_illnesses_tool.func())

    print("\nNurse: When did you last see a healthcare provider, and are your vaccinations current?")
    print("Saylor:", recent_medical_exam_tool.func())
    print("Saylor:", immunization_status_tool.func())

    print("\nNurse: Any concerns about safety at home or work? Also, have you thought about advance care planning or medical directives?")
    print("Saylor:", environmental_hazards_tool.func())
    print("Saylor:", advanced_care_basic_tool.func())

    print("\nNurse: Is there anything else you'd like to discuss or any questions you have for me?")
    print("Saylor: No, I think you've been very thorough. Thank you.")

if __name__ == "__main__":
    print("\n=== Alternative Assessment Conversation with Saylor Lee ===")
    run_sample_conversation()
    print("\n=== End of Conversation ===\n") 