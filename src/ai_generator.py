from groq import Groq

def generate_notes_for_all_units(api_key: str, rag_engine) -> str:
    """Iterates through all 5 units, querying RAG for each unit and compiling detailed notes."""
    client = Groq(api_key=api_key, timeout=45.0)
    
    units = [
        "Unit 1: Introduction & Core Fundamentals",
        "Unit 2: Architecture & Primary Principles",
        "Unit 3: Functional Blocks & Detailed Design",
        "Unit 4: Memory, Processing & Sub-systems",
        "Unit 5: Advanced Topics, Testing & Applications"
    ]

    all_notes = []

    for unit_idx, unit_title in enumerate(units, start=1):
        # Query context specifically for this unit
        context = rag_engine.query_context(f"{unit_title} concepts components questions", top_k=6)
        safe_context = context[:4000] if context else "Standard Syllabus Topics"

        prompt = f"""
        You are an expert Anna University / Autonomous Engineering Examiner.
        Generate COMPREHENSIVE, DISTINCTION-LEVEL EXAM NOTES for:
        
        {unit_title}
        
        Context Data from uploaded files:
        {safe_context}

        STRICT EXAM FORMAT REQUIREMENTS:

        # {unit_title}

        ## 1. Core Definitions & Important Terms
        - Provide 3 to 4 key definitions with technical terms in bold (`**`).

        ## 2. High-Yield 2-Mark Questions & Answers
        - Question 1 & Question 2 with detailed 3-line answers.

        ## 3. High-Yield 16-Mark Question (COMPREHENSIVE ESSAY TYPE ANSWER)
        Write a complete, long-form, highly detailed 16-mark answer covering:

        ### 16-Mark Question: [Write a major essay topic from this unit]

        #### A. Introduction & Theoretical Principle
        - Provide a multi-paragraph, detailed theoretical explanation of the concept, purpose, and significance.

        #### B. Architecture & Component Block Breakdown
        - Do NOT use ASCII box diagrams with `+---+` symbols.
        - Instead, list each functional block clearly with numbers, describing its inputs, outputs, and internal logic in detail.

        #### C. Step-by-Step Working Mechanism / Derivation / Operation
        - Write a minimum of 6 sequential steps explaining the operation/derivation in depth.

        #### D. Key Technical Features & Comparison Table
        - Provide a markdown table comparing key features or modes.

        #### E. Real-World Engineering Applications & Advantages
        - List 4 practical applications and advantages.

        Make sure the 16-mark answer is extremely thorough, rich in technical terms, and ready for distinction-level grading.
        """

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You write exhaustive, high-yield university exam answers with maximum technical clarity."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=3000
        )

        unit_output = response.choices[0].message.content
        all_notes.append(unit_output)

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
