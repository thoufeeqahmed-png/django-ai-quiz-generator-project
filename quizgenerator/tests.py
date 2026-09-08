import json
from django.test import TestCase
from django.urls import reverse
from .forms import QuizGeneratorForm
from .models import QuizHistory
from .views import generate_dynamic_quiz


class QuizGeneratorTests(TestCase):
    def test_home_page_get(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "AI Quiz Generator")
        self.assertIsInstance(response.context['form'], QuizGeneratorForm)
        self.assertFalse(response.context['quiz_ready'])

    def test_dynamic_topic_post_submission(self):
        payload = {
            'topic': 'World War 2',
            'difficulty': 'medium',
            'num_questions': 5,
        }
        response = self.client.post(reverse('home'), data=payload)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['quiz_ready'])
        self.assertEqual(response.context['topic'], 'World War 2')
        self.assertEqual(response.context['difficulty'], 'Medium')
        self.assertContains(response, 'World War 2')

        # Verify parsed questions structure
        questions = json.loads(response.context['questions_json'])
        self.assertEqual(len(questions), 5)
        for q in questions:
            self.assertIn('question', q)
            self.assertIn('options', q)
            self.assertIn('correctAnswer', q)
            self.assertIn('explanation', q)
            self.assertIsInstance(q['correctAnswer'], int)
            self.assertTrue(0 <= q['correctAnswer'] < len(q['options']))

    def test_custom_novel_topic_generation(self):
        payload = {
            'topic': 'Astrophysical Thermodynamics',
            'difficulty': 'hard',
            'num_questions': 10,
        }
        response = self.client.post(reverse('home'), data=payload)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['quiz_ready'])
        questions = json.loads(response.context['questions_json'])
        self.assertEqual(len(questions), 10)

    def test_custom_topic_max_20_questions(self):
        payload = {
            'topic': 'Robotics and Neural Engineering',
            'difficulty': 'hard',
            'num_questions': 20,
        }
        response = self.client.post(reverse('home'), data=payload)
        self.assertEqual(response.status_code, 200)
        questions = json.loads(response.context['questions_json'])
        self.assertEqual(len(questions), 20)

    def test_form_validation_invalid_questions_count(self):
        form = QuizGeneratorForm(data={
            'topic': 'Cricket',
            'difficulty': 'easy',
            'num_questions': 99,  # Max is 20
        })
        self.assertFalse(form.is_valid())
        self.assertIn('num_questions', form.errors)

    def test_generate_dynamic_quiz_function(self):
        questions = generate_dynamic_quiz('Python', 'easy', 3)
        self.assertEqual(len(questions), 3)
        for idx, q in enumerate(questions, 1):
            self.assertEqual(q['id'], idx)
            self.assertTrue(len(q['options']) >= 2)

    def test_api_generate_quiz_get(self):
        response = self.client.get(reverse('api_generate_quiz'), {'topic': 'JavaScript', 'difficulty': 'easy', 'num_questions': 4})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['topic'], 'JavaScript')
        self.assertEqual(data['count'], 4)
        self.assertEqual(len(data['questions']), 4)

    def test_api_generate_quiz_post(self):
        payload = {'topic': 'Quantum Physics', 'difficulty': 'hard', 'num_questions': 5}
        response = self.client.post(
            reverse('api_generate_quiz'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['questions']), 5)

    def test_api_save_history(self):
        payload = {
            'topic': 'Biology',
            'difficulty': 'medium',
            'score': 4,
            'total_questions': 5
        }
        response = self.client.post(
            reverse('api_save_history'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertTrue(QuizHistory.objects.filter(topic='Biology', score=4).exists())

    def test_quiz_history_model(self):
        entry = QuizHistory.objects.create(
            topic='Cyber Security',
            difficulty='hard',
            score=3,
            total_questions=3,
            percentage=100.0
        )
        self.assertIn('Cyber Security', str(entry))
        self.assertIn('100%', str(entry))
