from django import forms

DIFFICULTY_CHOICES = [
    ('easy', 'Easy'),
    ('medium', 'Medium'),
    ('hard', 'Hard'),
]

class QuizGeneratorForm(forms.Form):
    topic = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'id': 'id_topic',
            'class': 'form-input',
            'placeholder': 'e.g. World War 2, Cricket, Quantum Physics, Biology, Movies...',
            'autocomplete': 'off',
        }),
        label="Topic"
    )
    difficulty = forms.ChoiceField(
        choices=DIFFICULTY_CHOICES,
        initial='medium',
        required=True,
        widget=forms.Select(attrs={
            'id': 'id_difficulty',
            'class': 'form-select',
        }),
        label="Difficulty"
    )
    num_questions = forms.IntegerField(
        min_value=1,
        max_value=20,
        initial=5,
        required=True,
        widget=forms.NumberInput(attrs={
            'id': 'id_num_questions',
            'class': 'form-input',
            'min': '1',
            'max': '20',
        }),
        label="Number of Questions"
    )
