from django.contrib import admin
from .models import QuizHistory


@admin.register(QuizHistory)
class QuizHistoryAdmin(admin.ModelAdmin):
    list_display = ('topic', 'difficulty', 'score', 'total_questions', 'percentage', 'created_at')
    list_filter = ('difficulty', 'created_at')
    search_fields = ('topic',)
    ordering = ('-created_at',)
