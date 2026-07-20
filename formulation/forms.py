from django import forms
from .models import Ingredient, NutrientRequirement
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = [
            'name',
            'protein',
            'energy',
            'ether_extract',
            'crude_fiber',
            'calcium',
            'phosphorus',
            'a_phosphorus',
            'salt',
            'sodium',
            'chloride',
            'lysine',
            'methionine',
            'threonine',
            'arginine',
            'leucine',
            'tryptophan',
            'linoleic',
            'choline',
            'cost',
            'min_inclusion',
            'max_inclusion',
        ]


class NutrientRequirementForm(forms.ModelForm):
    class Meta:
        model = NutrientRequirement
        fields = "__all__"

    # ✅ MUST be inside class
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            if name.endswith("_min") or name.endswith("_max"):
                field.required = True
class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password1",
            "password2",
        ]