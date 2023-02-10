from django import forms

class DocumentForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea)

class SearchForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea)

class QuestionForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea)
