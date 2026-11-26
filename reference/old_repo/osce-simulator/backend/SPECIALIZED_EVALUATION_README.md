# Specialized OSCE Evaluation System

This document explains the new specialized evaluation system that uses individual GPT agents for each OSCE category, providing more precise and consistent evaluations.

## Overview

The specialized evaluation system replaces the generic single-prompt evaluation with 13 specialized agents, each focused on a specific OSCE category. This approach ensures:

- **Consistency**: Each category uses the same evaluation criteria every time
- **Precision**: Specialized prompts for each category lead to more accurate scoring
- **Transparency**: Clear scoring rubrics for each category
- **Maintainability**: Easy to update individual category criteria without affecting others

## Architecture

### Evaluation Categories

The system evaluates 13 categories across two main groups:

#### Core Assessment Categories (48 points total)
1. **Introduction & Collaboration** (0-5 points)
   - Self-introduction and role
   - Greeting and explicit consent
   - Reason for visit (chief complaint)
   - Preferred name and/or pronouns
   - Demographics (age, gender)
   - Occupational status
   - Relationship or marital status
   - Living situation or address
   - Language or cultural background

2. **Past Medical History Part 2** (0-6 points)
   - Current medications (prescription and OTC)
   - Medication dosages and frequency
   - Medication adherence and compliance
   - Medication side effects or adverse reactions
   - Allergies (medications, foods, environmental)
   - Allergy severity and reactions
   - Previous medication trials and outcomes
   - Medication interactions or contraindications

3. **Family History** (0-6 points)
   - First generation (parents) - health conditions
   - Second generation (grandparents) - health conditions
   - Third generation (siblings, aunts/uncles) - health conditions
   - Hereditary conditions or genetic risks
   - Age of onset for family conditions
   - Cause of death for deceased family members
   - Ethnic/racial background and genetic considerations
   - Family patterns of disease

4. **Functional Assessment Part 1** (0-6 points)
   - Activity level and exercise patterns
   - Mobility and ambulation status
   - Sleep patterns and quality
   - Nutrition and dietary habits
   - Elimination patterns (bowel and bladder)
   - Activities of daily living (ADLs)
   - Instrumental activities of daily living (IADLs)
   - Functional limitations or disabilities

5. **Functional Assessment Part 2** (0-6 points)
   - Coping mechanisms and stress management
   - Smoking history and current status
   - Vaping or e-cigarette use
   - Alcohol consumption patterns
   - Recreational drug use
   - Advanced care planning preferences
   - Living will or advance directives
   - Healthcare proxy or power of attorney

6. **Review of Systems** (0-6 points)
   - Cardiovascular system review
   - Respiratory system review
   - Gastrointestinal system review
   - Neurological system review
   - Musculoskeletal system review
   - Integumentary system review
   - Relevance to patient's medical history
   - Relevance to family history

7. **Health Promotion Opportunities** (0-6 points)
   - Identification of health promotion needs
   - Nutrition and diet counseling
   - Exercise and physical activity recommendations
   - Smoking cessation support
   - Alcohol moderation guidance
   - Stress management techniques
   - Preventive care recommendations
   - Lifestyle modification suggestions

8. **Quality of Health Promotion** (0-6 points)
   - Breaks down complex information appropriately
   - Verifies patient understanding
   - Uses evidence-based recommendations
   - Tailors information to patient needs
   - Uses appropriate language and terminology
   - Encourages patient engagement
   - Provides practical, actionable advice
   - Follows up on patient comprehension

#### Global Appreciation Categories (34 points total)
9. **Patient Centered Care** (0-6 points)
   - Validates patient experience and concerns
   - Considers patient beliefs and values
   - Adapts interactions to patient needs
   - Respects patient autonomy and preferences
   - Shows empathy and understanding
   - Involves patient in decision-making
   - Addresses patient fears and anxieties
   - Cultural sensitivity and awareness

10. **Interview Style** (0-6 points)
    - Uses open-ended questions appropriately
    - Guides with purposeful close-ended questions
    - Avoids negative phrasing
    - Uses statements instead of questions when appropriate
    - Maintains conversational flow
    - Demonstrates active listening
    - Uses appropriate transitions
    - Manages interview pace effectively

11. **Organization** (0-6 points)
    - Completes assessment in orderly manner
    - Uses logical sequence of questions
    - Maintains focus and avoids tangents
    - Transitions smoothly between sections
    - Manages time effectively
    - Prioritizes information gathering
    - Demonstrates systematic approach
    - Completes all necessary sections

12. **Clinical Judgment** (0-10 points)
    - Demonstrates sound clinical knowledge
    - Shows knowledge of pertinent clinical data
    - Uses appropriate clinical reasoning
    - Identifies relevant risk factors
    - Recognizes clinical patterns
    - Applies evidence-based practice
    - Demonstrates critical thinking
    - Shows understanding of pathophysiology
    - Uses appropriate clinical terminology
    - Demonstrates clinical judgment

13. **Professionalism** (0-6 points)
    - Maintains professional demeanor
    - Shows respect for patient dignity
    - Maintains appropriate boundaries
    - Demonstrates ethical behavior
    - Shows cultural sensitivity
    - Maintains confidentiality
    - Demonstrates accountability
    - Shows commitment to patient care

## Usage

### API Endpoint

The specialized evaluation is automatically used when calling the evaluation endpoint:

```bash
POST /api/evaluate
```

### Request Body

```json
{
  "case_id": "SCN_SAYLOR",
  "conversation_id": "conv_123",
  "notes": "Optional SOAP notes",
  "time_taken": 1800
}
```

### Response

The response includes scores and detailed feedback for each category:

```json
{
  "case_id": "SCN_SAYLOR",
  "conversation_id": "conv_123",
  "scores": {
    "introduction_collaboration": 4,
    "past_medical_history_part2": 5,
    "family_history": 4,
    "functional_assessment_part1": 3,
    "functional_assessment_part2": 4,
    "review_of_systems": 3,
    "health_promotion_opportunities": 4,
    "quality_health_promotion": 3,
    "patient_centered_care": 5,
    "interview_style": 4,
    "organization": 4,
    "clinical_judgment": 7,
    "professionalism": 5
  },
  "weighted_total": 59,
  "out_of": 82,
  "feedback": {
    "introduction_collaboration": "Good coverage of most elements...",
    "past_medical_history_part2": "Comprehensive medication assessment...",
    // ... other category feedback
    "overall": "Overall Assessment: Good (59/82 points). The student demonstrates solid clinical assessment skills..."
  }
}
```

## Testing

### Run the Test Script

```bash
cd backend
python test_specialized_evaluation.py
```

This will test the specialized evaluation system with sample data and show how each category is evaluated.

### Expected Output

The test script will show:
- Individual category scores and feedback
- Total score calculation
- Overall assessment with recommendations
- Individual category evaluation demonstration

## Customization

### Adding New Categories

To add a new evaluation category:

1. Create a new method in `LangChainService`:
```python
async def evaluate_new_category(self, transcript: str, case_details: Optional[dict] = None) -> tuple[int, str]:
    prompt = ChatPromptTemplate.from_template("""
    Your specialized prompt here...
    """)
    # Implementation...
```

2. Add it to the `evaluate_performance_specialized` method
3. Update the schemas in `evaluation.py`
4. Update the API endpoint in `main.py`

### Modifying Existing Categories

To modify an existing category's evaluation criteria:

1. Update the prompt template in the corresponding evaluation method
2. Adjust the scoring rubric if needed
3. Test with the test script

### Scoring Rubrics

Each category has its own scoring rubric that can be customized:

- **Introduction & Collaboration**: 0-5 points (consent required for any points)
- **Most categories**: 0-6 points
- **Clinical Judgment**: 0-10 points

## Benefits

1. **Consistency**: Same criteria applied every time
2. **Accuracy**: Specialized prompts lead to better evaluations
3. **Transparency**: Clear scoring criteria for each category
4. **Maintainability**: Easy to update individual categories
5. **Scalability**: Easy to add new categories or modify existing ones
6. **Debugging**: Individual category evaluation for troubleshooting

## Troubleshooting

### Common Issues

1. **JSON Parsing Errors**: The system includes robust JSON parsing with fallbacks
2. **API Key Issues**: Ensure your OpenAI API key is properly configured
3. **Memory Issues**: Each evaluation makes 13 API calls, monitor usage

### Debug Mode

Enable debug logging to see individual LLM responses:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Fallback System

If any individual category evaluation fails, the system:
- Logs the error
- Assigns a score of 0
- Provides error feedback
- Continues with other categories
- Generates overall assessment based on successful evaluations

## Performance Considerations

- **API Calls**: Each evaluation makes 13 API calls to GPT
- **Latency**: Total evaluation time is the sum of all individual evaluations
- **Cost**: 13x the cost of single evaluation
- **Reliability**: Individual failures don't break the entire evaluation

## Future Enhancements

1. **Parallel Evaluation**: Run category evaluations concurrently
2. **Caching**: Cache common evaluation patterns
3. **Batch Processing**: Evaluate multiple conversations simultaneously
4. **Custom Models**: Use different models for different categories
5. **Learning**: Improve prompts based on evaluation feedback

## Support

For questions or issues with the specialized evaluation system:

1. Check the logs for detailed error messages
2. Run the test script to verify functionality
3. Review the individual category evaluation methods
4. Check API key configuration and rate limits
