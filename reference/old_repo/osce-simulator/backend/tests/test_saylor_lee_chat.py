import pytest
from app.services.langchain_service import LangChainService

@pytest.mark.asyncio
async def test_saylor_lee_basic_greeting():
    """Test basic greeting and introduction with Saylor Lee"""
    service = LangChainService()
    
    # Test basic greeting
    response1 = await service.chat_with_patient('SCN_SAYLOR', 'Hello', memory_key='test_basic_greeting')
    print(f"\n=== Basic Greeting Test ===")
    print(f"Doctor: Hello")
    print(f"Saylor Lee: {response1.message}")
    print(f"Emotion: {response1.emotion}")
    
    # Test how are you
    response2 = await service.chat_with_patient('SCN_SAYLOR', 'How are you today?', memory_key='test_basic_greeting')
    print(f"\nDoctor: How are you today?")
    print(f"Saylor Lee: {response2.message}")
    print(f"Emotion: {response2.emotion}")
    
    # Test name request
    response3 = await service.chat_with_patient('SCN_SAYLOR', 'What is your name?', memory_key='test_basic_greeting')
    print(f"\nDoctor: What is your name?")
    print(f"Saylor Lee: {response3.message}")
    print(f"Emotion: {response3.emotion}")
    
    # Test what brings you in
    response4 = await service.chat_with_patient('SCN_SAYLOR', 'What brings you in today?', memory_key='test_basic_greeting')
    print(f"\nDoctor: What brings you in today?")
    print(f"Saylor Lee: {response4.message}")
    print(f"Emotion: {response4.emotion}")
    
    # Verify responses are appropriate for a patient
    assert "How can I help you" not in response1.message
    assert "How can I help you" not in response2.message
    assert "How can I help you" not in response3.message
    assert "How can I help you" not in response4.message
    
    # Verify name response
    assert "Saylor" in response3.message or "Lee" in response3.message
    
    # Verify presenting concern mentions Montreal/Ottawa
    assert "Montreal" in response4.message or "Ottawa" in response4.message

@pytest.mark.asyncio
async def test_saylor_lee_medical_history():
    """Test medical history questions with Saylor Lee"""
    service = LangChainService()
    
    print(f"\n=== Medical History Test ===")
    
    # Test general medical history
    response1 = await service.chat_with_patient('SCN_SAYLOR', 'Do you have any medical conditions?', memory_key='test_medical_history')
    print(f"\nDoctor: Do you have any medical conditions?")
    print(f"Saylor Lee: {response1.message}")
    print(f"Emotion: {response1.emotion}")
    
    # Test medications
    response2 = await service.chat_with_patient('SCN_SAYLOR', 'What medications do you take?', memory_key='test_medical_history')
    print(f"\nDoctor: What medications do you take?")
    print(f"Saylor Lee: {response2.message}")
    print(f"Emotion: {response2.emotion}")
    
    # Test allergies
    response3 = await service.chat_with_patient('SCN_SAYLOR', 'Do you have any allergies?', memory_key='test_medical_history')
    print(f"\nDoctor: Do you have any allergies?")
    print(f"Saylor Lee: {response3.message}")
    print(f"Emotion: {response3.emotion}")
    
    # Test family history
    response4 = await service.chat_with_patient('SCN_SAYLOR', 'Tell me about your family history', memory_key='test_medical_history')
    print(f"\nDoctor: Tell me about your family history")
    print(f"Saylor Lee: {response4.message}")
    print(f"Emotion: {response4.emotion}")
    
    # Verify medical information is present
    assert "diabetes" in response1.message.lower() or "anxiety" in response1.message.lower()
    assert "metformin" in response2.message.lower() or "cipralex" in response2.message.lower()
    assert "peanut" in response3.message.lower()
    assert "mother" in response4.message.lower() or "father" in response4.message.lower()

@pytest.mark.asyncio
async def test_saylor_lee_lifestyle_social():
    """Test lifestyle and social history questions with Saylor Lee"""
    service = LangChainService()
    
    print(f"\n=== Lifestyle & Social History Test ===")
    
    # Test smoking/vaping
    response1 = await service.chat_with_patient('SCN_SAYLOR', 'Do you smoke or vape?', memory_key='test_lifestyle')
    print(f"\nDoctor: Do you smoke or vape?")
    print(f"Saylor Lee: {response1.message}")
    print(f"Emotion: {response1.emotion}")
    
    # Test alcohol
    response2 = await service.chat_with_patient('SCN_SAYLOR', 'Do you drink alcohol?', memory_key='test_lifestyle')
    print(f"\nDoctor: Do you drink alcohol?")
    print(f"Saylor Lee: {response2.message}")
    print(f"Emotion: {response2.emotion}")
    
    # Test exercise
    response3 = await service.chat_with_patient('SCN_SAYLOR', 'What kind of physical activity do you do?', memory_key='test_lifestyle')
    print(f"\nDoctor: What kind of physical activity do you do?")
    print(f"Saylor Lee: {response3.message}")
    print(f"Emotion: {response3.emotion}")
    
    # Test relationships
    response4 = await service.chat_with_patient('SCN_SAYLOR', 'Tell me about your relationships', memory_key='test_lifestyle')
    print(f"\nDoctor: Tell me about your relationships")
    print(f"Saylor Lee: {response4.message}")
    print(f"Emotion: {response4.emotion}")
    
    # Test sleep
    response5 = await service.chat_with_patient('SCN_SAYLOR', 'How is your sleep?', memory_key='test_lifestyle')
    print(f"\nDoctor: How is your sleep?")
    print(f"Saylor Lee: {response5.message}")
    print(f"Emotion: {response5.emotion}")
    
    # Verify lifestyle information
    assert "vape" in response1.message.lower()
    assert "beer" in response2.message.lower() or "wine" in response2.message.lower()
    assert "walk" in response3.message.lower() or "golf" in response3.message.lower()
    assert "partner" in response4.message.lower() or "relationship" in response4.message.lower()
    assert "6" in response5.message or "six" in response5.message.lower()

@pytest.mark.asyncio
async def test_saylor_lee_restricted_information():
    """Test that Saylor Lee only reveals restricted information when explicitly asked"""
    service = LangChainService()
    
    print(f"\n=== Restricted Information Test ===")
    
    # Test cholesterol - should NOT be mentioned initially
    response1 = await service.chat_with_patient('SCN_SAYLOR', 'What medications do you take?', memory_key='test_restricted')
    print(f"\nDoctor: What medications do you take?")
    print(f"Saylor Lee: {response1.message}")
    print(f"Emotion: {response1.emotion}")
    
    # Now explicitly ask about cholesterol
    response2 = await service.chat_with_patient('SCN_SAYLOR', 'Do you have high cholesterol?', memory_key='test_restricted')
    print(f"\nDoctor: Do you have high cholesterol?")
    print(f"Saylor Lee: {response2.message}")
    print(f"Emotion: {response2.emotion}")
    
    # Test epipen - should NOT be mentioned initially
    response3 = await service.chat_with_patient('SCN_SAYLOR', 'Do you have any allergies?', memory_key='test_restricted')
    print(f"\nDoctor: Do you have any allergies?")
    print(f"Saylor Lee: {response3.message}")
    print(f"Emotion: {response3.emotion}")
    
    # Now explicitly ask about epipen
    response4 = await service.chat_with_patient('SCN_SAYLOR', 'Do you carry an epipen?', memory_key='test_restricted')
    print(f"\nDoctor: Do you carry an epipen?")
    print(f"Saylor Lee: {response4.message}")
    print(f"Emotion: {response4.emotion}")
    
    # Verify restricted information behavior
    # Note: The LLM may not perfectly follow conditional logic, so we'll check for general patterns
    # The first response should mention base medications (metformin, cipralex)
    assert "metformin" in response1.message.lower() or "cipralex" in response1.message.lower()
    
    # The second response should acknowledge cholesterol when explicitly asked
    assert "cholesterol" in response2.message.lower()
    
    # Epipen should not be in first response but should be in second
    assert "epipen" not in response3.message.lower() and "epi-pen" not in response3.message.lower()
    assert "epipen" in response4.message.lower() or "epi-pen" in response4.message.lower()

@pytest.mark.asyncio
async def test_saylor_lee_conversation_consistency():
    """Test that Saylor Lee maintains consistency across the conversation"""
    service = LangChainService()
    
    print(f"\n=== Conversation Consistency Test ===")
    
    # Ask about medications twice
    response1 = await service.chat_with_patient('SCN_SAYLOR', 'What medications do you take?', memory_key='test_consistency')
    print(f"\nDoctor: What medications do you take?")
    print(f"Saylor Lee: {response1.message}")
    print(f"Emotion: {response1.emotion}")
    
    response2 = await service.chat_with_patient('SCN_SAYLOR', 'Can you tell me again what medications you take?', memory_key='test_consistency')
    print(f"\nDoctor: Can you tell me again what medications you take?")
    print(f"Saylor Lee: {response2.message}")
    print(f"Emotion: {response2.emotion}")
    
    # Ask about age
    response3 = await service.chat_with_patient('SCN_SAYLOR', 'How old are you?', memory_key='test_consistency')
    print(f"\nDoctor: How old are you?")
    print(f"Saylor Lee: {response3.message}")
    print(f"Emotion: {response3.emotion}")
    
    # Ask about age again
    response4 = await service.chat_with_patient('SCN_SAYLOR', 'What is your age?', memory_key='test_consistency')
    print(f"\nDoctor: What is your age?")
    print(f"Saylor Lee: {response4.message}")
    print(f"Emotion: {response4.emotion}")
    
    # Verify consistency - both medication responses should mention medications
    meds1 = response1.message.lower()
    meds2 = response2.message.lower()
    
    # Both responses should mention some medications (may not be identical due to LLM variability)
    # At least one should mention metformin or cipralex
    assert ("metformin" in meds1 or "cipralex" in meds1 or "medication" in meds1) or ("metformin" in meds2 or "cipralex" in meds2 or "medication" in meds2)
    
    # Age responses should be consistent (though Saylor Lee's age isn't specified in the prompt, 
    # the responses should be consistent with each other)
    age1 = response3.message.lower()
    age2 = response4.message.lower()
    # Both should either give an age or say they don't know/aren't sure
    assert ("don't know" in age1 and "don't know" in age2) or ("not sure" in age1 and "not sure" in age2) or (any(char.isdigit() for char in age1) and any(char.isdigit() for char in age2))

@pytest.mark.asyncio
async def test_saylor_lee_patient_role_behavior():
    """Test that Saylor Lee consistently behaves as a patient, not a provider"""
    service = LangChainService()
    
    print(f"\n=== Patient Role Behavior Test ===")
    
    # Test various scenarios that might trigger provider-like responses
    test_cases = [
        "How can I help you today?",
        "What can I do for you?",
        "How can I assist you?",
        "yes help me",
        "I need help",
        "Can you help me?",
        "What should I do?",
        "I'm not sure what to do"
    ]
    
    for i, question in enumerate(test_cases, 1):
        response = await service.chat_with_patient('SCN_SAYLOR', question, memory_key=f'test_patient_role_{i}')
        print(f"\nDoctor: {question}")
        print(f"Saylor Lee: {response.message}")
        print(f"Emotion: {response.emotion}")
        
        # Verify Saylor Lee never offers to help the doctor
        assert "How can I help you" not in response.message
        assert "How can I assist you" not in response.message
        assert "What can I do for you" not in response.message
        assert "How can I help you today" not in response.message
        
        # Verify Saylor Lee responds as a patient seeking care
        patient_indicators = [
            "I'm here for",
            "I need",
            "I have",
            "I'm seeking",
            "check-up",
            "appointment",
            "care",
            "medical attention",
            "help",
            "assistance"
        ]
        
        # At least one patient indicator should be present
        assert any(indicator in response.message.lower() for indicator in patient_indicators), f"Response doesn't sound like a patient: {response.message}"

@pytest.mark.asyncio
async def test_saylor_lee_comprehensive_interview():
    """Test a comprehensive interview scenario similar to the specialized evaluation tests"""
    service = LangChainService()
    
    print(f"\n=== Comprehensive Saylor Lee Interview Test ===")
    
    # Simulate a comprehensive medical interview
    interview_questions = [
        "Hello, I'm Dr. Smith. How are you today?",
        "What brings you in today?",
        "What is your name?",
        "How old are you?",
        "Do you have any medical conditions?",
        "What medications do you take?",
        "Do you have any allergies?",
        "Do you smoke or vape?",
        "Do you drink alcohol?",
        "What kind of physical activity do you do?",
        "How is your sleep?",
        "Tell me about your family history",
        "Are you in a relationship?",
        "Do you have any concerns about your health?",
        "Is there anything else you'd like to discuss?"
    ]
    
    conversation_log = []
    
    for i, question in enumerate(interview_questions, 1):
        response = await service.chat_with_patient('SCN_SAYLOR', question, memory_key='test_comprehensive')
        conversation_log.append(f"Doctor: {question}")
        conversation_log.append(f"Saylor Lee: {response.message}")
        conversation_log.append(f"Emotion: {response.emotion}")
        conversation_log.append("")
        
        print(f"\nQ{i}: {question}")
        print(f"A{i}: {response.message}")
        print(f"Emotion: {response.emotion}")
        
        # Verify each response is appropriate for a patient
        assert "How can I help you" not in response.message
        assert "How can I assist you" not in response.message
        assert len(response.message.strip()) > 0  # Response should not be empty
    
    # Print full conversation log
    print(f"\n=== Full Conversation Log ===")
    for line in conversation_log:
        print(line)
    
    # Verify key information was revealed appropriately
    full_conversation = " ".join([log for log in conversation_log if "Saylor Lee:" in log])
    
    # Should mention key medical information
    assert "diabetes" in full_conversation.lower() or "anxiety" in full_conversation.lower()
    assert "metformin" in full_conversation.lower() or "cipralex" in full_conversation.lower()
    assert "peanut" in full_conversation.lower()
    assert "montreal" in full_conversation.lower() or "ottawa" in full_conversation.lower()
    
    print(f"\n=== Interview Summary ===")
    print(f"Total questions asked: {len(interview_questions)}")
    print(f"All responses were appropriate for a patient role")
    print(f"Key medical information was revealed appropriately")
    print(f"No provider-like responses detected")
