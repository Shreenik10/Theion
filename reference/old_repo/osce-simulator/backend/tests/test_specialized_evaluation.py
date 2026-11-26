import pytest
from app.services.specialized_evaluation_service import SpecializedEvaluationService

@pytest.mark.asyncio
async def test_empty_transcript():
    service = SpecializedEvaluationService()  # Will use OpenAI
    
    # Test with None
    result = await service.evaluate_all_categories(None)
    assert result["total_score"] == 0
    assert result["max_possible"] == 65
    assert not result["scores"]  # Empty dict
    assert not result["feedback"]  # Empty dict
    
    # Test with empty string
    result = await service.evaluate_all_categories("")
    assert result["total_score"] == 0
    assert result["max_possible"] == 65
    assert not result["scores"]
    assert not result["feedback"]
    
    # Test with whitespace
    result = await service.evaluate_all_categories("   ")
    assert result["total_score"] == 0
    assert result["max_possible"] == 65
    assert not result["scores"]
    assert not result["feedback"]

@pytest.mark.asyncio
async def test_full_interview():
    service = SpecializedEvaluationService()  # Will use OpenAI
    
    transcript = """Doctor: Hi, my name is Alex Kim, I'm a third-year medical student working with Dr. Smith today. Is it okay if I ask you some questions and perform an assessment?
Patient: Sure, that's fine.
Doctor: Thank you. Can I confirm your preferred name and pronouns?
Patient: Yes, call me Sarah. She/her.
Doctor: Great, thanks, Sarah. What brings you in today?
Patient: I've been feeling short of breath for the past few weeks, especially when climbing stairs.
Doctor: Okay, thanks for sharing that. How old are you, and can I confirm some basic details?
Patient: I'm 54, I live with my husband, and I work as an accountant.
Doctor: Perfect. And where are you living right now?
Patient: Downtown, in a condo.
Doctor: Got it. Do you have any significant medical conditions?
Patient: I was diagnosed with type 2 diabetes five years ago, and I also have mild asthma.
Doctor: Any surgeries or hospitalizations in the past?
Patient: I had my gallbladder removed 10 years ago and was admitted once for pneumonia.
Doctor: Thank you. Are you up to date on vaccinations like flu and pneumonia?
Patient: Yes, mostly.
Doctor: Okay. I also need to ask — are you currently sexually active?
Patient: Yes.
Doctor: Any history of STIs?
Patient: No, never.
Doctor: Do you have any allergies?
Patient: Yes, peanuts — I carry an EpiPen.
Doctor: Perfect. Are you taking any medications right now?
Patient: Yes, metformin 500 mg twice daily and salbutamol inhaler as needed.
Doctor: Great, and how often do you use your inhaler?
Patient: Maybe twice a week.
Doctor: Any over-the-counter meds, supplements, or recreational drugs?
Patient: Just a multivitamin. No drugs.
Doctor: Excellent. Do you smoke or vape?
Patient: Yes, about half a pack a day for 20 years.
Doctor: Thanks. Do you drink alcohol?
Patient: Occasionally, maybe one or two drinks on weekends.
Doctor: Okay. How's your diet and exercise?
Patient: I try to follow a low-carb diet, but I don't exercise much.
Doctor: How much physical activity do you usually get per week?
Patient: Maybe a 20-minute walk three times a week.
Doctor: Any trouble sleeping? Do you nap during the day?
Patient: I usually sleep six hours, and yes, I nap about 30 minutes in the afternoons.
Doctor: Got it. How's your mood and stress lately?
Patient: Pretty stressed at work, honestly.
Doctor: How do you cope with stress?
Patient: I usually talk to my husband or watch TV.
Doctor: That makes sense. Do you have a strong social support network?
Patient: Yes, my family is very supportive.
Doctor: Do you have an advance-care plan in place in case of emergencies?
Patient: No, I don't.
Doctor: Okay, that's something we can talk about later. Are there any major illnesses in your family?
Patient: My dad had a heart attack at 62, my mom has high blood pressure, and my sister has type 2 diabetes.
Doctor: Thank you. Just to be thorough, have you noticed any chest pain, palpitations, swelling, cough, or wheezing lately?
Patient: Some wheezing, yes, but no chest pain or swelling.
Doctor: Any vision changes, numbness, or tingling in your feet?
Patient: My vision has been a little blurry lately, and sometimes I feel tingling in my toes.
Doctor: Thanks. Based on what we've discussed, I'd recommend carrying your EpiPen at all times, monitoring your blood sugars regularly, and aiming for 150 minutes of exercise per week. Would you like me to give you resources on smoking cessation and stress management techniques?
Patient: Yes, please.
Doctor: Perfect. There are great nicotine replacement options and mindfulness tools I can share with you. Does that sound okay?
Patient: Yes, that would be helpful.
Doctor: Great. That covers what I needed for now. Do you have any questions for me?
Patient: No, I think that's everything.
Doctor: Thanks, Sarah. We'll work together to make sure we manage your symptoms well."""
    
    result = await service.evaluate_all_categories(transcript)
    
    print("\n=== OSCE Interview Performance Analysis ===")
    print(f"\nOverall Score: {result['total_score']}/{result['max_possible']} ({(result['total_score']/result['max_possible']*100):.1f}%)")
    
    print("\nStrengths:")
    strengths = []
    for category, score in result['scores'].items():
        max_score = 10 if category == "clinical_judgment" else 5
        percentage = (score/max_score) * 100
        if percentage >= 80:  # 80% or higher is a strength
            strengths.append(f"- {category.replace('_', ' ').title()}: {score}/{max_score} ({percentage:.1f}%)")
    print("\n".join(strengths) if strengths else "- None identified")
    
    print("\nAreas for Improvement:")
    improvements = []
    for category, score in result['scores'].items():
        max_score = 10 if category == "clinical_judgment" else 5
        percentage = (score/max_score) * 100
        if percentage < 60:  # Less than 60% needs improvement
            improvements.append(f"- {category.replace('_', ' ').title()}: {score}/{max_score} ({percentage:.1f}%)")
    print("\n".join(improvements) if improvements else "- None identified")
    
    print("\nDetailed Scores:")
    for category, score in result['scores'].items():
        max_score = 10 if category == "clinical_judgment" else 5
        percentage = (score/max_score) * 100
        print(f"{category.replace('_', ' ').title()}: {score}/{max_score} ({percentage:.1f}%)")
        print(f"  {result['feedback'][category]}")
    
    print(f"\nOverall Feedback: {result['feedback']['overall']}")
    
    # No assertions - this is just for analysis

@pytest.mark.asyncio
async def test_detailed_interview():
    service = SpecializedEvaluationService()  # Will use OpenAI
    
    transcript = """Doctor: Hi, my name is Alex Kim. I'm a third-year medical student working with Dr. Smith today. Is it okay if I ask you some questions and perform an assessment?
Patient: Sure, that's fine.
Doctor: Thank you. Can I confirm your preferred name and pronouns?
Patient: Yes, call me Sarah. She/her.
Doctor: Great, thanks Sarah. What brings you in today?
Patient: I've been feeling short of breath for the past few weeks, especially when climbing stairs.
Doctor: I'm sorry to hear that. Let's go through this carefully. When did it start, and has it been getting worse?
Patient: About three weeks ago, and it's been getting worse.
Doctor: How does it affect your daily activities — for example, climbing stairs or walking?
Patient: I used to climb three flights of stairs, but now I get winded after one.
Doctor: Do you get short of breath at rest, or only with exertion?
Patient: Only with exertion.
Doctor: Do you wake up short of breath at night, or need extra pillows to sleep?
Patient: No.
Doctor: Any chest pain, palpitations, swelling in your legs, or coughing up blood?
Patient: No chest pain or swelling, but I sometimes wheeze.
Doctor: Do you produce any cough or sputum?
Patient: Not usually.
Doctor: Any fevers, night sweats, or weight loss?
Patient: No.
Doctor: Any recent travel, new pets, or occupational exposures to dust, chemicals, or mold?
Patient: No, none of those.
Doctor: Do you have any medical conditions?
Patient: Type 2 diabetes for five years, and mild asthma.
Doctor: Any surgeries or hospitalizations?
Patient: Gallbladder removed ten years ago, and hospitalized once for pneumonia.
Doctor: Thank you.
Doctor: What medications do you take?
Patient: Metformin 500 mg twice daily, salbutamol inhaler as needed.
Doctor: How often do you use your inhaler?
Patient: Maybe twice a week.
Doctor: Any over-the-counter meds, supplements, or recreational drugs?
Patient: Just a multivitamin. No drugs.
Doctor: Do you have any allergies?
Patient: Yes, peanuts. I carry an EpiPen.
Doctor: Any major illnesses in your family?
Patient: My dad had a heart attack at 62, my mom has high blood pressure, and my sister has diabetes.
Doctor: Do you smoke or vape?
Patient: Yes, half a pack a day for 20 years.
Doctor: Do you drink alcohol?
Patient: Occasionally, one or two drinks on weekends.
Doctor: What's your diet like?
Patient: I try to follow a low-carb diet.
Doctor: And exercise?
Patient: A 20-minute walk three times a week.
Doctor: How's your sleep? Any snoring or daytime sleepiness?
Patient: I sleep about six hours. I nap sometimes, and my husband says I snore.
Doctor: How's your mood and stress level?
Patient: Pretty stressed at work.
Doctor: How do you usually cope?
Patient: I talk to my husband or watch TV.
Doctor: That's good. Do you feel you have good support at home?
Patient: Yes, very supportive.
Doctor: And what do you do for work?
Patient: I'm an accountant.
Doctor: Just to check — any vision changes, numbness, or tingling in your feet?
Patient: Yes, a bit of blurry vision and tingling in my toes.
Doctor: Any changes in urination or infections?
Patient: No.
Doctor: Any reflux, heartburn, or stomach issues?
Patient: No.
Doctor: Sarah, thank you for sharing all of that. To summarize: you've had worsening shortness of breath on exertion for three weeks, with some wheezing, a history of diabetes and asthma, and you smoke half a pack a day. My main considerations are asthma, smoking-related lung disease, or possibly heart disease given your family history.
To figure this out, I'd like to examine you and order some tests — likely lung function tests, a chest X-ray, bloodwork, and possibly heart tests.
In the meantime:
Please keep your EpiPen with you at all times.
Monitor your blood sugars and follow up with your diabetes team.
Aim for at least 150 minutes of physical activity weekly.
I strongly recommend smoking cessation — we can support you with nicotine replacement or medications.
We'll also check your eyes and feet regularly because diabetes can affect them.
Vaccinations like flu and pneumonia are also very important for you.
If you develop severe shortness of breath, chest pain, or coughing up blood, please seek urgent care right away.
Do you have any questions or concerns?
Patient: No, that sounds good.
Doctor: Perfect. We'll work together to manage your symptoms and keep you healthy. Thank you, Sarah."""
    
    result = await service.evaluate_all_categories(transcript)
    
    print("\n=== OSCE Detailed Interview Performance Analysis ===")
    print(f"\nOverall Score: {result['total_score']}/{result['max_possible']} ({(result['total_score']/result['max_possible']*100):.1f}%)")
    
    print("\nStrengths:")
    strengths = []
    for category, score in result['scores'].items():
        max_score = 10 if category == "clinical_judgment" else 5
        percentage = (score/max_score) * 100
        if percentage >= 80:  # 80% or higher is a strength
            strengths.append(f"- {category.replace('_', ' ').title()}: {score}/{max_score} ({percentage:.1f}%)")
    print("\n".join(strengths) if strengths else "- None identified")
    
    print("\nAreas for Improvement:")
    improvements = []
    for category, score in result['scores'].items():
        max_score = 10 if category == "clinical_judgment" else 5
        percentage = (score/max_score) * 100
        if percentage < 60:  # Less than 60% needs improvement
            improvements.append(f"- {category.replace('_', ' ').title()}: {score}/{max_score} ({percentage:.1f}%)")
    print("\n".join(improvements) if improvements else "- None identified")
    
    print("\nDetailed Scores:")
    for category, score in result['scores'].items():
        max_score = 10 if category == "clinical_judgment" else 5
        percentage = (score/max_score) * 100
        print(f"{category.replace('_', ' ').title()}: {score}/{max_score} ({percentage:.1f}%)")
        print(f"  {result['feedback'][category]}")
    
    print(f"\nOverall Feedback: {result['feedback']['overall']}")
    
    # No assertions - this is just for analysis

@pytest.mark.asyncio
async def test_comprehensive_interview():
    service = SpecializedEvaluationService()  # Will use OpenAI
    
    transcript = """Doctor: Good morning. I'm Alex Kim, a third-year medical student working with Dr. Smith. I'd like to ask you some questions and do an exam to understand your breathing concerns. Is it alright to proceed?
Patient: Yes, that's okay.
Doctor: Thank you. What name do you prefer I use, and what pronouns do you use?
Patient: Sarah, and she/her.
Doctor: Thanks, Sarah. How old are you, and how would you describe your background or the main language you're most comfortable with?
Patient: I'm 54. I'm Canadian, and English is fine.
Doctor: Great. What brings you in today?
Patient: I've been short of breath for a few weeks, worse with stairs.
Doctor: When did this start, and how has it changed over time?
Patient: About three weeks ago, and it's getting worse.
Doctor: How far can you walk or how many flights of stairs before needing to stop?
Patient: One flight now; I used to do three.
Doctor: Any shortness of breath at rest, chest pain, palpitations, ankle swelling, or coughing up blood?
Patient: No chest pain or swelling. I wheeze sometimes. No blood.
Doctor: Do you have cough or sputum? Fevers, night sweats, or unintentional weight loss?
Patient: Rare cough, no sputum. No fevers, sweats, or weight loss.
Doctor: Any recent travel, new pets, or workplace exposures to dust, fumes, or mold?
Patient: None.

Doctor: I'll ask about your medical history. What long-term conditions have you been diagnosed with?
Patient: Type 2 diabetes for five years and mild asthma.
Doctor: Have you ever had surgeries or been in hospital?
Patient: Yes—gallbladder removed ten years ago, and I was hospitalized once with pneumonia.
Doctor: Any past illnesses or infections besides that pneumonia? Childhood illnesses like chickenpox?
Patient: I had chickenpox as a kid; otherwise nothing major.
Doctor: Are your vaccinations up to date—flu, COVID boosters, pneumonia, tetanus?
Patient: Yes—flu this season, COVID booster last fall, tetanus a couple of years ago. I had a pneumonia shot two years ago.
Doctor: Any history of depression, anxiety, or other mental health conditions or treatment?
Patient: No diagnoses. I've felt stressed but never saw a therapist.
Doctor: Are you currently sexually active? Any concerns about STIs or need for contraception?
Patient: Yes, with my husband; no STI concerns.
Doctor: Any pregnancies or gynecologic history I should know—pregnancies, menopause, abnormal bleeding?
Patient: Two pregnancies, both vaginal deliveries. I'm post-menopausal for three years, no abnormal bleeding.
Doctor: Do you have any allergies to medications, foods, or other exposures?
Patient: Peanuts—carry an EpiPen. No drug allergies.

Doctor: Let's review medications. Please include dose and how often you take each.
Patient: Metformin 500 mg twice a day; salbutamol inhaler 2 puffs as needed—usually twice a week; atorvastatin 20 mg at night.
Doctor: Any over-the-counter medications?
Patient: Ibuprofen 200 mg about once a week for headaches; a daily multivitamin.
Doctor: Herbal or natural products?
Patient: Omega-3, 1000 mg once daily.
Doctor: Any recreational drug use? If none, I'll note that.
Patient: None.
Doctor: Have you had any side effects or adverse reactions to medicines or vaccines?
Patient: No.

Doctor: I'll ask about your family's health. Do your parents have any medical conditions?
Patient: My dad had a heart attack at 62; my mom has high blood pressure and high cholesterol.
Doctor: Any conditions among siblings or your children?
Patient: My sister has type 2 diabetes. My two adult children are healthy.
Doctor: How about your grandparents?
Patient: My maternal grandmother had a stroke in her 70s; paternal grandfather had type 2 diabetes.
Doctor: Any significant illnesses in your extended family—like breast or colon cancer?
Patient: An uncle had colon cancer in his 60s.

Doctor: I'd like to understand daily function. How active are you in a typical week—frequency, duration, and intensity?
Patient: I walk 25 minutes, four days a week—moderate pace.
Doctor: Do you use any mobility aids like a cane or walker?
Patient: No.
Doctor: How is your sleep? Do you take daytime naps?
Patient: I sleep about six hours. I nap 20–30 minutes most afternoons.
Doctor: Tell me about your nutrition—any specific patterns or restrictions?
Patient: Lower-carb diet; I try to include vegetables and lean protein.
Doctor: Any bowel or bladder issues—constipation, diarrhea, urgency, or nighttime urination?
Patient: Occasional constipation; no urinary issues.
Doctor: Are you independent with daily activities like bathing, dressing, cooking, and shopping?
Patient: Yes, fully independent.

Doctor: I'll cover coping and lifestyle. On average, how much do you smoke, and for how many years?
Patient: Half a pack a day for 20 years.
Doctor: I'll record that as about 10 pack-years. Do you vape?
Patient: No.
Doctor: How much alcohol do you drink in a typical week—number of standard drinks?
Patient: Two to three drinks on weekends.
Doctor: You mentioned stress. What strategies do you use to manage it?
Patient: Talking with my husband and walking after dinner.
Doctor: When stress is higher, what else helps—have you tried breathing exercises, mindfulness apps, or journaling?
Patient: Deep breathing helps; I haven't tried apps or journaling.
Doctor: How is your mood overall—down, little interest, or anxiety symptoms in the past two weeks?
Patient: Some worry with work deadlines but otherwise okay.
Doctor: Who is in your support network?
Patient: My husband and close friends.
Doctor: Have you ever discussed advance-care planning—naming a decision-maker or outlining your preferences?
Patient: Not formally.
Doctor: We can provide information and a form if you'd like.

Doctor: I'll do a brief review of systems related to your diabetes, asthma, and family heart history. Any chest pain, pressure, palpitations, orthopnea, or waking up short of breath at night?
Patient: No chest pain, no orthopnea or waking short of breath.
Doctor: Respiratory—cough, sputum, wheeze, or tightness?
Patient: Intermittent wheeze; no sputum.
Doctor: Endocrine—excess thirst, frequent urination, increased hunger, heat or cold intolerance, recent weight change?
Patient: More thirsty lately and up once at night to urinate; weight is stable.
Doctor: Neurologic—headaches, dizziness, numbness, tingling, or weakness?
Patient: Tingling in toes, no weakness.
Doctor: Eyes/vision—any blurriness or changes?
Patient: Some blurriness recently.
Doctor: Skin/feet—any sores, color changes, or slow-healing wounds?
Patient: No sores; skin looks normal.
Doctor: Gastrointestinal—nausea, abdominal pain, or changes in bowel habits beyond the occasional constipation you mentioned?
Patient: No.
Doctor: Genitourinary—burning with urination or recurrent infections?
Patient: No.

Doctor: Thanks, Sarah. Here's what I'm hearing: three weeks of exertional shortness of breath with intermittent wheeze in the context of asthma, tobacco use (~10 pack-years), type 2 diabetes, and a family history of cardiovascular disease. My working considerations are asthma with increased symptoms, smoking-related airway disease, and we should also screen for cardiac causes given your risk profile.

Doctor: Plan, in brief. Please stop me if anything is unclear.

Testing: spirometry with bronchodilator, chest X-ray, ECG, and basic labs (A1c, lipid panel). We'll also check urine albumin and schedule a dilated eye exam and foot exam. Does this plan make sense so far?
Patient: Yes.
Doctor: 2) Medications: continue metformin 500 mg twice daily and atorvastatin 20 mg nightly. Use salbutamol 2 puffs as needed; if you need it more than twice a week, let us know—we may add a daily inhaler. Any questions about your current doses or timing?
Patient: No, that's clear.
Doctor: 3) Smoking cessation: quitting will help breathing and heart risk. Options include nicotine patch or gum, varenicline, and counseling. Would you like written resources and a quit-line referral?
Patient: Yes, please.
Doctor: 4) Physical activity and diet: target at least 150 minutes per week of moderate activity—your 25-minute walks four days a week are a great start; increasing to five or six days would meet the goal. After-meal walks can help glucose control. Are you comfortable trying that?
Patient: Yes.
Doctor: 5) Allergy preparedness: always carry your EpiPen and check the expiry date. Would you like a replacement prescription if it's close to expiring?
Patient: That would be helpful.
Doctor: 6) Vaccinations and screening: stay current with flu, COVID boosters, and pneumonia vaccines; we'll confirm dates today. Home blood-pressure checks once or twice weekly would be useful, given family history.
Patient: Okay.
Doctor: 7) Stress management: two options to try this week—five-minute box-breathing twice daily and a mindfulness app. Would journaling in the evening be practical for you?
Patient: I can try the app and journaling.
Doctor: 8) Advance-care planning: I'll give you a short guide to name a decision-maker and outline preferences. Can I send that through the patient portal?
Patient: Yes, please.

Doctor: To be sure I explained everything clearly, could you summarize the top two or three steps you'll start with?
Patient: I'll start the smoking-cessation plan, increase my walks, and keep my EpiPen with me.
Doctor: Perfect—that matches my recommendations. What questions do you have for me?
Patient: None right now.
Doctor: If you notice severe shortness of breath, chest pain, or coughing up blood, seek urgent care immediately. Otherwise we'll follow up after your tests. Thanks for talking with me today, Sarah.
Patient: Thank you."""
    
    result = await service.evaluate_all_categories(transcript)
    
    print("\n=== OSCE Comprehensive Interview Performance Analysis ===")
    print(f"\nOverall Score: {result['total_score']}/{result['max_possible']} ({(result['total_score']/result['max_possible']*100):.1f}%)")
    
    print("\nStrengths:")
    strengths = []
    for category, score in result['scores'].items():
        max_score = 10 if category == "clinical_judgment" else 5
        percentage = (score/max_score) * 100
        if percentage >= 80:  # 80% or higher is a strength
            strengths.append(f"- {category.replace('_', ' ').title()}: {score}/{max_score} ({percentage:.1f}%)")
    print("\n".join(strengths) if strengths else "- None identified")
    
    print("\nAreas for Improvement:")
    improvements = []
    for category, score in result['scores'].items():
        max_score = 10 if category == "clinical_judgment" else 5
        percentage = (score/max_score) * 100
        if percentage < 60:  # Less than 60% needs improvement
            improvements.append(f"- {category.replace('_', ' ').title()}: {score}/{max_score} ({percentage:.1f}%)")
    print("\n".join(improvements) if improvements else "- None identified")
    
    print("\nDetailed Scores:")
    for category, score in result['scores'].items():
        max_score = 10 if category == "clinical_judgment" else 5
        percentage = (score/max_score) * 100
        print(f"{category.replace('_', ' ').title()}: {score}/{max_score} ({percentage:.1f}%)")
        print(f"  {result['feedback'][category]}")
    
    print(f"\nOverall Feedback: {result['feedback']['overall']}")
    
    # No assertions - this is just for analysis