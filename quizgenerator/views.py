import json
from django.shortcuts import render
from .forms import QuizGeneratorForm


def generate_dynamic_quiz(topic, difficulty, num_questions):
    """
    Generates dynamic questions for any user-provided topic and difficulty.
    This structure is designed for easy replacement with an LLM/AI API (Gemini, OpenAI, etc.) in the next step.
    """
    templates = [
        {
            "id": 1,
            "type": "multiple_choice",
            "question": f"Which of the following is a fundamental concept or core principle in {topic}?",
            "options": [
                f"Core structural fundamentals and key theories of {topic}",
                f"A concept entirely unrelated to {topic}",
                f"An obsolete and disproven misconception",
                f"An isolated theory with no practical application"
            ],
            "correctAnswer": 0,
            "explanation": f"Understanding the foundational principles of {topic} is essential for mastering this subject."
        },
        {
            "id": 2,
            "type": "true_false",
            "question": f"True or False: Advancements and study in {topic} require systematic methodology and accurate domain knowledge.",
            "options": ["True", "False"],
            "correctAnswer": 0,
            "explanation": f"Systematic analysis and accurate principles are crucial when exploring {topic}."
        },
        {
            "id": 3,
            "type": "multiple_choice",
            "question": f"When evaluating {topic} at a {difficulty.capitalize()} level, what is typically the primary focus of experts?",
            "options": [
                f"Analyzing key variables, methods, and practical impacts in {topic}",
                "Relying on arbitrary assumptions without validation",
                "Ignoring empirical evidence and documented findings",
                "Random trial-and-error with no structured record"
            ],
            "correctAnswer": 0,
            "explanation": f"Evidence-based analysis and evaluating critical variables are standard practices in {topic}."
        },
        {
            "id": 4,
            "type": "multiple_choice",
            "question": f"Which factor contributes most significantly to the importance and study of {topic}?",
            "options": [
                f"Its broad applicability and influence across interconnected areas",
                "Having zero practical relevance in the real world",
                "Remaining strictly isolated from all other domains",
                "A total lack of underlying rules or patterns"
            ],
            "correctAnswer": 0,
            "explanation": f"{topic} holds significant value because of its broader applications and insights."
        },
        {
            "id": 5,
            "type": "true_false",
            "question": f"True or False: Mastery of {topic} is best developed through a combination of conceptual understanding and active problem-solving.",
            "options": ["True", "False"],
            "correctAnswer": 0,
            "explanation": f"Combining strong theory with practical application leads to in-depth comprehension of {topic}."
        },
        {
            "id": 6,
            "type": "multiple_choice",
            "question": f"What is a common challenge encountered when working with complex aspects of {topic}?",
            "options": [
                f"Navigating nuance, managing complexity, and optimizing solutions in {topic}",
                "The complete lack of any variables or rules",
                "Ensuring that no progress is ever documented",
                "Avoiding all analytical thinking and synthesis"
            ],
            "correctAnswer": 0,
            "explanation": f"Managing complexity and optimizing results is a central challenge in {topic}."
        },
        {
            "id": 7,
            "type": "true_false",
            "question": f"True or False: Interdisciplinary perspectives and modern research frequently introduce new breakthroughs in {topic}.",
            "options": ["True", "False"],
            "correctAnswer": 0,
            "explanation": f"Cross-disciplinary insights and ongoing research continually expand our understanding of {topic}."
        },
        {
            "id": 8,
            "type": "multiple_choice",
            "question": f"How do practitioners and analysts in {topic} verify new claims, techniques, or observations?",
            "options": [
                f"Through rigorous verification, empirical testing, and peer review in {topic}",
                "By accepting unverified claims without evidence",
                "By permanently ignoring newly discovered data",
                "Without using any systematic evaluation metrics"
            ],
            "correctAnswer": 0,
            "explanation": f"Rigorous verification and empirical testing ensure reliability and accuracy in {topic}."
        },
        {
            "id": 9,
            "type": "multiple_choice",
            "question": f"Which of the following best describes the structured framework used in {topic}?",
            "options": [
                f"A systematic body of knowledge, terminology, and principles for {topic}",
                "A random, disorganized collection of opinions",
                "An arbitrary list with no logical connections",
                "An unverified set of folklore"
            ],
            "correctAnswer": 0,
            "explanation": f"A structured framework provides the necessary foundation for analyzing and advancing {topic}."
        },
        {
            "id": 10,
            "type": "multiple_choice",
            "question": f"What is an essential goal when mastering {topic} at a {difficulty.capitalize()} level?",
            "options": [
                f"Applying analytical reasoning to solve domain-specific problems in {topic}",
                "Memorizing trivia without understanding context",
                "Avoiding any structured inquiry or problem solving",
                "Restricting knowledge to a single unproven assertion"
            ],
            "correctAnswer": 0,
            "explanation": f"Applying analytical reasoning and contextual understanding demonstrates competency in {topic}."
        }
    ]

    count = min(max(1, num_questions), len(templates))
    return templates[:count]


def home(request):
    quiz_ready = False
    topic = ""
    difficulty = "Medium"
    num_questions = 5
    questions = []
    questions_json = "[]"

    if request.method == 'POST':
        form = QuizGeneratorForm(request.POST)
        if form.is_valid():
            topic = form.cleaned_data['topic'].strip()
            difficulty = form.cleaned_data['difficulty']
            num_questions = form.cleaned_data['num_questions']

            questions = generate_dynamic_quiz(topic, difficulty, num_questions)
            questions_json = json.dumps(questions)
            quiz_ready = True
    else:
        form = QuizGeneratorForm()

    context = {
        'form': form,
        'quiz_ready': quiz_ready,
        'topic': topic,
        'difficulty': difficulty.capitalize(),
        'num_questions': num_questions,
        'questions_json': questions_json,
    }
    return render(request, 'quizgenerator/home.html', context)