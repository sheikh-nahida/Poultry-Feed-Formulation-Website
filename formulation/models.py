from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Max


# =====================================
# INGREDIENT MODEL
# =====================================
class Ingredient(models.Model):
    ingredient_id = models.CharField(max_length=10, unique=True, editable=False)
    name = models.CharField(max_length=100, unique=True)

    # =========================
    # PROXIMATE
    # =========================
    protein = models.FloatField(default=0)
    energy = models.FloatField(default=0)
    ether_extract = models.FloatField(default=0)
    crude_fiber = models.FloatField(default=0)

    # =========================
    # MINERALS
    # =========================
    calcium = models.FloatField(default=0)
    phosphorus = models.FloatField(default=0)
    a_phosphorus = models.FloatField(default=0)
    salt = models.FloatField(default=0)
    sodium = models.FloatField(default=0)
    chloride = models.FloatField(default=0)

    # =========================
    # AMINO ACIDS
    # =========================
    lysine = models.FloatField(default=0)
    methionine = models.FloatField(default=0)
    cystine = models.FloatField(default=0)
    methionine_cystine = models.FloatField(default=0)

    threonine = models.FloatField(default=0)
    arginine = models.FloatField(default=0)
    leucine = models.FloatField(default=0)
    tryptophan = models.FloatField(default=0)

    # =========================
    # OTHERS
    # =========================
    linoleic = models.FloatField(default=0)
    choline = models.FloatField(default=0)

    # =========================
    # ECONOMICS
    # =========================
    cost = models.FloatField(default=0)

    # =========================
    # INCLUSION LIMITS (%)
    # =========================
    min_inclusion = models.FloatField(default=0)
    max_inclusion = models.FloatField(default=100)

    # =========================
    # VALIDATION
    # =========================
    def clean(self):
        if self.min_inclusion < 0 or self.max_inclusion < 0:
            raise ValidationError("Inclusion cannot be negative")

        if self.min_inclusion > self.max_inclusion:
            raise ValidationError("Min inclusion cannot exceed max inclusion")

        if self.cost <= 0:
            raise ValidationError(f"{self.name}: Cost must be > 0")

    # =========================
    # AUTO ID
    # =========================
    def save(self, *args, **kwargs):
        if not self.ingredient_id:
            last = Ingredient.objects.order_by('-id').first()
            next_id = int(last.ingredient_id.replace("ING", "")) + 1 if last else 1
            self.ingredient_id = f"ING{next_id:03d}"

        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# =====================================
# NUTRIENT REQUIREMENTS
# =====================================
class NutrientRequirement(models.Model):
    nutrient_id = models.CharField(max_length=10, unique=True, editable=False)

    animal_type = models.CharField(max_length=50)
    life_stage = models.CharField(max_length=50)

    # =========================
    # PROXIMATE
    # =========================
    protein_min = models.FloatField(null=True, blank=True)
    protein_max = models.FloatField(null=True, blank=True)

    energy_min = models.FloatField(null=True, blank=True)
    energy_max = models.FloatField(null=True, blank=True)

    ether_extract_min = models.FloatField(null=True, blank=True)
    ether_extract_max = models.FloatField(null=True, blank=True)

    crude_fiber_min = models.FloatField(null=True, blank=True)
    crude_fiber_max = models.FloatField(null=True, blank=True)

    # =========================
    # MINERALS
    # =========================
    calcium_min = models.FloatField(null=True, blank=True)
    calcium_max = models.FloatField(null=True, blank=True)

    phosphorus_min = models.FloatField(null=True, blank=True)
    phosphorus_max = models.FloatField(null=True, blank=True)

    a_phosphorus_min = models.FloatField(null=True, blank=True)
    a_phosphorus_max = models.FloatField(null=True, blank=True)

    salt_min = models.FloatField(null=True, blank=True)
    salt_max = models.FloatField(null=True, blank=True)

    sodium_min = models.FloatField(null=True, blank=True)
    sodium_max = models.FloatField(null=True, blank=True)

    chloride_min = models.FloatField(null=True, blank=True)
    chloride_max = models.FloatField(null=True, blank=True)

    # =========================
    # AMINO ACIDS
    # =========================
    lysine_min = models.FloatField(null=True, blank=True)
    lysine_max = models.FloatField(null=True, blank=True)

    methionine_min = models.FloatField(null=True, blank=True)
    methionine_max = models.FloatField(null=True, blank=True)

    methionine_cystine_min = models.FloatField(null=True, blank=True)
    methionine_cystine_max = models.FloatField(null=True, blank=True)

    threonine_min = models.FloatField(null=True, blank=True)
    threonine_max = models.FloatField(null=True, blank=True)

    arginine_min = models.FloatField(null=True, blank=True)
    arginine_max = models.FloatField(null=True, blank=True)

    leucine_min = models.FloatField(null=True, blank=True)
    leucine_max = models.FloatField(null=True, blank=True)

    tryptophan_min = models.FloatField(null=True, blank=True)
    tryptophan_max = models.FloatField(null=True, blank=True)

    # =========================
    # OTHERS
    # =========================
    linoleic_min = models.FloatField(null=True, blank=True)
    linoleic_max = models.FloatField(null=True, blank=True)

    choline_min = models.FloatField(null=True, blank=True)
    choline_max = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ("animal_type", "life_stage")

    def save(self, *args, **kwargs):
        if not self.nutrient_id:
            last = NutrientRequirement.objects.order_by('-id').first()
            next_id = int(last.nutrient_id.replace("NUT", "")) + 1 if last else 1
            self.nutrient_id = f"NUT{next_id:03d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.animal_type} - {self.life_stage}"


# =====================================
# FEED FORMULA
# =====================================
class FeedFormula(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    requirement = models.ForeignKey(
        NutrientRequirement,
        on_delete=models.PROTECT
    )

    animal_type = models.CharField(max_length=50)
    life_stage = models.CharField(max_length=50)

    optimization_id = models.CharField(max_length=50, blank=True, null=True)
    run_number = models.PositiveIntegerField(default=1)

    total_cost = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.total_cost <= 0:
            raise ValidationError("Total cost must be positive")

    def save(self, *args, **kwargs):

        last_run = FeedFormula.objects.filter(
            animal_type=self.animal_type,
            life_stage=self.life_stage
        ).order_by('-run_number').first()

        self.run_number = last_run.run_number + 1 if last_run else 1

        if not self.optimization_id:
            last_id = FeedFormula.objects.aggregate(max_id=Max('id'))['max_id']
            next_id = (last_id or 0) + 1
            self.optimization_id = f"OPT{next_id:05d}"

        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} | {self.animal_type}-{self.life_stage} | Run {self.run_number}"


# =====================================
# FEED FORMULA ITEMS
# =====================================
class FeedFormulaItem(models.Model):
    formula = models.ForeignKey(
        FeedFormula,
        related_name="items",
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)

    inclusion_rate = models.FloatField()
    cost = models.FloatField()

    def clean(self):
        if self.inclusion_rate < 0 or self.inclusion_rate > 100:
            raise ValidationError("Inclusion must be between 0 and 100")

        if self.cost < 0:
            raise ValidationError("Cost cannot be negative")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ingredient.name} ({self.inclusion_rate:.2f}%)"