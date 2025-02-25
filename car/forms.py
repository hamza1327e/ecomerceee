from django import forms
from .models import Order, Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']

    def __init__(self, *args, **kwargs):
        self.parent_review = kwargs.pop('parent_review', None)
        super(ReviewForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        review = super(ReviewForm, self).save(commit=False)
        review.parent_review = self.parent_review
        if commit:
            review.save()
        return review