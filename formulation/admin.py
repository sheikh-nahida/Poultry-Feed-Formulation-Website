from django.contrib import admin
from .models import Ingredient, NutrientRequirement, FeedFormula, FeedFormulaItem


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'ingredient_id', 'name', 'protein', 'energy', 'cost',
        'min_inclusion', 'max_inclusion'
    )
    list_editable = ('protein', 'energy', 'cost')
    search_fields = ('name', 'ingredient_id')
    readonly_fields = ('ingredient_id',)


@admin.register(NutrientRequirement)
class NutrientRequirementAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Animal Info', {'fields': ('animal_type', 'life_stage')}),
        ('Proximate', {'fields': ('protein_min', 'energy_min', 'ether_extract_min', 'crude_fiber_max')}),
        ('Minerals', {'fields': ('calcium_min', 'phosphorus_min', 'a_phosphorus_min', 'salt_max', 'sodium_min', 'chloride_min')}),
        ('Amino Acids', {'fields': ('lysine_min', 'methionine_min', 'threonine_min', 'arginine_min', 'leucine_min', 'tryptophan_min')}),
        ('Others', {'fields': ('linoleic_min', 'choline_min')}),
    )
    list_display = ('nutrient_id', 'animal_type', 'life_stage')
    list_filter = ('animal_type', 'life_stage')
    readonly_fields = ('nutrient_id',)


@admin.register(FeedFormula)
class FeedFormulaAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'animal_type', 'life_stage', 'total_cost', 'created_at')
    list_filter = ('animal_type', 'life_stage')


@admin.register(FeedFormulaItem)
class FeedFormulaItemAdmin(admin.ModelAdmin):
    list_display = ('formula', 'ingredient', 'inclusion_rate', 'cost')

