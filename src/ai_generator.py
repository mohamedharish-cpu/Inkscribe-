from groq import Groq

def generate_notes_for_all_units(api_key: str, rag_engine) -> str:
    """
    Iterates through all 5 units and generates:
    - 7 to 10 Two-Mark (2M) Questions & Answers
    - 5 to 7 Sixteen-Mark (16M) Questions & Answers with detailed breakdowns
    """
    client = Groq(api_key=api_key, timeout=60.0)
    
    units = [
        "Unit 1: Introduction & Core Fundamentals",
        "Unit 2: Architecture & Primary Principles",
        "Unit 3: Functional Blocks & Detailed Design",
        "Unit 4: Memory, Processing & Sub-systems",
        "Unit 5: Advanced Topics, Testing & Applications"
    ]

    all_notes = []

    for unit_title in units:
        # Retrieve context specific to this unit from RAG Vector Store
        context = rag_engine.query_context(f"{unit_title} key concepts syllabus pyq questions", top_k=8)
        safe_context = context[:5000] if context else "Standard Academic Syllabus Data"

        prompt = f"""
        You are a Chief Senior University Examiner creating an official Question Bank.
        Generate Distinction-Level Exam Notes for: **{unit_title}**

        Context Data from Uploaded Files:
        {safe_context}

        STRICT GENERATION RULES FOR THIS UNIT:

        ================================================================
        # {unit_title}
        ================================================================

        ## PART A: SHORT ANSWER QUESTIONS (Provide EXACTLY 7 TO 10 Questions)
        Generate 7 to 10 high-yield 2-Mark Questions with concise, 3-line technical answers.
        Highlight important technical terms using `**bold**`.

        Format for Part A:
        ### Q1. [2-Mark Question Title]
        **Answer:** [Detailed 2 to 3 line technical explanation]

        ---

        ## PART B: BIG ESSAY QUESTIONS (Provide EXACTLY 5 TO 7 Questions)
        Generate 5 to 7 detailed 16-Mark Questions with complete, multi-section answers.
        
        For EACH of the 16-Mark Questions, you MUST use the following format:

        ### 16-MARK QUESTION [Number]: [Question Title]

        #### 1. Introduction & Theoretical Principle
        Provide a detailed explanation of the core concept, purpose, and working theory.

        #### 2. Block / Architecture Explanation
        Describe all internal blocks, inputs, outputs, and control signals step-by-step using bullet points (Do NOT use raw ASCII box diagrams like +---+).

        #### 3. Step-by-Step Working Mechanism / Derivation
        Provide minimum 5 sequential steps explaining how it executes or derives.

        #### 4. Key Features & Summary
        List key characteristics, timing parameters, or comparison points.

        #### 5. Real-World Applications & Advantages
        List practical engineering applications and main advantages.

        ================================================================
        Ensure all 7-10 (2M) and 5-7 (16M) questions are generated completely without leaving anything out.
        """

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a university senior examiner drafting detailed, high-yield exam question banks with strict counts."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=4000
        )

        all_notes.append(response.choices[0].message.content)

    return "\n\n---\n\n".join(all_notes)


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
