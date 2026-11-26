from langchain_community.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_community.tools import Tool
from dotenv import load_dotenv
import os

load_dotenv()
llm = ChatOpenAI(api_key=os.getenv('OPENAI_API_KEY'), model_name='gpt-3.5-turbo')


# Consent Tool
def check_consent(context: str = "") -> str:
    """
    Returns 
    - str: Affirmative consent response.
    """
    return f"Yes, I consent."

consent_tool = Tool(
    name="ConsentCheck",
    description="Fetch consent response from Saylor Lee.",
    func=check_consent
)

# WellnessPleasantryResponse Tool
def check_how_are_you_doing(context: str = "") -> str:
    """
    Returns:
    - str: Saylor Lee’s spoken response to general wellness inquiries.
    """
    return "I'm doing well, thank you. How are you?"

wellness_tool = Tool(
    name="WellnessPleasantryResponse",
    description="Use this tool if Saylor Lee is asked something like 'How are you doing?' or 'How have you been?' She responds politely.",
    func=check_how_are_you_doing
)

# What brings you in today Tool
def presenting_concern() -> str:
    """
    Returns:
    - str: Saylor Lee’s natural patient response about why she is seeking care today.
    """
    return f"Well, I moved from Ottawa to Montreal about six months ago. I’m new to this clinic and here for an initial check‑up."

presenting_concern_tool = Tool(
    name="PresentingConcern",
    description="Use this tool if Saylor Lee is asked 'What brings you in today?' or 'Why are you here today?' Returns her presenting concern.",
    func=presenting_concern
)

# Tracking variables for tool usage - alphabetically organized
acp_basic_used = False
acp_details_asked = False
alcohol_use_used = False
allergies_used = False
allergy_reaction_asked = False
assistive_devices_used = False
basic_activity_used = False
bracelet_asked = False
cardiovascular_used = False
childhood_illnesses_used = False
cholesterol_asked = False
communicable_diseases_used = False
coping_used = False
cough_status_asked = False
diet_recall_asked = False
elimination_used = False
endocrine_basic_used = False
endocrine_symptoms_asked = False
environmental_allergies_used = False
environmental_hazards_used = False
epipen_asked = False
family_history_used = False
financial_status_used = False
foot_sensation_asked = False
genitourinary_used = False
golf_details_asked = False
heent_status_used = False
immunization_details_asked = False
immunization_status_used = False
injuries_used = False
medication_allergies_used = False
medication_history_used = False
medical_history_used = False
mental_health_used = False
mobility_status_used = False
musculoskeletal_used = False
nail_clubbing_asked = False
neurological_used = False
nonprescription_used = False
nutrition_info_used = False
obstetrical_history_used = False
otc_medication_used = False
peripheral_vascular_used = False
presenting_concern_used = False
recent_exam_used = False
relationships_used = False
respiratory_basic_used = False
sexual_health_used = False
skin_hair_basic_used = False
sleep_patterns_used = False
smoking_status_used = False
spiritual_used = False
stbbi_asked = False
substance_use_used = False
supplements_used = False
surgical_history_used = False
vaping_details_asked = False
vision_changes_asked = False
walking_details_asked = False


# Medical History Tool
def medical_history() -> str:
    """
    Returns:
    - str: Saylor Lee's general medical history including diabetes and anxiety
    """
    global medical_history_used
    if medical_history_used:
        return llm.predict("Respond naturally about having  type 2 diabetes for 5 years and anxiety treated for 2 years.")
    medical_history_used = True
    return "I was diagnosed with Type 2 Diabetes about 5 years ago. I've also experienced anxiety on and off with major life events. I was diagnosed and started treatment for anxiety with my healthcare practitioner about 2 years ago. The medication has helped a lot."

medical_history_tool = Tool(
    name="MedicalHistory",
    description="Use this tool when Saylor Lee is asked about her medical history, health conditions, or when medical history is being discussed.",
    func=medical_history
)

def cholesterol_history(context: str = "") -> str:
    """
    Returns:
    - str: Saylor Lee's cholesterol history, only if explicitly asked
    """
    global cholesterol_asked
    if cholesterol_asked:
        return llm.predict("Respond naturally about being diagnosed with high cholesterol at the same time as diabetes.")
    cholesterol_asked = True
    return f"I was diagnosed with high cholesterol at the same time as my diabetes."

cholesterol_tool = Tool(
    name="CholesterolHistory",
    description="ONLY use this tool when Saylor Lee is EXPLICITLY asked about cholesterol. Do not volunteer this information otherwise.",
    func=cholesterol_history
)

def surgical_history() -> str:
    """
    Returns:
    - str: Saylor Lee's surgical history
    """
    global surgical_history_used
    if surgical_history_used:
        return llm.predict("Respond naturally about having appendix removed at age 20 with no complications.")
    surgical_history_used = True
    return f"I had my appendix removed when I was 20 years old. There were no complications."

surgical_history_tool = Tool(
    name="SurgicalHistory",
    description="Use this tool when Saylor Lee is asked about any previous surgeries or surgical history.",
    func=surgical_history
)

def obstetrical_history() -> str:
    """
    Returns:
    - str: Saylor Lee's obstetrical history
    """
    global obstetrical_history_used
    if obstetrical_history_used:
        return llm.predict("Respond naturally about never having been pregnant, no miscarriages, no abortions.")
    obstetrical_history_used = True
    return f"I've never been pregnant before, and I haven't had any miscarriages or abortions."

obstetrical_history_tool = Tool(
    name="ObstetricalHistory",
    description="Use this tool when Saylor Lee is asked about pregnancy history, obstetrical history, or any questions related to previous pregnancies.",
    func=obstetrical_history
)

def medication_history() -> str:
    """
    Returns:
    - str: Saylor Lee's current medications
    """
    global medication_history_used, cholesterol_asked
    if medication_history_used:
        if cholesterol_asked:
            return llm.predict("Respond naturally about taking Metformin 500mg twice daily, Lipitor 20mg nightly, and Cipralex 10mg daily.")
        return llm.predict("Respond naturally about taking Metformin 500mg twice daily and Cipralex 10mg daily.")
    
    medication_history_used = True
    if cholesterol_asked:
        return "I'm currently taking Metformin 500mg twice a day for diabetes, Lipitor 20mg every evening for high cholesterol, and Cipralex 10mg daily - I've been on that for anxiety for about 2 years now."
    return "I'm currently taking Metformin 500mg twice a day for diabetes and Cipralex 10mg daily - I've been on that for anxiety for about 2 years now."

medication_history_tool = Tool(
    name="MedicationHistory",
    description="Use this tool when Saylor Lee is asked about current medications or medication history.",
    func=medication_history
)



def otc_medication_history() -> str:
    """
    Returns:
    - str: Saylor Lee's over-the-counter medication usage
    """
    global otc_medication_used
    if otc_medication_used:
        return llm.predict("Respond naturally about taking Tylenol 650mg (2 tablets) for occasional headaches about once a month.")
    otc_medication_used = True
    return "I take Tylenol occasionally for headaches - about once a month. When I do take it, I take 650mg, which is two tablets."

otc_medication_tool = Tool(
    name="OTCMedicationHistory",
    description="Use this tool when Saylor Lee is asked about over-the-counter medications, non-prescription drugs, or pain relievers.",
    func=otc_medication_history
)

def supplements_history() -> str:
    """
    Returns:
    - str: Saylor Lee's herbal supplements and natural products usage
    """
    global supplements_used
    if supplements_used:
        return llm.predict("Respond naturally about not taking any herbal supplements or natural products.")
    supplements_used = True
    return "I don't take any herbal supplements or natural products."

supplements_tool = Tool(
    name="SupplementsHistory",
    description="Use this tool when Saylor Lee is asked about herbal supplements, vitamins, natural products, or alternative medicines.",
    func=supplements_history
)



def nonprescription_medications() -> str:
    """
    Returns:
    - str: Combined information about Saylor Lee's OTC medications and supplements
    """
    global nonprescription_used, otc_medication_used, supplements_used
    otc_medication_used = True
    supplements_used = True
    
    if nonprescription_used:
        return llm.predict("Respond naturally about taking Tylenol 650mg (2 tablets) for occasional headaches monthly, and not taking any supplements or herbal products.")
    nonprescription_used = True
    return "I take Tylenol occasionally for headaches - about once a month, 650mg which is two tablets. I don't take any herbal supplements or natural products."

nonprescription_tool = Tool(
    name="NonprescriptionMedications",
    description="Use this tool when Saylor Lee is asked about both over-the-counter medications AND supplements/herbals, or when asked generally about non-prescription products.",
    func=nonprescription_medications
)

def communicable_diseases() -> str:
    """
    Returns:
    - str: Saylor Lee's communicable disease history
    """
    global communicable_diseases_used
    if communicable_diseases_used:
        return llm.predict("Respond naturally about having no history of communicable diseases.")
    communicable_diseases_used = True
    return "I don't have any history of communicable diseases."

communicable_diseases_tool = Tool(
    name="CommunicableDiseases",
    description="Use this tool when Saylor Lee is asked about communicable diseases or infectious disease history.",
    func=communicable_diseases
)

def stbbi_history(context: str = "") -> str:
    """
    Returns:
    - str: Saylor Lee's STBBI testing history, only if explicitly asked
    """
    global stbbi_asked
    if not any(term in context.lower() for term in ["sti", "std", "stbbi", "sexually transmitted"]):
        return "I prefer to discuss specific health matters when asked about them directly."
    
    if stbbi_asked:
        return llm.predict("Respond naturally about having negative STBBI test results from two years ago when tested with partner.")
    stbbi_asked = True
    return "My partner and I were tested two years ago, and all results were negative."

stbbi_tool = Tool(
    name="STBBIHistory",
    description="ONLY use this tool when Saylor Lee is EXPLICITLY asked about sexually transmitted infections, STIs, STDs, or STBBIs.",
    func=stbbi_history
)

def food_allergies() -> str:
    """
    Returns:
    - str: Saylor Lee's food allergy information
    """
    global allergies_used
    if allergies_used:
        return llm.predict("Respond naturally about being allergic to peanuts.")
    allergies_used = True
    return "I'm allergic to peanuts."

food_allergies_tool = Tool(
    name="FoodAllergies",
    description="Use this tool when Saylor Lee is asked about food allergies or dietary restrictions due to allergies.",
    func=food_allergies
)

def allergy_reaction() -> str:
    """
    Returns:
    - str: Details about Saylor Lee's last allergic reaction
    """
    global allergy_reaction_asked
    if allergy_reaction_asked:
        return llm.predict("Respond naturally about last reaction being a few years ago with facial swelling and difficulty breathing.")
    allergy_reaction_asked = True
    return "My last reaction was a few years ago - my face got swollen and I had difficulty breathing."

allergy_reaction_tool = Tool(
    name="AllergyReaction",
    description="ONLY use this tool when Saylor Lee is EXPLICITLY asked about her allergic reaction symptoms or what happened during her reaction.",
    func=allergy_reaction
)

def epipen_info() -> str:
    """
    Returns:
    - str: Information about Saylor Lee's epipen status and knowledge
    """
    global epipen_asked
    if epipen_asked:
        return llm.predict("Respond naturally about not carrying an epipen but knowing how to use one - orange to thigh, blue to sky.")
    epipen_asked = True
    return "I don't carry an epi-pen, but I know how to use one - 'Orange to the thigh and blue to the sky.'"

epipen_tool = Tool(
    name="EpipenInfo",
    description="ONLY use this tool when Saylor Lee is EXPLICITLY asked about carrying or using an epipen/auto-injector.",
    func=epipen_info
)

def medic_alert() -> str:
    """
    Returns:
    - str: Information about Saylor Lee's medic alert bracelet status
    """
    global bracelet_asked
    if bracelet_asked:
        return llm.predict("Respond naturally about not wearing a medic alert bracelet.")
    bracelet_asked = True
    return "I don't wear a medic alert bracelet."

medic_alert_tool = Tool(
    name="MedicAlert",
    description="ONLY use this tool when Saylor Lee is EXPLICITLY asked about wearing a medic alert bracelet or medical ID.",
    func=medic_alert
)

def reaction_and_epipen() -> str:
    """
    Returns:
    - str: Combined information about reaction and epipen
    """
    global allergy_reaction_asked, epipen_asked
    allergy_reaction_asked = True
    epipen_asked = True
    return "My last reaction was a few years ago - my face got swollen and I had difficulty breathing. I don't carry an epi-pen, but I know how to use one - 'Orange to the thigh and blue to the sky.'"

reaction_epipen_tool = Tool(
    name="ReactionAndEpipen",
    description="ONLY use this tool when Saylor Lee is EXPLICITLY asked about both her allergic reaction AND epipen/auto-injector use.",
    func=reaction_and_epipen
)

def reaction_and_bracelet() -> str:
    """
    Returns:
    - str: Combined information about reaction and medic alert
    """
    global allergy_reaction_asked, bracelet_asked
    allergy_reaction_asked = True
    bracelet_asked = True
    return "My last reaction was a few years ago - my face got swollen and I had difficulty breathing. I don't wear a medic alert bracelet."

reaction_bracelet_tool = Tool(
    name="ReactionAndBracelet",
    description="ONLY use this tool when Saylor Lee is EXPLICITLY asked about both her allergic reaction AND medic alert bracelet.",
    func=reaction_and_bracelet
)

def epipen_and_bracelet() -> str:
    """
    Returns:
    - str: Combined information about epipen and medic alert
    """
    global epipen_asked, bracelet_asked
    epipen_asked = True
    bracelet_asked = True
    return "I don't carry an epi-pen, but I know how to use one - 'Orange to the thigh and blue to the sky.' I don't wear a medic alert bracelet."

epipen_bracelet_tool = Tool(
    name="EpipenAndBracelet",
    description="ONLY use this tool when Saylor Lee is EXPLICITLY asked about both epipen/auto-injector AND medic alert bracelet.",
    func=epipen_and_bracelet
)

def all_allergy_details() -> str:
    """
    Returns:
    - str: All detailed information about allergy management
    """
    global allergy_reaction_asked, epipen_asked, bracelet_asked
    allergy_reaction_asked = True
    epipen_asked = True
    bracelet_asked = True
    return "My last reaction was a few years ago - my face got swollen and I had difficulty breathing. I don't carry an epi-pen, but I know how to use one - 'Orange to the thigh and blue to the sky.' I don't wear a medic alert bracelet."

all_allergy_details_tool = Tool(
    name="AllAllergyDetails",
    description="ONLY use this tool when Saylor Lee is EXPLICITLY asked about her allergic reaction, epipen/auto-injector, AND medic alert bracelet all together.",
    func=all_allergy_details
)

def medication_allergies() -> str:
    """
    Returns:
    - str: Saylor Lee's medication allergy information
    """
    global medication_allergies_used
    if medication_allergies_used:
        return llm.predict("Respond naturally about having no medication allergies.")
    medication_allergies_used = True
    return "I don't have any allergies to medications."

medication_allergies_tool = Tool(
    name="MedicationAllergies",
    description="Use this tool when Saylor Lee is asked about medication allergies or drug allergies.",
    func=medication_allergies
)

def environmental_allergies() -> str:
    """
    Returns:
    - str: Saylor Lee's environmental allergy information
    """
    global environmental_allergies_used
    if environmental_allergies_used:
        return llm.predict("Respond naturally about having no environmental allergies.")
    environmental_allergies_used = True
    return "I don't have any environmental allergies."

environmental_allergies_tool = Tool(
    name="EnvironmentalAllergies",
    description="Use this tool when Saylor Lee is asked about environmental allergies, seasonal allergies, or allergies to things like pollen, dust, etc.",
    func=environmental_allergies
)

def injuries_history() -> str:
    """
    Returns:
    - str: Saylor Lee's injury and accident history
    """
    global injuries_used
    if injuries_used:
        return llm.predict("Respond naturally about breaking tibia while skiing as a child, without remembering much detail.")
    injuries_used = True
    return "I broke my tibia once when I was a kid while skiing. It was years ago, and I don't remember much more about it."

injuries_history_tool = Tool(
    name="InjuriesHistory",
    description="Use this tool when Saylor Lee is asked about past injuries, accidents, or broken bones.",
    func=injuries_history
)

def childhood_illnesses() -> str:
    """
    Returns:
    - str: Saylor Lee's childhood illness history
    """
    global childhood_illnesses_used
    if childhood_illnesses_used:
        return llm.predict("Respond naturally about having no significant childhood illnesses.")
    childhood_illnesses_used = True
    return "I didn't have any significant childhood illnesses."

childhood_illnesses_tool = Tool(
    name="ChildhoodIllnesses",
    description="Use this tool when Saylor Lee is asked about illnesses or health conditions from childhood.",
    func=childhood_illnesses
)

def immunization_status() -> str:
    """
    Returns:
    - str: Saylor Lee's general immunization status
    """
    global immunization_status_used
    if immunization_status_used:
        return llm.predict("Respond naturally about keeping vaccines up to date and planning to get flu shot this year.")
    immunization_status_used = True
    return "I keep all my vaccines up to date, and I'm planning on getting the flu shot this year."

immunization_status_tool = Tool(
    name="ImmunizationStatus",
    description="Use this tool when Saylor Lee is asked about general immunization status or vaccine maintenance.",
    func=immunization_status
)

def immunization_details() -> str:
    """
    Returns:
    - str: Detailed information about Saylor Lee's immunizations when specifically asked
    """
    global immunization_details_asked
    if immunization_details_asked:
        return llm.predict("Respond naturally about last flu shot being last fall and not knowing how to get vaccines in Montreal.")
    immunization_details_asked = True
    return "My last immunization was the flu vaccine last fall. I'm not sure how to get my vaccines here in Montreal since moving."

immunization_details_tool = Tool(
    name="ImmunizationDetails",
    description="ONLY use this tool when Saylor Lee is EXPLICITLY asked about specific immunization dates or how to get vaccines in Montreal.",
    func=immunization_details
)

def recent_medical_exam() -> str:
    """
    Returns:
    - str: Information about Saylor Lee's most recent medical examination and current healthcare situation
    """
    global recent_exam_used
    if recent_exam_used:
        return llm.predict("Respond naturally about last medical exam being 6 months ago for diabetes follow-up, and not having seen anyone since moving.")
    recent_exam_used = True
    return "My last medical examination was 6 months ago - it was a routine follow-up for my diabetes. Since moving, I haven't been able to see any healthcare providers here yet."

recent_medical_exam_tool = Tool(
    name="RecentMedicalExam",
    description="Use this tool when Saylor Lee is asked about her most recent medical examination, last doctor's visit, or current access to healthcare.",
    func=recent_medical_exam
)

def family_health_history() -> str:
    """
    Returns:
    - str: Comprehensive information about Saylor Lee's family health history and relationships
    """
    global family_history_used
    if family_history_used:
        return llm.predict("Respond naturally about mother living in Florida with controlled type 2 diabetes, father passing from lung cancer 5 years ago, healthy sister around 62 who you're close with along with her family, and not knowing grandparents' health history.")
    family_history_used = True
    return "My mother lives in Florida and has type 2 diabetes, which is well-controlled. My father passed away 5 years ago from lung cancer. I have one sister who's close to my age, around 62, and she's healthy. We're very close, and I'm also close with my nieces and nephews. They all get along well with my partner. I don't know my grandparents' health history."

family_health_history_tool = Tool(
    name="FamilyHealthHistory",
    description="Use this tool when Saylor Lee is asked about family medical history, family health conditions, or family relationships.",
    func=family_health_history
)

def health_perception() -> str:
    """
    Returns:
    - str: Saylor Lee's perception of her health and lifestyle, including stress management
    """
    global health_perception_used
    if health_perception_used:
        return llm.predict("Respond naturally about feeling healthy overall, having good diet and exercise habits, stress being managed with medication but being open to additional management tips.")
    health_perception_used = True
    return "I consider myself a healthy person - we eat well and I think I exercise enough. My stress levels are mostly under control since starting medications, though I would appreciate some tips to help manage it a bit better."

health_perception_tool = Tool(
    name="HealthPerception",
    description="Use this tool when Saylor Lee is asked about how she views her health, lifestyle habits, stress levels, or when discussing health management strategies.",
    func=health_perception
)

def basic_activity() -> str:
    """
    Returns:
    - str: Basic information about Saylor Lee's physical activities
    """
    global basic_activity_used
    if basic_activity_used:
        return llm.predict("Respond naturally about doing walking and golf as main activities.")
    basic_activity_used = True
    return "My main physical activities are walking and golf."

basic_activity_tool = Tool(
    name="BasicActivity",
    description="Use this tool when Saylor Lee is asked generally about what physical activities or exercise she does.",
    func=basic_activity
)

def walking_details() -> str:
    """
    Returns:
    - str: Detailed information about Saylor Lee's walking habits
    """
    global walking_details_asked
    if walking_details_asked:
        return llm.predict("Respond naturally about previously walking 30 minutes every evening but having difficulty maintaining this since moving to town, wanting to resume daily walks.")
    walking_details_asked = True
    return "I used to walk for about 30 minutes every evening, but I haven't been able to walk as much since moving into town. I would very much like to get back to my daily walks."

walking_details_tool = Tool(
    name="WalkingDetails",
    description="ONLY use this tool when Saylor Lee is EXPLICITLY asked about her walking routine or habits.",
    func=walking_details
)

def golf_details() -> str:
    """
    Returns:
    - str: Detailed information about Saylor Lee's golfing habits
    """
    global golf_details_asked
    if golf_details_asked:
        return llm.predict("Respond naturally about golfing every Saturday during summer months, mainly for networking purposes.")
    golf_details_asked = True
    return "I golf every Saturday over the summer months, mostly for networking."

golf_details_tool = Tool(
    name="GolfDetails",
    description="ONLY use this tool when Saylor Lee is EXPLICITLY asked about her golfing habits or frequency.",
    func=golf_details
)

def walking_and_golf_details() -> str:
    """
    Returns:
    - str: Combined information about walking and golf details
    """
    global walking_details_asked, golf_details_asked
    walking_details_asked = True
    golf_details_asked = True
    return "I used to walk for about 30 minutes every evening, but haven't been able to walk as much since moving into town. I would very much like to get back to my daily walks. As for golf, I play every Saturday over the summer months, mostly for networking."

walking_golf_tool = Tool(
    name="WalkingAndGolfDetails",
    description="ONLY use this tool when Saylor Lee is EXPLICITLY asked about both her walking AND golfing habits together.",
    func=walking_and_golf_details
)

def basic_and_walking_details() -> str:
    """
    Returns:
    - str: Combined basic activity and walking details
    """
    global basic_activity_used, walking_details_asked
    basic_activity_used = True
    walking_details_asked = True
    return "My main physical activities are walking and golf. About my walking - I used to do 30 minutes every evening, but haven't been able to walk as much since moving into town. I would very much like to get back to my daily walks."

basic_walking_tool = Tool(
    name="BasicAndWalkingDetails",
    description="Use this tool when Saylor Lee is asked about her activities with specific interest in walking details.",
    func=basic_and_walking_details
)

def basic_and_golf_details() -> str:
    """
    Returns:
    - str: Combined basic activity and golf details
    """
    global basic_activity_used, golf_details_asked
    basic_activity_used = True
    golf_details_asked = True
    return "My main physical activities are walking and golf. About golfing - I play every Saturday over the summer months, mostly for networking."

basic_golf_tool = Tool(
    name="BasicAndGolfDetails",
    description="Use this tool when Saylor Lee is asked about her activities with specific interest in golfing details.",
    func=basic_and_golf_details
)

def all_activity_details() -> str:
    """
    Returns:
    - str: All activity information combined
    """
    global basic_activity_used, walking_details_asked, golf_details_asked
    basic_activity_used = True
    walking_details_asked = True
    golf_details_asked = True
    return "My main physical activities are walking and golf. I used to walk for about 30 minutes every evening, but haven't been able to walk as much since moving into town. I would very much like to get back to my daily walks. As for golf, I play every Saturday over the summer months, mostly for networking."

all_activity_tool = Tool(
    name="AllActivityDetails",
    description="Use this tool when Saylor Lee is asked for comprehensive information about ALL her physical activities and their details.",
    func=all_activity_details
)

def mobility_status() -> str:
    """
    Returns:
    - str: Information about Saylor Lee's mobility status
    """
    global mobility_status_used
    if mobility_status_used:
        return llm.predict("Respond naturally about having no mobility issues.")
    mobility_status_used = True
    return "I don't have any mobility issues."

mobility_status_tool = Tool(
    name="MobilityStatus",
    description="Use this tool when Saylor Lee is asked about her mobility, movement capabilities, or any physical limitations.",
    func=mobility_status
)

def assistive_devices() -> str:
    """
    Returns:
    - str: Information about Saylor Lee's need for assistive devices
    """
    global assistive_devices_used
    if assistive_devices_used:
        return llm.predict("Respond naturally about not needing any assistive devices.")
    assistive_devices_used = True
    return "I don't need any assistive devices."

assistive_devices_tool = Tool(
    name="AssistiveDevices",
    description="Use this tool when Saylor Lee is asked about using or needing any assistive devices, mobility aids, or support equipment.",
    func=assistive_devices
)

def sleep_patterns() -> str:
    """
    Returns:
    - str: Information about Saylor Lee's sleep patterns and quality
    """
    global sleep_patterns_used
    if sleep_patterns_used:
        return llm.predict("Respond naturally about getting 6 hours of sleep per night, not waking up during the night but having trouble falling asleep due to making mental to-do lists.")
    sleep_patterns_used = True
    return "I usually get about 6 hours of sleep per night. I don't wake up during the night, but I do have a hard time falling asleep because I tend to make mental to-do lists."

sleep_patterns_tool = Tool(
    name="SleepPatterns",
    description="Use this tool when Saylor Lee is asked about her sleep habits, sleep quality, sleep duration, or any sleep-related concerns.",
    func=sleep_patterns
)

def nutrition_info() -> str:
    """
    Returns:
    - str: Information about Saylor Lee's dietary changes and current diet
    """
    global nutrition_info_used
    if nutrition_info_used:
        return llm.predict("Respond naturally about making major diet changes after diabetes diagnosis, working with diabetes team, and following partner's vegetarian diet.")
    nutrition_info_used = True
    return "I made drastic changes to my diet when I was diagnosed with diabetes 5 years ago. I worked with a diabetes team who helped me revamp my lifestyle - I really didn't want to have to start insulin. My partner started following a vegetarian diet, so I'm doing that as well now."

nutrition_info_tool = Tool(
    name="NutritionInfo",
    description="Use this tool when Saylor Lee is asked about her diet, dietary changes, or general nutrition habits.",
    func=nutrition_info
)

def diet_recall() -> str:
    """
    Returns:
    - str: 24-hour diet recall information
    """
    global diet_recall_asked
    if diet_recall_asked:
        return llm.predict("Respond naturally with a 24-hour healthy vegetarian meal recall: oatmeal with berries for breakfast, lentil soup and salad for lunch, veggie stir-fry for dinner, nuts and fruit for snacks.")
    diet_recall_asked = True
    return "For breakfast, I had oatmeal with fresh berries. Lunch was lentil soup with a mixed green salad. Dinner was a vegetable stir-fry with tofu. I snack on nuts and fruit throughout the day."

diet_recall_tool = Tool(
    name="DietRecall",
    description="ONLY use this tool when Saylor Lee is EXPLICITLY asked about what she ate in the last 24 hours or for a food diary.",
    func=diet_recall
)

def complete_nutrition_info() -> str:
    """
    Returns:
    - str: Combined nutrition information and diet recall
    """
    global nutrition_info_used, diet_recall_asked
    nutrition_info_used = True
    diet_recall_asked = True
    return "I made drastic changes to my diet when I was diagnosed with diabetes 5 years ago. I worked with a diabetes team who helped me revamp my lifestyle - I really didn't want to have to start insulin. My partner started following a vegetarian diet, so I'm doing that as well now. As an example of what I eat: for breakfast, I had oatmeal with fresh berries. Lunch was lentil soup with a mixed green salad. Dinner was a vegetable stir-fry with tofu. I snack on nuts and fruit throughout the day."

complete_nutrition_tool = Tool(
    name="CompleteNutritionInfo",
    description="Use this tool when Saylor Lee is asked about BOTH her general nutrition habits AND specific food intake.",
    func=complete_nutrition_info
)

def elimination_patterns() -> str:
    """
    Returns:
    - str: Information about Saylor Lee's bowel and urinary elimination patterns
    """
    global elimination_used
    if elimination_used:
        return llm.predict("Respond naturally about having regular daily bowel movements, formed stool, and no urinary issues.")
    elimination_used = True
    return "I have regular bowel movements once a day, formed, with no issues. I don't have any urinary problems."

elimination_patterns_tool = Tool(
    name="EliminationPatterns",
    description="Use this tool when Saylor Lee is asked about bowel movements, urinary function, or elimination patterns.",
    func=elimination_patterns
)

def interpersonal_relationships() -> str:
    """
    Returns:
    - str: Information about Saylor Lee's relationships and social support
    """
    global relationships_used
    if relationships_used:
        return llm.predict("Respond naturally about 32-year committed relationship, supportive family, good friends, community, and new colleagues, mentioning no children.")
    relationships_used = True
    return "I've been in a committed relationship for about 32 years - it's a good relationship. We have a supportive family, and they're fun to be around - we all get along well. We have many friends and a great community. I think I have great new colleagues at my new firm too. We don't have any children."

interpersonal_relationships_tool = Tool(
    name="InterpersonalRelationships",
    description="Use this tool when Saylor Lee is asked about her relationships, family, social support, or community connections.",
    func=interpersonal_relationships
)

def spiritual_resources() -> str:
    """
    Returns:
    - str: Information about Saylor Lee's spiritual resources
    """
    global spiritual_used
    if spiritual_used:
        return llm.predict("Respond naturally about not having any spiritual resources.")
    spiritual_used = True
    return "I don't have any spiritual resources."

spiritual_resources_tool = Tool(
    name="SpiritualResources",
    description="Use this tool when Saylor Lee is asked about spirituality, religious practices, or spiritual support.",
    func=spiritual_resources
)

def coping_strategies() -> str:
    """
    Returns:
    - str: Information about Saylor Lee's coping and stress management
    """
    global coping_used
    if coping_used:
        return llm.predict("Respond naturally about needing to use coping strategies more, previously enjoying walks but not prioritizing them lately, and having heard about but not tried journaling.")
    coping_used = True
    return "I need to use coping strategies more often. I used to like going for walks but haven't prioritized that lately. Someone mentioned journaling to me before, but I've never tried it."

coping_strategies_tool = Tool(
    name="CopingStrategies",
    description="Use this tool when Saylor Lee is asked about how she manages stress, coping mechanisms, or stress management techniques.",
    func=coping_strategies
)

def smoking_status() -> str:
    """
    Returns:
    - str: Basic information about Saylor Lee's smoking/vaping status
    """
    global smoking_status_used
    if smoking_status_used:
        return llm.predict("Respond naturally about currently vaping, with no other smoking history.")
    smoking_status_used = True
    return "I currently vape. I don't have any other history of smoking."

smoking_status_tool = Tool(
    name="SmokingStatus",
    description="Use this tool when Saylor Lee is asked generally about smoking, vaping, or tobacco use.",
    func=smoking_status
)

def vaping_details() -> str:
    """
    Returns:
    - str: Detailed information about Saylor Lee's vaping habits when explicitly asked
    """
    global vaping_details_asked
    if vaping_details_asked:
        return llm.predict("Respond naturally about using one nicotine vape cartridge per day for 5 years, mentioning it helped with stress.")
    vaping_details_asked = True
    return "I go through about one cartridge per day, and I've been vaping for 5 years now. The cartridges contain nicotine. It used to help me with stress."

vaping_details_tool = Tool(
    name="VapingDetails",
    description="ONLY use this tool when Saylor Lee is EXPLICITLY asked about vaping frequency, duration, or reasons for vaping.",
    func=vaping_details
)

def alcohol_use() -> str:
    """
    Returns:
    - str: Information about Saylor Lee's alcohol consumption
    """
    global alcohol_use_used
    if alcohol_use_used:
        return llm.predict("Respond naturally about having one beer or wine daily after work, sometimes two on weekends.")
    alcohol_use_used = True
    return "I usually have one beer or glass of wine when I get home from work, sometimes two on weekends."

alcohol_use_tool = Tool(
    name="AlcoholUse",
    description="Use this tool when Saylor Lee is asked about alcohol consumption or drinking habits.",
    func=alcohol_use
)

def substance_use() -> str:
    """
    Returns:
    - str: Information about Saylor Lee's substance use history
    """
    global substance_use_used
    if substance_use_used:
        return llm.predict("Respond naturally about never using substances.")
    substance_use_used = True
    return "I've never used any substances."

substance_use_tool = Tool(
    name="SubstanceUse",
    description="Use this tool when Saylor Lee is asked about substance use, drug use, or recreational drug history.",
    func=substance_use
)

def environmental_hazards() -> str:
    """
    Returns:
    - str: Information about Saylor Lee's environmental hazard exposure
    """
    global environmental_hazards_used
    if environmental_hazards_used:
        return llm.predict("Respond naturally about having no environmental hazards.")
    environmental_hazards_used = True
    return "I don't have any environmental hazards."

environmental_hazards_tool = Tool(
    name="EnvironmentalHazards",
    description="Use this tool when Saylor Lee is asked about environmental hazards or exposure risks.",
    func=environmental_hazards
)

def sexual_health() -> str:
    """
    Returns:
    - str: Information about Saylor Lee's sexual health
    """
    global sexual_health_used
    if sexual_health_used:
        return llm.predict("Respond naturally about being in a monogamous relationship, negative STBBI test 2 years ago, and not using contraception or barriers.")
    sexual_health_used = True
    return "I'm in a monogamous relationship. My last STBBI test was 2 years ago and the results were negative. I don't use any contraception or protective barriers."

sexual_health_tool = Tool(
    name="SexualHealth",
    description="Use this tool when Saylor Lee is asked about sexual health, relationships, contraception, or STBBI testing.",
    func=sexual_health
)

def financial_status() -> str:
    """
    Returns:
    - str: Information about Saylor Lee's financial situation
    """
    global financial_status_used
    if financial_status_used:
        return llm.predict("Respond naturally about having no financial issues.")
    financial_status_used = True
    return "I don't have any financial issues."

financial_status_tool = Tool(
    name="FinancialStatus",
    description="Use this tool when Saylor Lee is asked about financial situation or economic status.",
    func=financial_status
)

def advanced_care_basic() -> str:
    """
    Returns:
    - str: Basic information about Saylor Lee's advanced care planning status
    """
    global acp_basic_used
    if acp_basic_used:
        return llm.predict("Respond naturally about never having discussed advanced care planning and wanting more information.")
    acp_basic_used = True
    return "No one has ever talked to me about advanced care planning. I would like more information about it."

advanced_care_basic_tool = Tool(
    name="AdvancedCarePlanningBasic",
    description="Use this tool when Saylor Lee is asked generally about advanced care planning or end-of-life planning.",
    func=advanced_care_basic
)

def advanced_care_details() -> str:
    """
    Returns:
    - str: Detailed information about Saylor Lee's advanced care planning when explicitly asked
    """
    global acp_details_asked
    if acp_details_asked:
        return llm.predict("Respond naturally about assuming partner is medical power of attorney, having up-to-date will, no code status, and no other concerns.")
    acp_details_asked = True
    return "I've assumed my partner would be my medical power of attorney. I do have an up-to-date will. I don't have any code status established. Other than that, I don't have any concerns."

advanced_care_details_tool = Tool(
    name="AdvancedCarePlanningDetails",
    description="ONLY use this tool when Saylor Lee is EXPLICITLY asked about specific aspects of advanced care planning like power of attorney, will, or code status.",
    func=advanced_care_details
)

def skin_hair_basic() -> str:
    """
    Returns:
    - str: Basic information about Saylor Lee's skin and hair status
    """
    global skin_hair_basic_used
    if skin_hair_basic_used:
        return llm.predict("Respond naturally about having no skin issues but noticing some hair thinning/loss in shower.")
    skin_hair_basic_used = True
    return "I don't have any skin issues, but I have noticed a little bit of hair thinning and hair loss when I shower."

skin_hair_basic_tool = Tool(
    name="SkinHairBasic",
    description="Use this tool when Saylor Lee is asked about general skin condition or hair health.",
    func=skin_hair_basic
)

def nail_clubbing_status() -> str:
    """
    Returns:
    - str: Information about nail clubbing when explicitly asked
    """
    global nail_clubbing_asked
    if nail_clubbing_asked:
        return llm.predict("Respond naturally about having no nail clubbing.")
    nail_clubbing_asked = True
    return "No, I don't have any nail clubbing."

nail_clubbing_tool = Tool(
    name="NailClubbingStatus",
    description="ONLY use this tool when Saylor Lee is EXPLICITLY asked about nail clubbing.",
    func=nail_clubbing_status
)

def foot_sensation() -> str:
    """
    Returns:
    - str: Information about foot sensation when explicitly asked
    """
    global foot_sensation_asked
    if foot_sensation_asked:
        return llm.predict("Respond naturally about having no numbness, tingling, or loss of sensation in feet.")
    foot_sensation_asked = True
    return "No, I don't have any numbness, tingling, or loss of sensation in my feet."

foot_sensation_tool = Tool(
    name="FootSensation",
    description="ONLY use this tool when Saylor Lee is EXPLICITLY asked about foot sensation, numbness, or tingling.",
    func=foot_sensation
)

def vision_status() -> str:
    """
    Returns:
    - str: Information about vision changes when explicitly asked
    """
    global vision_changes_asked
    if vision_changes_asked:
        return llm.predict("Respond naturally about having no changes in vision.")
    vision_changes_asked = True
    return "No, I haven't noticed any changes in my vision."

vision_status_tool = Tool(
    name="VisionStatus",
    description="ONLY use this tool when Saylor Lee is EXPLICITLY asked about vision changes or visual symptoms.",
    func=vision_status
)

def heent_status() -> str:
    """
    Returns:
    - str: Information about Saylor Lee's HEENT status, including headaches
    """
    global heent_status_used, otc_medication_used
    otc_medication_used = True  # Mark OTC info as shared since headaches are mentioned
    if heent_status_used:
        return llm.predict("Respond naturally about having monthly headaches treated with Tylenol as previously mentioned, with no other HEENT issues.")
    heent_status_used = True
    return "I get headaches about once per month and take Tylenol for them, as I mentioned before. I don't have any other head, eye, ear, nose, or throat issues."

heent_status_tool = Tool(
    name="HEENTStatus",
    description="Use this tool when Saylor Lee is asked about head, eyes, ears, nose, throat symptoms, or headaches.",
    func=heent_status
)

def respiratory_basic() -> str:
    """
    Returns:
    - str: Basic information about Saylor Lee's respiratory status
    """
    global respiratory_basic_used
    if respiratory_basic_used:
        return llm.predict("Respond naturally about having no respiratory issues.")
    respiratory_basic_used = True
    return "I don't have any respiratory issues."

respiratory_basic_tool = Tool(
    name="RespiratoryBasic",
    description="Use this tool when Saylor Lee is asked about general respiratory health or breathing.",
    func=respiratory_basic
)

def cough_status() -> str:
    """
    Returns:
    - str: Information about cough when explicitly asked
    """
    global cough_status_asked
    if cough_status_asked:
        return llm.predict("Respond naturally about having no cough.")
    cough_status_asked = True
    return "No, I don't have any cough."

cough_status_tool = Tool(
    name="CoughStatus",
    description="ONLY use this tool when Saylor Lee is EXPLICITLY asked about presence of cough.",
    func=cough_status
)

def cardiovascular_status() -> str:
    """
    Returns:
    - str: Information about Saylor Lee's cardiovascular system
    """
    global cardiovascular_used
    if cardiovascular_used:
        return llm.predict("Respond naturally about having no cardiovascular issues.")
    cardiovascular_used = True
    return "I don't have any cardiovascular issues."

cardiovascular_tool = Tool(
    name="CardiovascularStatus",
    description="Use this tool when Saylor Lee is asked about heart health or cardiovascular system.",
    func=cardiovascular_status
)

def peripheral_vascular_status() -> str:
    """
    Returns:
    - str: Information about Saylor Lee's peripheral vascular system
    """
    global peripheral_vascular_used
    if peripheral_vascular_used:
        return llm.predict("Respond naturally about having no peripheral vascular issues.")
    peripheral_vascular_used = True
    return "I don't have any peripheral vascular issues."

peripheral_vascular_tool = Tool(
    name="PeripheralVascularStatus",
    description="Use this tool when Saylor Lee is asked about circulation or peripheral vascular system.",
    func=peripheral_vascular_status
)

def genitourinary_status() -> str:
    """
    Returns:
    - str: Information about Saylor Lee's genitourinary system
    """
    global genitourinary_used
    if genitourinary_used:
        return llm.predict("Respond naturally about having no genitourinary issues.")
    genitourinary_used = True
    return "I don't have any genitourinary issues."

genitourinary_tool = Tool(
    name="GenitourinaryStatus",
    description="Use this tool when Saylor Lee is asked about genitourinary system or urinary function.",
    func=genitourinary_status
)

def musculoskeletal_status() -> str:
    """
    Returns:
    - str: Information about Saylor Lee's musculoskeletal system
    """
    global musculoskeletal_used
    if musculoskeletal_used:
        return llm.predict("Respond naturally about having no musculoskeletal issues.")
    musculoskeletal_used = True
    return "I don't have any musculoskeletal issues."

musculoskeletal_tool = Tool(
    name="MusculoskeletalStatus",
    description="Use this tool when Saylor Lee is asked about muscles, bones, joints, or musculoskeletal system.",
    func=musculoskeletal_status
)

def neurological_status() -> str:
    """
    Returns:
    - str: Information about Saylor Lee's neurological system
    """
    global neurological_used
    if neurological_used:
        return llm.predict("Respond naturally about having no neurological issues.")
    neurological_used = True
    return "I don't have any neurological issues."

neurological_tool = Tool(
    name="NeurologicalStatus",
    description="Use this tool when Saylor Lee is asked about neurological system or nervous system function.",
    func=neurological_status
)

def mental_health_status() -> str:
    """
    Returns:
    - str: Information about Saylor Lee's current mental health status
    """
    global mental_health_used
    if mental_health_used:
        return llm.predict("Respond naturally about having no mental health concerns beyond the previously mentioned anxiety that's treated with medication.")
    mental_health_used = True
    return "I don't have any other mental health concerns beyond the anxiety I mentioned before, which is being treated with medication."

mental_health_tool = Tool(
    name="MentalHealthStatus",
    description="Use this tool when Saylor Lee is asked about current mental health status or psychological wellbeing.",
    func=mental_health_status
)

def endocrine_basic() -> str:
    """
    Returns:
    - str: Basic information about Saylor Lee's endocrine system
    """
    global endocrine_basic_used
    if endocrine_basic_used:
        return llm.predict("Respond naturally about having well-controlled diabetes.")
    endocrine_basic_used = True
    return "I have diabetes, but it's well controlled."

endocrine_basic_tool = Tool(
    name="EndocrineBasic",
    description="Use this tool when Saylor Lee is asked about general endocrine system or diabetes status.",
    func=endocrine_basic
)

def endocrine_symptoms() -> str:
    """
    Returns:
    - str: Information about specific endocrine symptoms when explicitly asked
    """
    global endocrine_symptoms_asked
    if endocrine_symptoms_asked:
        return llm.predict("Respond naturally about having no unintentional weight loss, fever, chills, or night sweats.")
    endocrine_symptoms_asked = True
    return "No, I haven't had any unintentional weight loss, fever, chills, or night sweats."

endocrine_symptoms_tool = Tool(
    name="EndocrineSymptoms",
    description="ONLY use this tool when Saylor Lee is EXPLICITLY asked about specific endocrine symptoms like weight loss, fever, chills, or night sweats.",
    func=endocrine_symptoms
)
