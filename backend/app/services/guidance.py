"""
Service for questionnaire validation and methodological guidance.
"""
from typing import List, Dict, Any, Tuple
from app.models.audit import Question, QuestionType


class MethodologicalGuidance:
    """
    Provides automated methodological guidance for questionnaire design.
    """
    
    # Validated instruments database
    VALIDATED_INSTRUMENTS = {
        "eq5d": {
            "name": "EQ-5D-5L",
            "description": "Quality of life measure",
            "domain": "patient_reported_outcomes",
        },
        "barthel": {
            "name": "Barthel Index",
            "description": "Activities of daily living",
            "domain": "functional_assessment",
        },
        "phq9": {
            "name": "PHQ-9",
            "description": "Depression screening",
            "domain": "mental_health",
        },
        "gad7": {
            "name": "GAD-7",
            "description": "Anxiety screening",
            "domain": "mental_health",
        },
    }
    
    @staticmethod
    def analyze_question(question_data: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
        """
        Analyze a question and provide methodological feedback.
        
        Returns:
            (has_warnings, warnings, suggestions)
        """
        warnings = []
        suggestions = []
        
        # Check for free text
        if question_data["question_type"] in [QuestionType.TEXT_SHORT, QuestionType.TEXT_LONG]:
            warnings.append("Free text is difficult to analyze quantitatively")
            suggestions.append("Consider using categorical options or validated scales instead")
            
            if not question_data.get("free_text_justification"):
                warnings.append("Free text requires justification")
        
        # Check for unclear categorical options
        if question_data["question_type"] in [
            QuestionType.CATEGORICAL_SINGLE,
            QuestionType.CATEGORICAL_MULTIPLE,
        ]:
            options = question_data.get("options", {}).get("choices", [])
            
            if len(options) < 2:
                warnings.append("Categorical questions need at least 2 options")
            
            if len(options) > 10:
                warnings.append("Too many options may confuse respondents")
                suggestions.append("Consider grouping options or using hierarchical questions")
            
            # Check for overlapping ranges
            if any("to" in opt.lower() or "-" in opt for opt in options):
                suggestions.append("Ensure numeric ranges don't overlap")
        
        # Check for missing validation
        if question_data["question_type"] == QuestionType.NUMERIC:
            validation = question_data.get("validation", {})
            
            if not validation.get("min") and not validation.get("max"):
                warnings.append("Numeric questions should have min/max validation")
                suggestions.append("Set plausible clinical ranges to catch data entry errors")
        
        # Suggest validated instruments
        question_text = question_data.get("question_text", "").lower()
        
        for key, instrument in MethodologicalGuidance.VALIDATED_INSTRUMENTS.items():
            if any(word in question_text for word in instrument["name"].lower().split()):
                suggestions.append(
                    f"Consider using the validated {instrument['name']} instrument for {instrument['description']}"
                )
        
        has_warnings = len(warnings) > 0
        return has_warnings, warnings, suggestions
    
    @staticmethod
    def calculate_questionnaire_quality_score(questions: List[Question]) -> Dict[str, float]:
        """
        Calculate methodological quality scores for a questionnaire.
        
        Returns:
            Dictionary with various quality metrics
        """
        total_questions = len(questions)
        
        if total_questions == 0:
            return {
                "methodological_quality_score": 0.0,
                "analysability_score": 0.0,
            }
        
        # Count structured vs free-text questions
        structured_count = sum(
            1 for q in questions
            if q.question_type not in [QuestionType.TEXT_SHORT, QuestionType.TEXT_LONG]
        )
        
        # Count questions with validation
        validated_count = sum(
            1 for q in questions
            if q.validation and len(q.validation) > 0
        )
        
        # Count questions using validated instruments
        validated_instrument_count = sum(
            1 for q in questions
            if q.validated_instrument
        )
        
        # Count questions with clear variable names
        clear_variable_names = sum(
            1 for q in questions
            if q.variable_name and len(q.variable_name) > 0
        )
        
        # Calculate scores
        structure_score = (structured_count / total_questions) * 100
        validation_score = (validated_count / total_questions) * 100
        instrument_score = (validated_instrument_count / total_questions) * 100
        naming_score = (clear_variable_names / total_questions) * 100
        
        # Overall methodological quality (weighted average)
        methodological_quality = (
            structure_score * 0.4 +
            validation_score * 0.3 +
            instrument_score * 0.2 +
            naming_score * 0.1
        )
        
        # Analysability score (focus on structured data)
        analysability = (
            structure_score * 0.6 +
            validation_score * 0.3 +
            naming_score * 0.1
        )
        
        return {
            "methodological_quality_score": round(methodological_quality, 2),
            "analysability_score": round(analysability, 2),
            "structure_percentage": round(structure_score, 2),
            "validation_percentage": round(validation_score, 2),
            "instrument_percentage": round(instrument_score, 2),
        }
    
    @staticmethod
    def suggest_question_improvements(question: Question) -> List[str]:
        """
        Suggest specific improvements for a question.
        """
        suggestions = []
        
        # Check question text clarity
        if len(question.question_text) < 10:
            suggestions.append("Question text is very short - consider adding more context")
        
        if len(question.question_text) > 200:
            suggestions.append("Question text is very long - consider breaking into multiple questions")
        
        # Check for ambiguous wording
        ambiguous_words = ["sometimes", "usually", "often", "rarely"]
        if any(word in question.question_text.lower() for word in ambiguous_words):
            suggestions.append("Avoid ambiguous frequency words - use specific timeframes instead")
        
        # Check for double-barreled questions
        if " and " in question.question_text.lower():
            suggestions.append("This may be a double-barreled question - consider splitting into separate questions")
        
        # Suggest help text if missing
        if not question.help_text:
            suggestions.append("Add help text to guide data entry")
        
        # Suggest clinical guidance if missing
        if not question.clinical_guidance:
            suggestions.append("Add clinical guidance to explain the question's purpose")
        
        return suggestions
    
    @staticmethod
    def check_questionnaire_completeness(questions: List[Question]) -> Dict[str, Any]:
        """
        Check if questionnaire covers essential audit domains.
        """
        domains_covered = {
            "demographics": False,
            "clinical_presentation": False,
            "intervention": False,
            "outcomes": False,
            "process_metrics": False,
        }
        
        for question in questions:
            text = question.question_text.lower()
            
            if any(word in text for word in ["age", "sex", "gender", "ethnicity"]):
                domains_covered["demographics"] = True
            
            if any(word in text for word in ["diagnosis", "symptom", "presentation"]):
                domains_covered["clinical_presentation"] = True
            
            if any(word in text for word in ["treatment", "surgery", "procedure", "intervention"]):
                domains_covered["intervention"] = True
            
            if any(word in text for word in ["outcome", "complication", "mortality", "readmission"]):
                domains_covered["outcomes"] = True
            
            if any(word in text for word in ["time", "delay", "waiting", "duration"]):
                domains_covered["process_metrics"] = True
        
        completeness_score = sum(domains_covered.values()) / len(domains_covered) * 100
        
        missing_domains = [
            domain for domain, covered in domains_covered.items()
            if not covered
        ]
        
        return {
            "completeness_score": round(completeness_score, 2),
            "domains_covered": domains_covered,
            "missing_domains": missing_domains,
        }


guidance_service = MethodologicalGuidance()
