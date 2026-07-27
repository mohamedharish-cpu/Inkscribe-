from groq import Groq

def generate_exam_notes_for_unit(api_key: str, unit_name: str, context: str, mode: str) -> str:
    """Generates structured high-yield exam notes with strict 16-mark formatting using Groq."""
    client = Groq(api_key=api_key, timeout=30.0)
    
    safe_context = context[:6000] if context else ""

    prompt = f"""
    You are an expert university professor and exam evaluator.
    Target Mode: {mode}
    Unit/Subject: {unit_name}

    Context Documents:
    {safe_context}

    Task:
    Generate distinction-level exam notes in clean markdown syntax.

    STRICT FORMATTING RULES:
    1. **Core Concepts**: Clear definitions with key technical terms bolded using `**`.
    2. **High-Yield 2-Mark Questions**: Provide concise 2-line answers.
    3. **STRICT 16-MARK QUESTION FORMAT**: For every 16-mark question, format the answer into these mandatory sub-sections:
       - **16-Mark Question**: [Question Title]
       - **1. Introduction & Basic Principle**: (Overview of the concept)
       - **2. Block Diagram / Architecture Representation**: (Textual/ASCII representation of the flow or architecture)
       - **3. Detailed Step-by-Step Methodology / Derivation**: (Comprehensive step-by-step breakdown)
       - **4. Key Features & Working Mechanism**: (Technical deep dive)
       - **5. Applications & Summary Table**: (Practical use cases)

    Do not leave out any section of the 16-mark format.
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You write structured, high-yield university exam answers with proper subheadings and diagrams."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=3000
    )

    return response.choices[0].message.content


def clear_user_doubt(api_key: str, user_question: str, notes_context: str) -> str:
    """Clears user doubts using Groq LLaMA 3.1."""
    client = Groq(api_key=api_key, timeout=20.0)

    prompt = f"""
    Context Notes:
    {notes_context[:3000]}

    User Question:
    {user_question}

    Task:
    Provide a clear, simple, step-by-step explanation for the student's doubt using analogies or structured bullet points if needed.
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a helpful and clear academic AI tutor."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4,
        max_tokens=1500
    )

    return response.choices[0].message.content
