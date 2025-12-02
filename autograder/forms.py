# In forms.py

from django import forms
from .models import MarkingTask

class MarkingTaskForm(forms.ModelForm):
    class Meta:
        model = MarkingTask
        fields = ['assign_title', 'files', 'marking_scheme']
