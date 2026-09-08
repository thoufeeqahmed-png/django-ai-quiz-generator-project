import json
import os
import random
try:
    import requests
except ImportError:
    requests = None
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .forms import QuizGeneratorForm
from .models import QuizHistory

# Predefined domain knowledge bases for popular topics with rich questions & explanations
TOPIC_KNOWLEDGE_BASE = {
    'python': [
        {
            "question": "Which built-in Python data structure is mutable and maintains insertion order?",
            "correct": "List",
            "distractors": ["Tuple", "Frozenset", "String"],
            "explanation": "Lists in Python are mutable sequences that preserve insertion order. Tuples and Strings are immutable."
        },
        {
            "question": "True or False: In Python, functions are first-class citizens and can be passed as arguments to other functions.",
            "type": "true_false",
            "correct": "True",
            "distractors": ["False"],
            "explanation": "Python treats functions as first-class objects, allowing them to be assigned to variables, stored in data structures, and passed to or returned from other functions."
        },
        {
            "question": "What does the '__init__' method represent in a Python class?",
            "correct": "A constructor method called automatically when an object is instantiated",
            "distractors": [
                "A static method that deletes instance variables",
                "A method to import external libraries",
                "A destructor method executed upon garbage collection"
            ],
            "explanation": "The '__init__' method initializes new object instances with given attributes upon instantiation."
        },
        {
            "question": "Which keyword is used in Python to create a generator function?",
            "correct": "yield",
            "distractors": ["return", "generate", "async"],
            "explanation": "'yield' pauses function execution and produces an item for an iterator without destroying local state."
        },
        {
            "question": "What will 'bool([])' evaluate to in Python?",
            "correct": "False",
            "distractors": ["True", "None", "Raises TypeError"],
            "explanation": "Empty sequences and collections (such as empty lists, tuples, and strings) evaluate to False in a boolean context in Python."
        },
        {
            "question": "What is the primary purpose of the Python GIL (Global Interpreter Lock)?",
            "correct": "To ensure thread-safe memory management in CPython by allowing only one thread to execute Python bytecode at a time",
            "distractors": [
                "To speed up GPU-based tensor calculations",
                "To compile Python script directly to native x86 machine code",
                "To prevent circular imports between modules"
            ],
            "explanation": "The GIL is a mutex used in CPython that protects access to Python objects, preventing multiple threads from executing Python bytecodes at once."
        },
        {
            "question": "Which of the following creates a dictionary comprehension in Python?",
            "correct": "{k: v for k, v in items}",
            "distractors": ["[k: v for k, v in items]", "(k: v for k, v in items)", "{k, v for k, v in items}"],
            "explanation": "Dictionary comprehensions use curly braces with key: value syntax like {k: v for k, v in iterable}."
        },
        {
            "question": "True or False: Python's 'is' operator checks for value equality while '==' checks for identity.",
            "type": "true_false",
            "correct": "False",
            "distractors": ["True"],
            "explanation": "'==' checks for value equality, whereas 'is' checks whether two variables refer to the exact same object in memory (identity)."
        },
        {
            "question": "What is the time complexity of looking up a key in a standard Python dictionary in the average case?",
            "correct": "O(1)",
            "distractors": ["O(n)", "O(log n)", "O(n^2)"],
            "explanation": "Python dictionaries are implemented using hash tables, offering O(1) average time complexity for key lookups."
        },
        {
            "question": "Which built-in module in Python is used for regular expressions?",
            "correct": "re",
            "distractors": ["regex", "pyregex", "match"],
            "explanation": "The 're' module provides regular expression matching operations in Python."
        }
    ],
    'javascript': [
        {
            "question": "Which keyword is used in modern JavaScript to declare a block-scoped, reassignable variable?",
            "correct": "let",
            "distractors": ["var", "const", "static"],
            "explanation": "'let' declares block-scoped variables that can be reassigned. 'const' declares block-scoped read-only identifiers."
        },
        {
            "question": "What is the result of 'typeof null' in JavaScript?",
            "correct": "'object'",
            "distractors": ["'null'", "'undefined'", "'boolean'"],
            "explanation": "'typeof null' returning 'object' is a legacy bug in JavaScript that has been preserved for backward compatibility."
        },
        {
            "question": "True or False: JavaScript is a single-threaded language that handles asynchronous operations using an event loop.",
            "type": "true_false",
            "correct": "True",
            "distractors": ["False"],
            "explanation": "JavaScript has a single call stack and uses the event loop, task queue, and microtask queue to handle non-blocking asynchronous operations."
        },
        {
            "question": "Which method converts a JavaScript object or value into a JSON string?",
            "correct": "JSON.stringify()",
            "distractors": ["JSON.parse()", "JSON.toString()", "JSON.encode()"],
            "explanation": "JSON.stringify() serializes a JavaScript object or array into a standard JSON string."
        },
        {
            "question": "What is the primary difference between '==' and '===' in JavaScript?",
            "correct": "'===' checks both value and type without type coercion, while '==' performs type coercion",
            "distractors": [
                "'==' is strictly faster than '==='",
                "'===' only works on numbers and strings",
                "'==' is used for assignment, '===' is used for comparison"
            ],
            "explanation": "The strict equality operator (===) does not do type conversion before comparing values, unlike loose equality (==)."
        }
    ],
    'cricket': [
        {
            "question": "How many players are on the field for a single cricket team during play?",
            "correct": "11",
            "distractors": ["9", "10", "12"],
            "explanation": "Each cricket team fields 11 players during a standard match."
        },
        {
            "question": "What is the standard length of a cricket pitch between the two sets of wickets?",
            "correct": "22 yards (20.12 meters)",
            "distractors": ["20 yards", "24 yards", "18 yards"],
            "explanation": "According to the Laws of Cricket, the pitch is 22 yards (66 feet / 20.12 m) long between the wickets."
        },
        {
            "question": "True or False: In cricket, a batsman can be given out 'Leg Before Wicket' (LBW) off a no-ball.",
            "type": "true_false",
            "correct": "False",
            "distractors": ["True"],
            "explanation": "A batsman cannot be dismissed LBW, Bowled, Caught, Stumped, or Hit Wicket off a delivery that is called a No-ball."
        },
        {
            "question": "Which country won the inaugural ICC Men's Cricket World Cup in 1975?",
            "correct": "West Indies",
            "distractors": ["Australia", "England", "India"],
            "explanation": "The West Indies won the first-ever Cricket World Cup in 1975 under the captaincy of Clive Lloyd, defeating Australia in the final."
        },
        {
            "question": "What does the cricketing term 'Googly' refer to?",
            "correct": "A deceptive delivery bowled by a right-arm leg spinner that spins into the right-handed batsman",
            "distractors": [
                "A fast bouncer aimed directly at the batsman's helmet",
                "A delivery bowled intentionally without touching the pitch",
                "A slow left-arm orthodox arm ball"
            ],
            "explanation": "A googly (or 'wrong'un') is bowled by a wrist spinner with the wrist turned over, making the ball break the opposite way from standard leg spin."
        },
        {
            "question": "Who holds the record for the highest individual score in Test match cricket (400 not out)?",
            "correct": "Brian Lara",
            "distractors": ["Sachin Tendulkar", "Don Bradman", "Matthew Hayden"],
            "explanation": "Brian Lara scored 400 not out against England at Antigua in 2004, which remains the highest score in Test cricket history."
        },
        {
            "question": "What is the maximum number of overs a bowler can bowl in a standard 50-over One Day International (ODI)?",
            "correct": "10 overs",
            "distractors": ["8 overs", "12 overs", "15 overs"],
            "explanation": "In standard ODIs, no single bowler may bowl more than one-fifth of the total overs, which is 10 overs in a 50-over match."
        }
    ],
    'world war 2': [
        {
            "question": "In which year did World War II officially begin in Europe following the invasion of Poland?",
            "correct": "1939",
            "distractors": ["1938", "1940", "1941"],
            "explanation": "World War II began in Europe on September 1, 1939, when Nazi Germany invaded Poland, prompting Britain and France to declare war."
        },
        {
            "question": "What was the codename for the Allied amphibious landings in Normandy on June 6, 1944 (D-Day)?",
            "correct": "Operation Overlord",
            "distractors": ["Operation Barbarossa", "Operation Torch", "Operation Market Garden"],
            "explanation": "Operation Overlord was the codename for the Battle of Normandy, which launched the successful Allied invasion of German-occupied Western Europe."
        },
        {
            "question": "True or False: The Battle of Midway in 1942 was a decisive naval victory for the United States against Japan.",
            "type": "true_false",
            "correct": "True",
            "distractors": ["False"],
            "explanation": "The Battle of Midway (June 1942) resulted in the sinking of 4 Japanese aircraft carriers and is considered the turning point in the Pacific Theater."
        },
        {
            "question": "Which major battle is widely regarded as the deadliest conflict and pivotal turning point on the Eastern Front?",
            "correct": "Battle of Stalingrad",
            "distractors": ["Battle of the Bulge", "Battle of Kursk", "Battle of Britain"],
            "explanation": "The Battle of Stalingrad (1942–1943) caused over 2 million casualties and marked the destruction of the German Sixth Army, halting German eastward expansion."
        },
        {
            "question": "What was the name of the secret Allied research and development project that created the first nuclear weapons?",
            "correct": "Manhattan Project",
            "distractors": ["Enigma Project", "Apollo Project", "Trinity Initiative"],
            "explanation": "The Manhattan Project, led by J. Robert Oppenheimer and General Leslie Groves, produced the first atomic bombs during WWII."
        },
        {
            "question": "On which Japanese cities were atomic bombs dropped in August 1945?",
            "correct": "Hiroshima and Nagasaki",
            "distractors": ["Tokyo and Kyoto", "Hiroshima and Yokohama", "Osaka and Nagasaki"],
            "explanation": "The United States dropped atomic bombs on Hiroshima (Aug 6, 1945) and Nagasaki (Aug 9, 1945), leading to Japan's surrender and the end of WWII."
        }
    ],
    'quantum physics': [
        {
            "question": "What does Heisenberg's Uncertainty Principle state?",
            "correct": "It is impossible to simultaneously measure both the exact position and momentum of a particle with unlimited precision",
            "distractors": [
                "Energy can neither be created nor destroyed in a quantum system",
                "Light travels faster in a vacuum when measured by an observer",
                "Every subatomic particle must have an equal and opposite charge"
            ],
            "explanation": "Heisenberg's Uncertainty Principle (Δx · Δp >= h/4π) shows a fundamental limit on how precisely position and momentum can be known concurrently."
        },
        {
            "question": "True or False: In quantum mechanics, wave-particle duality applies to both light and matter such as electrons.",
            "type": "true_false",
            "correct": "True",
            "distractors": ["False"],
            "explanation": "Louis de Broglie proposed that all matter exhibits wave-like properties (de Broglie wavelength), confirmed by electron diffraction experiments."
        },
        {
            "question": "Which phenomenon describes two or more quantum particles whose states are inextricably linked regardless of distance?",
            "correct": "Quantum Entanglement",
            "distractors": ["Quantum Tunneling", "Wave Function Collapse", "Quantum Annealing"],
            "explanation": "Quantum Entanglement occurs when particles interact such that the quantum state of each particle cannot be described independently of the others."
        },
        {
            "question": "What physical constant is represented by the symbol 'h' in quantum equations?",
            "correct": "Planck's Constant",
            "distractors": ["Boltzmann's Constant", "Gravitational Constant", "Coulomb's Constant"],
            "explanation": "Planck's constant (h ≈ 6.626 × 10^-34 J·s) relates a photon's energy to its frequency (E = hf)."
        },
        {
            "question": "What allows particles to pass through an energy barrier that they classically could not overcome?",
            "correct": "Quantum Tunneling",
            "distractors": ["Quantum Decoherence", "Superconductivity", "Stimulated Emission"],
            "explanation": "Quantum tunneling is the phenomenon where a subatomic particle passes through a potential energy barrier due to its finite wave function amplitude beyond the barrier."
        }
    ],
    'biology': [
        {
            "question": "What organelle is famously known as the 'powerhouse of the cell' for generating ATP?",
            "correct": "Mitochondria",
            "distractors": ["Ribosome", "Endoplasmic Reticulum", "Golgi Apparatus"],
            "explanation": "Mitochondria generate most of the chemical energy needed to power cellular biochemical reactions through ATP production."
        },
        {
            "question": "What are the four nucleotide nitrogenous bases found in DNA?",
            "correct": "Adenine, Thymine, Cytosine, Guanine",
            "distractors": [
                "Adenine, Uracil, Cytosine, Guanine",
                "Alanine, Threonine, Cysteine, Glycine",
                "Adenine, Thymine, Cytosine, Uracil"
            ],
            "explanation": "DNA contains Adenine (A), Thymine (T), Cytosine (C), and Guanine (G). RNA replaces Thymine with Uracil (U)."
        },
        {
            "question": "True or False: Photosynthesis in plants consumes carbon dioxide and water to produce glucose and oxygen.",
            "type": "true_false",
            "correct": "True",
            "distractors": ["False"],
            "explanation": "The photosynthetic equation is 6CO2 + 6H2O + light -> C6H12O6 + 6O2."
        },
        {
            "question": "Which enzyme is responsible for unwinding the DNA double helix during DNA replication?",
            "correct": "DNA Helicase",
            "distractors": ["DNA Polymerase", "DNA Ligase", "RNA Primase"],
            "explanation": "DNA Helicase breaks the hydrogen bonds between nucleotide base pairs to separate the two strands of DNA for replication."
        },
        {
            "question": "What type of blood cells are primarily responsible for transporting oxygen throughout the human body?",
            "correct": "Erythrocytes (Red Blood Cells)",
            "distractors": ["Leukocytes (White Blood Cells)", "Thrombocytes (Platelets)", "Lymphocytes"],
            "explanation": "Erythrocytes contain hemoglobin, an iron-rich protein that binds oxygen in the lungs and delivers it to body tissues."
        }
    ],
    'movies': [
        {
            "question": "Who directed the 1994 sci-fi/crime classic 'Pulp Fiction'?",
            "correct": "Quentin Tarantino",
            "distractors": ["Martin Scorsese", "Steven Spielberg", "Christopher Nolan"],
            "explanation": "'Pulp Fiction' was written and directed by Quentin Tarantino, winning the Palme d'Or at the 1994 Cannes Film Festival."
        },
        {
            "question": "Which movie was the first to win 11 Academy Awards (Oscars)?",
            "correct": "Ben-Hur (1959)",
            "distractors": ["Titanic (1997)", "The Lord of the Rings: The Return of the King (2003)", "Gone with the Wind (1939)"],
            "explanation": "'Ben-Hur' (1959) was the first film to win 11 Oscars, a record later tied by Titanic and The Return of the King."
        },
        {
            "question": "True or False: 'The Godfather' (1972) was based on the novel written by Mario Puzo.",
            "type": "true_false",
            "correct": "True",
            "distractors": ["False"],
            "explanation": "Francis Ford Coppola's 'The Godfather' is an adaptation of Mario Puzo's bestselling 1969 novel of the same name."
        },
        {
            "question": "Which animated feature was the first full-length computer-animated film in cinema history?",
            "correct": "Toy Story (1995)",
            "distractors": ["Shrek (2001)", "A Bug's Life (1998)", "Finding Nemo (2003)"],
            "explanation": "Pixar's 'Toy Story' (1995) was the first entirely computer-animated feature film, directed by John Lasseter."
        },
        {
            "question": "What is the highest-grossing film of all time worldwide (unadjusted for inflation)?",
            "correct": "Avatar (2009)",
            "distractors": ["Avengers: Endgame (2019)", "Titanic (1997)", "Star Wars: The Force Awakens (2015)"],
            "explanation": "James Cameron's 'Avatar' (2009) holds the record with over $2.9 billion in worldwide box office receipts."
        }
    ],
    'geography': [
        {
            "question": "What is the longest river in the world by total length?",
            "correct": "Nile River",
            "distractors": ["Amazon River", "Yangtze River", "Mississippi River"],
            "explanation": "The Nile River spans approximately 6,650 kilometers (4,132 miles) through northeastern Africa."
        },
        {
            "question": "Which country has the greatest number of natural lakes in the world?",
            "correct": "Canada",
            "distractors": ["Russia", "United States", "Finland"],
            "explanation": "Canada contains over 60% of the world's natural lakes, with an estimated 2 million lakes covering 9% of its land."
        },
        {
            "question": "True or False: Mount Kilimanjaro is the highest peak on the African continent.",
            "type": "true_false",
            "correct": "True",
            "distractors": ["False"],
            "explanation": "Mount Kilimanjaro in Tanzania rises 5,895 meters (19,341 ft) above sea level, making it the highest mountain in Africa."
        },
        {
            "question": "What is the deepest known location on Earth's seabed?",
            "correct": "Challenger Deep (Mariana Trench)",
            "distractors": ["Puerto Rico Trench", "Java Trench", "Tonga Trench"],
            "explanation": "Challenger Deep in the Mariana Trench reaches a depth of approximately 10,994 meters (36,070 ft) below sea level."
        },
        {
            "question": "Which strait connects the Mediterranean Sea to the Atlantic Ocean?",
            "correct": "Strait of Gibraltar",
            "distractors": ["Strait of Hormuz", "Strait of Malacca", "Bosporus Strait"],
            "explanation": "The Strait of Gibraltar separates Spain from Morocco and connects the Mediterranean Sea to the Atlantic Ocean."
        }
    ],
    'machine learning': [
        {
            "question": "What is the primary difference between Supervised and Unsupervised Learning?",
            "correct": "Supervised learning uses labeled training data with target outcomes; Unsupervised learning finds patterns in unlabeled data",
            "distractors": [
                "Supervised learning only works on images; Unsupervised only works on text",
                "Supervised learning requires zero training epochs",
                "Unsupervised learning always produces higher accuracy than supervised learning"
            ],
            "explanation": "Supervised learning algorithms learn from input-output pairs (ground truth labels), whereas unsupervised algorithms uncover hidden clusters without labels."
        },
        {
            "question": "True or False: Overfitting occurs when a model performs exceptionally well on training data but poorly on unseen test data.",
            "type": "true_false",
            "correct": "True",
            "distractors": ["False"],
            "explanation": "Overfitting happens when a model learns noise and specific details of the training set rather than generalizing underlying patterns."
        },
        {
            "question": "Which metric is best suited for evaluating a classification model with highly imbalanced classes?",
            "correct": "F1-Score / PR-AUC",
            "distractors": ["Raw Accuracy", "Mean Squared Error", "R-Squared"],
            "explanation": "Raw Accuracy can be misleading when classes are imbalanced. F1-Score combines Precision and Recall to give a balanced metric."
        },
        {
            "question": "What is the purpose of the activation function in artificial neural networks?",
            "correct": "To introduce non-linearity into the network, enabling it to learn complex patterns",
            "distractors": [
                "To compress the weights into integers",
                "To reset all neuron gradients to zero",
                "To decrease the learning rate after every epoch"
            ],
            "explanation": "Without non-linear activation functions (like ReLU or Sigmoid), a multi-layer neural network would behave just like a single linear regression layer."
        },
        {
            "question": "Which technique is commonly used to prevent overfitting in deep neural networks?",
            "correct": "Dropout regularization and early stopping",
            "distractors": [
                "Increasing the learning rate to 10.0",
                "Removing all validation sets",
                "Duplicating training data identically"
            ],
            "explanation": "Dropout randomly deactivates neurons during training to prevent co-adaptation of features, and early stopping halts training when validation loss stops improving."
        }
    ],
    'cyber security': [
        {
            "question": "What type of attack involves overwhelming a targeted server or network with flood of Internet traffic to disrupt normal operations?",
            "correct": "DDoS (Distributed Denial of Service)",
            "distractors": ["SQL Injection", "Cross-Site Scripting (XSS)", "Man-in-the-Middle (MitM)"],
            "explanation": "A Distributed Denial of Service (DDoS) attack utilizes a network of compromised machines (botnet) to flood a target with excessive traffic."
        },
        {
            "question": "True or False: Asymmetric cryptography uses a public key for encryption and a private key for decryption.",
            "type": "true_false",
            "correct": "True",
            "distractors": ["False"],
            "explanation": "Public-key cryptography uses mathematically linked keypairs where the public key encrypts data and only the matching private key can decrypt it."
        },
        {
            "question": "Which principle states that users should only be granted the minimum necessary permissions required to perform their duties?",
            "correct": "Principle of Least Privilege (PoLP)",
            "distractors": ["Zero Trust Architecture", "Defense in Depth", "Segregation of Duties"],
            "explanation": "The Principle of Least Privilege limits access rights for users and applications to the bare minimum necessary for legitimate tasks."
        }
    ],
    'chemistry': [
        {
            "question": "What is the atomic number of Carbon, which defines its chemical identity?",
            "correct": "6",
            "distractors": ["12", "8", "14"],
            "explanation": "Carbon has 6 protons in its nucleus, giving it an atomic number of 6."
        },
        {
            "question": "True or False: A pH value of less than 7 indicates an acidic solution.",
            "type": "true_false",
            "correct": "True",
            "distractors": ["False"],
            "explanation": "On the pH scale (0-14), values below 7 are acidic, 7 is neutral, and values above 7 are basic (alkaline)."
        },
        {
            "question": "Which type of chemical bond involves the sharing of electron pairs between atoms?",
            "correct": "Covalent Bond",
            "distractors": ["Ionic Bond", "Hydrogen Bond", "Metallic Bond"],
            "explanation": "Covalent bonding involves the mutual sharing of electron pairs between non-metal atoms."
        }
    ]
}


def try_ai_llm_generation(topic: str, difficulty: str, num_questions: int):
    """
    Optional live AI LLM generator.
    Checks for OPENAI_API_KEY or GEMINI_API_KEY in environment variables.
    If available, prompts the LLM for structured JSON; returns None on failure or if unconfigured.
    """
    openai_key = os.getenv('OPENAI_API_KEY', '').strip()
    gemini_key = os.getenv('GEMINI_API_KEY', '').strip()

    prompt = (
        f"Generate a {difficulty} level quiz about '{topic}' with exactly {num_questions} questions. "
        "Return ONLY a valid JSON array of objects with keys: "
        "'question' (string), 'options' (array of 4 strings or 2 for true/false), "
        "'correctAnswer' (integer 0-indexed corresponding to the correct string in options), "
        "'type' ('multiple_choice' or 'true_false'), "
        "'explanation' (concise string explaining the correct answer)."
    )

    if openai_key:
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {openai_key}",
                "Content-Type": "application/json"
            }
            body = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "You are an expert quiz generator. Return only raw JSON arrays."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7
            }
            res = requests.post(url, headers=headers, json=body, timeout=8)
            if res.status_code == 200:
                raw_txt = res.json()['choices'][0]['message']['content'].strip()
                if raw_txt.startswith("```json"):
                    raw_txt = raw_txt[7:]
                if raw_txt.endswith("```"):
                    raw_txt = raw_txt[:-3]
                parsed = json.loads(raw_txt.strip())
                if isinstance(parsed, list) and len(parsed) > 0:
                    for i, q in enumerate(parsed, 1):
                        q['id'] = i
                    return parsed[:num_questions]
        except Exception:
            pass

    if gemini_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
            body = {
                "contents": [{"parts": [{"text": prompt + " Respond ONLY with valid JSON array."}]}]
            }
            res = requests.post(url, json=body, timeout=8)
            if res.status_code == 200:
                content = res.json()['candidates'][0]['content']['parts'][0]['text'].strip()
                if content.startswith("```json"):
                    content = content[7:]
                if content.endswith("```"):
                    content = content[:-3]
                parsed = json.loads(content.strip())
                if isinstance(parsed, list) and len(parsed) > 0:
                    for i, q in enumerate(parsed, 1):
                        q['id'] = i
                    return parsed[:num_questions]
        except Exception:
            pass

    return None


def generate_dynamic_quiz(topic: str, difficulty: str, num_questions: int):
    """
    Generates dynamic questions for any user-provided topic and difficulty.
    1. Tries live LLM if API keys are set.
    2. Uses curated domain knowledge bases if topic matches.
    3. Fills remaining questions with 25+ dynamic multi-format cognitive question templates.
    """
    topic_clean = topic.strip()
    topic_lower = topic_clean.lower()
    difficulty_clean = difficulty.capitalize()

    # Optional Live AI call
    ai_generated = try_ai_llm_generation(topic_clean, difficulty_clean, num_questions)
    if ai_generated:
        return ai_generated

    raw_questions = []

    # 1. Match against curated knowledge bases
    for key, items in TOPIC_KNOWLEDGE_BASE.items():
        if key in topic_lower or topic_lower in key:
            for item in items:
                raw_questions.append({
                    "type": item.get("type", "multiple_choice"),
                    "question": item["question"],
                    "correct": item["correct"],
                    "distractors": item["distractors"],
                    "explanation": item["explanation"]
                })
            break

    # 2. Rich catalog of 25 dynamic templates for ANY topic or difficulty level
    generic_templates = [
        {
            "type": "multiple_choice",
            "question": f"Which of the following represents a foundational principle or core concept in {topic_clean}?",
            "correct": f"Core theoretical fundamentals, structured methodologies, and key mechanics of {topic_clean}",
            "distractors": [
                f"Unsubstantiated assumptions entirely unrelated to {topic_clean}",
                f"An obsolete concept that has been systematically disproven in modern {topic_clean}",
                "A purely speculative notion with zero empirical or practical basis"
            ],
            "explanation": f"Foundational principles and structured methodologies form the essential bedrock of {topic_clean}."
        },
        {
            "type": "true_false",
            "question": f"True or False: Advancing expertise in {topic_clean} at a {difficulty_clean} level requires systematic analysis and evidence-based methods.",
            "correct": "True",
            "distractors": ["False"],
            "explanation": f"Systematic methodology, continuous learning, and accurate domain principles are critical when studying {topic_clean}."
        },
        {
            "type": "multiple_choice",
            "question": f"When evaluating challenges in {topic_clean}, what is considered best practice among practitioners?",
            "correct": f"Analyzing key variables, assessing empirical outcomes, and optimizing solutions systematically in {topic_clean}",
            "distractors": [
                "Relying solely on arbitrary guesses without benchmarking or verification",
                "Ignoring all prior documented findings and industry standards",
                "Treating outcomes as completely random and untestable"
            ],
            "explanation": f"Evidence-based analysis, measuring variables, and iterative optimization are standard best practices in {topic_clean}."
        },
        {
            "type": "multiple_choice",
            "question": f"What is a primary factor that drives ongoing breakthroughs and developments in {topic_clean}?",
            "correct": f"Cross-disciplinary innovation, modern research, and practical real-world applications of {topic_clean}",
            "distractors": [
                f"Maintaining total isolation from all other fields of study",
                "Avoiding documentation and refusing to publish peer-reviewed results",
                "Relying exclusively on outdated 19th-century frameworks"
            ],
            "explanation": f"{topic_clean} evolves rapidly when connected to modern research and real-world implementation."
        },
        {
            "type": "true_false",
            "question": f"True or False: In {topic_clean}, mastering conceptual theory alone without practical problem-solving is sufficient for expert-level competency.",
            "correct": "False",
            "distractors": ["True"],
            "explanation": f"True mastery in {topic_clean} requires balancing deep theoretical foundations with hands-on practical application and critical problem solving."
        },
        {
            "type": "multiple_choice",
            "question": f"How do analysts and practitioners in {topic_clean} verify new claims, techniques, or observations?",
            "correct": f"Through rigorous validation, repeatable testing, and peer review in {topic_clean}",
            "distractors": [
                "By accepting unverified claims without evidence",
                "By permanently ignoring newly discovered data",
                "Without using any structured evaluation metrics"
            ],
            "explanation": f"Rigorous verification and repeatable empirical testing ensure reliability and accuracy in {topic_clean}."
        },
        {
            "type": "multiple_choice",
            "question": f"Which of the following describes the most significant challenge encountered when scaling {topic_clean} systems or methodologies?",
            "correct": f"Managing complexity, ensuring consistency, and optimizing resource efficiency in {topic_clean}",
            "distractors": [
                "The complete lack of any variables or rules",
                "Ensuring that no progress is ever documented",
                "Avoiding all analytical thinking and synthesis"
            ],
            "explanation": f"Managing architectural complexity and maintaining reliable consistency is a universal challenge in {topic_clean}."
        },
        {
            "type": "multiple_choice",
            "question": f"What distinguishes an advanced ({difficulty_clean}) practitioner from a beginner in {topic_clean}?",
            "correct": f"The ability to synthesize nuanced concepts, diagnose edge cases, and design resilient solutions in {topic_clean}",
            "distractors": [
                "Memorizing simple terminology without understanding context",
                "Applying static formulas without understanding trade-offs",
                "Avoiding structured testing and diagnostic metrics"
            ],
            "explanation": f"Advanced practitioners in {topic_clean} understand nuanced trade-offs, diagnostics, and edge-case handling."
        },
        {
            "type": "true_false",
            "question": f"True or False: Quantitative benchmarks and performance metrics play an indispensable role in evaluating success within {topic_clean}.",
            "correct": "True",
            "distractors": ["False"],
            "explanation": f"Metrics and benchmarks provide objective feedback necessary for continuous improvement and quality control in {topic_clean}."
        },
        {
            "type": "multiple_choice",
            "question": f"Which approach is most effective for troubleshooting and debugging failure states in {topic_clean}?",
            "correct": f"Isolating independent variables, analyzing root causes, and applying targeted remediation in {topic_clean}",
            "distractors": [
                "Restarting systems repeatedly without logging diagnostic data",
                "Applying random modifications simultaneously until symptoms disappear",
                "Assuming failure points are inherently unidentifiable"
            ],
            "explanation": f"Systematic root-cause isolation and targeted fixes ensure stable and repeatable resolution in {topic_clean}."
        },
        {
            "type": "multiple_choice",
            "question": f"In the historical evolution of {topic_clean}, which transition marked a pivotal turning point?",
            "correct": f"The shift toward standardized paradigms, precision tools, and data-driven methodologies in {topic_clean}",
            "distractors": [
                "The total abandonment of mathematical and analytical rigor",
                "Restricting knowledge dissemination to private hand-written scrolls",
                "The complete cessation of peer reviews and empirical validations"
            ],
            "explanation": f"Modernization in {topic_clean} has historically followed standardization, precision instrumentation, and data-backed protocols."
        },
        {
            "type": "true_false",
            "question": f"True or False: Ethical considerations, security implications, and reliability are integral aspects of modern {topic_clean} implementations.",
            "correct": "True",
            "distractors": ["False"],
            "explanation": f"Ethical rigor, safety protocols, and resilient design are vital requirements across modern applications of {topic_clean}."
        },
        {
            "type": "multiple_choice",
            "question": f"What role does continuous feedback and iteration play in the lifecycle of {topic_clean} projects?",
            "correct": f"It enables rapid adaptation to changing constraints and minimizes compounding errors in {topic_clean}",
            "distractors": [
                "It guarantees zero need for initial planning or architecture",
                "It serves only as a decorative formality without practical utility",
                "It prevents team members from collaborating effectively"
            ],
            "explanation": f"Iterative feedback cycles allow practitioners to refine models and detect anomalies early in {topic_clean}."
        },
        {
            "type": "multiple_choice",
            "question": f"Which term best captures the trade-off between speed and accuracy when executing workflows in {topic_clean}?",
            "correct": f"Efficiency-Precision Optimization in {topic_clean}",
            "distractors": [
                "Arbitrary Heuristic Neglect",
                "Infinite Redundancy Principle",
                "Unbounded Stochastic Drift"
            ],
            "explanation": f"Balancing speed against precision is an essential optimization problem encountered across {topic_clean}."
        },
        {
            "type": "true_false",
            "question": f"True or False: Documentation, clear architectural design, and knowledge sharing significantly improve long-term outcomes in {topic_clean}.",
            "correct": "True",
            "distractors": ["False"],
            "explanation": f"Clear documentation preserves institutional knowledge and facilitates collaborative scaling in {topic_clean}."
        },
        {
            "type": "multiple_choice",
            "question": f"When comparing different strategies in {topic_clean}, what metric provides the most reliable assessment of efficacy?",
            "correct": f"Reproducible benchmark performance under controlled, representative operating conditions in {topic_clean}",
            "distractors": [
                "Subjective popularity on unverified social forums",
                "The aesthetic appearance of marketing brochures",
                "The speed of single unverified trial runs"
            ],
            "explanation": f"Controlled, reproducible benchmarking is the gold standard for comparing methodologies in {topic_clean}."
        },
        {
            "type": "multiple_choice",
            "question": f"How should high-risk edge cases and anomalies be handled when managing {topic_clean} operations?",
            "correct": f"By implementing defensive safeguards, validation checkpoints, and graceful fallback mechanisms in {topic_clean}",
            "distractors": [
                "By ignoring edge cases until a complete system collapse occurs",
                "By hardcoding static values that mask underlying error flags",
                "By disabling error reporting and monitoring systems"
            ],
            "explanation": f"Defensive design patterns and fallback mechanisms prevent cascading failures in {topic_clean}."
        },
        {
            "type": "true_false",
            "question": f"True or False: Cross-functional collaboration between domain specialists and engineers enhances the real-world impact of {topic_clean}.",
            "correct": "True",
            "distractors": ["False"],
            "explanation": f"Interdisciplinary teamwork bridges theoretical knowledge and engineering execution in {topic_clean}."
        },
        {
            "type": "multiple_choice",
            "question": f"What is the primary risk of adopting unverified tools or shortcuts without due diligence in {topic_clean}?",
            "correct": f"Introducing hidden vulnerabilities, technical debt, and compromised reliability into {topic_clean}",
            "distractors": [
                "Instantly solving all known theoretical questions",
                "Eliminating the need for computing infrastructure",
                "Making the domain obsolete overnight"
            ],
            "explanation": f"Unvetted shortcuts introduce technical debt and unpredictable vulnerabilities in {topic_clean}."
        },
        {
            "type": "multiple_choice",
            "question": f"Which strategy best ensures long-term maintainability and adaptability in {topic_clean}?",
            "correct": f"Modular design, clear decoupling of components, and adhering to established standards in {topic_clean}",
            "distractors": [
                "Building monolithic structures where every component is tightly coupled",
                "Hardcoding business logic directly into UI presentation layers",
                "Refusing to update dependencies or review architecture"
            ],
            "explanation": f"Modularity and clean separation of concerns keep {topic_clean} systems maintainable over time."
        }
    ]

    # Combine knowledge base + templates without duplication
    for item in generic_templates:
        if len(raw_questions) >= max(num_questions, 25):
            break
        raw_questions.append(item)

    # 3. Process, shuffle options, and calculate exact correctAnswer index
    selected_raw = raw_questions[:min(num_questions, len(raw_questions))]
    processed_questions = []

    for i, q in enumerate(selected_raw, 1):
        correct_answer = q["correct"]
        if q.get("type") == "true_false":
            options = ["True", "False"]
            correct_idx = 0 if correct_answer == "True" else 1
        else:
            all_opts = [correct_answer] + list(q["distractors"])
            random.shuffle(all_opts)
            correct_idx = all_opts.index(correct_answer)

        processed_questions.append({
            "id": i,
            "type": q.get("type", "multiple_choice"),
            "question": q["question"],
            "options": all_opts if q.get("type") != "true_false" else options,
            "correctAnswer": correct_idx,
            "explanation": q["explanation"]
        })

    return processed_questions


def home(request):
    """
    Main web view for the AI Quiz Generator.
    Handles form submission and prepares quiz state.
    """
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


@csrf_exempt
def api_generate_quiz(request):
    """
    REST API endpoint for programmatic quiz generation.
    Supports GET & POST with topic, difficulty, and num_questions.
    """
    if request.method == 'POST':
        try:
            body = json.loads(request.body.decode('utf-8'))
            topic = body.get('topic', 'General Knowledge')
            difficulty = body.get('difficulty', 'medium')
            num_questions = int(body.get('num_questions', 5))
        except Exception:
            topic = request.POST.get('topic', 'General Knowledge')
            difficulty = request.POST.get('difficulty', 'medium')
            num_questions = int(request.POST.get('num_questions', 5))
    else:
        topic = request.GET.get('topic', 'General Knowledge')
        difficulty = request.GET.get('difficulty', 'medium')
        num_questions = int(request.GET.get('num_questions', 5))

    num_questions = max(1, min(num_questions, 20))
    questions = generate_dynamic_quiz(topic, difficulty, num_questions)

    return JsonResponse({
        'status': 'success',
        'topic': topic,
        'difficulty': difficulty,
        'count': len(questions),
        'questions': questions
    })


@csrf_exempt
def api_save_history(request):
    """
    REST API endpoint to record completed quiz score into QuizHistory.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            topic = data.get('topic', 'Unknown')
            difficulty = data.get('difficulty', 'medium').lower()
            score = int(data.get('score', 0))
            total_questions = int(data.get('total_questions', 1))
            percentage = round((score / total_questions) * 100, 1) if total_questions > 0 else 0.0

            history = QuizHistory.objects.create(
                topic=topic,
                difficulty=difficulty,
                score=score,
                total_questions=total_questions,
                percentage=percentage
            )
            return JsonResponse({
                'status': 'success',
                'id': history.id,
                'message': 'Quiz result saved successfully'
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Only POST method allowed'}, status=405)