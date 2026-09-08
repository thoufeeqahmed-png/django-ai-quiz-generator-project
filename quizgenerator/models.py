from django.db import models


class QuizHistory(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    topic = models.CharField(max_length=200)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='medium')
    score = models.PositiveIntegerField(default=0)
    total_questions = models.PositiveIntegerField(default=5)
    percentage = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Quiz History"
        verbose_name_plural = "Quiz Histories"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.topic} ({self.difficulty.capitalize()}) - {self.score}/{self.total_questions} ({self.percentage:.0f}%)"
