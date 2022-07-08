from django import forms

class StatementForm(forms.Form):
    link = forms.CharField(label='Вставьте ссылки на тикет в JIRA')