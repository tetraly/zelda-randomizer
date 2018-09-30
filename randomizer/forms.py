from django import forms

from .flags import FLAGS
from .models import MODES


class GenerateForm(forms.Form):
  region = forms.Field(required=False)
  seed = forms.Field(required=False)
  mode = forms.ChoiceField(required=True, choices=MODES)
  debug_mode = forms.BooleanField(required=False, initial=False)

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    for flag in FLAGS:
      self.fields[flag[0]] = forms.BooleanField(required=False, initial=False)
