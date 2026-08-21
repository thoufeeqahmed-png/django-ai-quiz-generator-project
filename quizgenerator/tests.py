from django.test import TestCase
from django.urls import reverse
from .forms import QuizGeneratorForm

class QuizGeneratorTests(TestCase):
    def test_home_page_get(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "AI Quiz Generator")
        self.assertIsInstance(response.context['form'], QuizGeneratorForm)

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
