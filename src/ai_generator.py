import os
import google.generativeai as genai

def setup_gemini(api_key: str):
    """Initializes Gemini API client."""
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-flash')

# Master System Prompt enforcing all 10 project conditions
SYSTEM_PROMPT = """
You are Inkscribe AI, an elite university exam strategist and AI tutor.
Your task is to generate high-scoring, exam-ready handwritten notes based strictly on provided context.

STRICT COLOR HIGHLIGHTING & STYLING TAGS (For PDF Generator):
1. Color Tags:
   - Use [COLOR:BLUE]Text[/COLOR] for Main Headings, Subheadings, and Sub-bullet titles.
   - Use [COLOR:ORANGE]Text[/COLOR] for Formulas, Key Equations, and Final Numerical Answers.
   - Use [COLOR:BOLD]Text[/COLOR] for crucial Exam Keywords that evaluators scan for.

2. Derivations & Numerical Problems (Slow Learner Friendly):
   - Never skip mathematical steps. Include (Reason / Rule applied) alongside each derivation line.
   - For Numerical Problems, follow strictly:
     a) Given Data & Units
     b) Formula Used (wrapped in [COLOR:ORANGE] tag)
     c) Step-by-Step Substitution
     d) Final Answer with Units

3. Hand-Drawn Style Diagram Placeholders:
   - Where a diagram is needed, output this exact format:
     [HAND-DRAWN DIAGRAM: Title | Labels: Label1, Label2, Label3 | Description: Visual layout flow]

4. Key Formulas Callout Box:
   - At the start of each topic/derivation, include:
     === KEY FORMULAS TO REMEMBER ===

STUDENT MODE RULES:
- Standard Mode (80-85%): Crisp, direct explanations, 5-7 key points per sub-topic.
- Topper Mode (90%+ Distinction): Complete technical depth, edge cases, and exhaustive 9-step coverage.
"""

def generate_exam_notes_for_unit(api_key: str, unit_name: str, context: str, mode: str = "Topper Mode (90%+ Distinction)") -> str:
    """Generates 5-8 16M and 10-12 2M notes for a given unit."""
    model = setup_gemini(api_key)
    
    prompt = f"""
    {SYSTEM_PROMPT}

    TARGET UNIT: {unit_name}
    SELECTED MODE: {mode}

    CONTEXT FROM BOOKS & SYLLABUS:
    {context}

    YOUR MANDATE:
    1. Generate MAXIMUM 5 to 8 High-Frequency 16-Mark Questions.
       Every 16-Mark question MUST strictly follow the 9-Step Evaluation Template:
       Step 1: Title & Clear Definition
       Step 2: Introduction
       Step 3: Working / Basic Principle
       Step 4: Construction & Labeled Diagram Placeholder
       Step 5: Detailed Operation / Working Steps
       Step 6: Advantages & Disadvantages
       Step 7: Limitations
       Step 8: Real-World Applications
       Step 9: Summary / Conclusion

    2. Generate MAXIMUM 10 to 12 Core 2-Mark Questions with precise, high-yield answers.

    Ensure all color tags ([COLOR:BLUE], [COLOR:ORANGE], [COLOR:BOLD]), step-by-step derivations, and formula callouts are strictly included!
    """

    response = model.generate_content(prompt)
    return response.text

def clear_user_doubt(api_key: str, user_question: str, notes_context: str) -> str:
    """Interactive AI Tutor function to clear student doubts on generated notes."""
    model = setup_gemini(api_key)
    
    prompt = f"""
    You are Inkscribe AI's Interactive Tutor. A student is studying these generated notes and has a doubt.
    
    NOTES CONTEXT:
    {notes_context}
    
    STUDENT'S DOUBT / QUESTION:
    "{user_question}"
    
    Explain in a warm, encouraging, slow-learner friendly tone. 
    Use a simple real-world analogy if needed, and break down steps line-by-line for 100% clarity.
    """
    
    response = model.generate_content(prompt)
    return response.text