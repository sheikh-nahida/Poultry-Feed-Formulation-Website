# formulation/genetic_optimizer.py

import random
import numpy as np

from django.db.models import Q

from .models import (
    Ingredient,
    NutrientRequirement,
    FeedFormula,
    FeedFormulaItem
)

# =========================================================
# GENETIC FEED OPTIMIZER
# =========================================================

def genetic_feed_optimizer(

    animal_type,
    life_stage,

    population_size=150,
    generations=200,

    elite_size=5,

    mutation_rate=0.10,

    max_active_ingredients=19,

    penalty_factor=10000
):

    print("\n" + "=" * 60)
    print("SMART GENETIC FEED OPTIMIZER")
    print("=" * 60)

    # =====================================================
    # LOAD REQUIREMENTS
    # =====================================================

    req = NutrientRequirement.objects.filter(
        animal_type__iexact=animal_type,
        life_stage__iexact=life_stage
    ).first()

    if not req:

        return {
            "success": False,
            "error": "Nutrient requirements not found"
        }

    # =====================================================
    # SELECT PRACTICAL INGREDIENTS ONLY
    # =====================================================

    allowed_ingredients = [

        # ENERGY
        "MAIZE",
        "WHEAT",
        "RICE POLISH",
        "D.O.R.B.",
        "MAIZE GLUTEN 2",
        "G.N.C.EXP",
        "FULL FAT SOYA",
        "RAGI",

        # PROTEIN
        "SOYABEAN MEAL",
        "SUNFLOWER MEAL",
        "MUSTARD CAKE",

        # FAT
        "VEG OIL",

        # MINERALS
        "D. C. P.",
        "L. S. P.",
        "O.SHELL GRIT",
        "SALT",

        # AMINO ACIDS
        "LYSINE",
        "METHIONINE",
        "THREONINE"
    ]

    ingredients = []

    for name in allowed_ingredients:

        ing = Ingredient.objects.filter(
            name__iexact=name,
            cost__gt=0
        ).first()

        if ing:
            ingredients.append(ing)

    if not ingredients:

        return {
            "success": False,
            "error": "No valid ingredients found"
        }

    n = len(ingredients)

    print(f"\nIngredients Loaded: {n}")

    # =====================================================
    # NUTRIENTS
    # =====================================================

    nutrient_keys = [

        "protein",
        "energy",
        "crude_fiber",

        "calcium",
        "phosphorus",
        "a_phosphorus",

        "salt",
        "sodium",
        "chloride",

        "lysine",
        "methionine",
        "methionine_cystine",
        "threonine",
    ]

    # =====================================================
    # INGREDIENT LIMITS
    # =====================================================

    ingredient_limits = {

        "MAIZE": 70,
        "WHEAT": 25,

        "RICE POLISH": 15,
        "D.O.R.B.": 15,

        "SOYABEAN MEAL": 35,
        "SUNFLOWER MEAL": 15,
        "MUSTARD CAKE": 12,
        "G.N.C.EXP": 10,
        "MAIZE GLUTEN 2": 8,
        "FULL FAT SOYA": 8,
        "RAGI": 10,

        "VEG OIL": 5,

        "D. C. P.": 6,
        "L. S. P.": 8,
        "O.SHELL GRIT": 10,

        "SALT": 0.5,

        "LYSINE": 0.5,
        "METHIONINE": 0.25,
        "THREONINE": 0.3
    }

    mins = np.zeros(n)
    maxs = np.zeros(n)

    for i, ing in enumerate(ingredients):

        mins[i] = 0

        maxs[i] = ingredient_limits.get(
            ing.name.upper(),
            100
        )

    # =====================================================
    # REPAIR FUNCTION
    # =====================================================

    def repair(ch):

        ch = np.array(ch, dtype=float)

        # Apply limits
        ch = np.clip(ch, mins, maxs)

        # =================================================
        # LIMIT ACTIVE INGREDIENTS
        # =================================================

        sorted_idx = np.argsort(ch)[::-1]

        keep_idx = set(sorted_idx[:max_active_ingredients])

        for i in range(len(ch)):

            if i not in keep_idx:
                ch[i] = 0.0

        # =================================================
        # NORMALIZE
        # =================================================

        total = ch.sum()

        if total <= 0:
            ch = np.random.random(n)

        ch = (ch / ch.sum()) * 100

        # Re-adjust
        for _ in range(10):

            ch = np.clip(ch, mins, maxs)

            diff = 100 - ch.sum()

            if abs(diff) < 0.01:
                break

            free = np.where(ch < maxs)[0]

            if len(free) > 0:
                ch[free] += diff / len(free)

        ch = np.clip(ch, mins, maxs)

        ch = (ch / ch.sum()) * 100

        return ch

    # =====================================================
    # CALCULATE NUTRIENTS
    # =====================================================

    def calculate(ch):

        nutrients = {
            k: 0.0 for k in nutrient_keys
        }

        total_cost = 0.0

        for i, inclusion in enumerate(ch):

            ing = ingredients[i]

            total_cost += (
                inclusion * float(ing.cost)
            ) / 100

            for nut in nutrient_keys:

                val = getattr(
                    ing,
                    nut,
                    0
                ) or 0

                nutrients[nut] += (
                    inclusion * float(val)
                ) / 100

        return nutrients, total_cost

    # =====================================================
    # FITNESS
    # =====================================================

    def fitness(ch):

        TOL = 1e-2

        nutrients, total_cost = calculate(ch)

        feasible = True

        penalty = 0

        violations = []

        for nut in nutrient_keys:

            achieved = nutrients[nut]

            min_req = getattr(
                req,
                f"{nut}_min",
                None
            )

            max_req = getattr(
                req,
                f"{nut}_max",
                None
            )

            # =============================================
            # MINIMUM
            # =============================================

            if min_req is not None and min_req > 0:

                if achieved < (min_req - TOL):

                    feasible = False

                    diff = (
                        min_req - achieved
                    ) / min_req

                    penalty += (
                        diff * penalty_factor
                    )

                    violations.append(
                        f"{nut}: {achieved:.2f} < {min_req}"
                    )

            # =============================================
            # MAXIMUM
            # =============================================

            if max_req is not None and max_req > 0:

                if achieved > (max_req + TOL):

                    feasible = False

                    diff = (
                        achieved - max_req
                    ) / max_req

                    penalty += (
                        diff * penalty_factor
                    )

                    violations.append(
                        f"{nut}: {achieved:.2f} > {max_req}"
                    )

        score = total_cost

        if not feasible:
            score += penalty

        return (
            feasible,
            score,
            nutrients,
            total_cost,
            violations
        )

    # =====================================================
    # CREATE INDIVIDUAL
    # =====================================================

    def create_individual():

        ch = np.zeros(n)

        for i, ing in enumerate(ingredients):

            name = ing.name.upper()

            # ENERGY
            if name == "MAIZE":
                ch[i] = random.uniform(35, 60)

            elif name == "WHEAT":
                ch[i] = random.uniform(0, 15)

            elif name == "RICE POLISH":
                ch[i] = random.uniform(0, 10)

            elif name == "D.O.R.B.":
                ch[i] = random.uniform(0, 8)
            elif name == "G.N.C.EXP":
                ch[i] = random.uniform(0, 8)

            elif name == "MAIZE GLUTEN 2":
                ch[i] = random.uniform(0, 5)

            elif name == "RAGI":
                ch[i] = random.uniform(0, 5)

            elif name == "FULL FAT SOYA":
                ch[i] = random.uniform(0, 5)

            # PROTEIN
            elif name == "SOYABEAN MEAL":
                ch[i] = random.uniform(15, 30)

            elif name == "SUNFLOWER MEAL":
                ch[i] = random.uniform(0, 8)

            elif name == "MUSTARD CAKE":
                ch[i] = random.uniform(0, 5)

            # FAT
            elif name == "VEG OIL":
                ch[i] = random.uniform(0, 4)

            # MINERALS
            elif name in [
                "D. C. P.",
                "L. S. P.",
                "O.SHELL GRIT",
                "SALT"
            ]:
                ch[i] = random.uniform(0.1, 3)

            # AMINO ACIDS
            elif name in [
                "LYSINE",
                "METHIONINE",
                "THREONINE"
            ]:
                ch[i] = random.uniform(0, 0.3)

            else:
                ch[i] = random.uniform(0, 1)

        return repair(ch)

    # =====================================================
    # TOURNAMENT SELECTION
    # =====================================================

    def select_parent(pop):

        candidates = random.sample(
            pop,
            min(5, len(pop))
        )

        candidates.sort(
            key=lambda x: (
                not x["feasible"],
                x["score"]
            )
        )

        return candidates[0]["chromosome"]

    # =====================================================
    # CROSSOVER
    # =====================================================

    def crossover(p1, p2):

        alpha = random.random()

        child = (
            alpha * p1
            +
            (1 - alpha) * p2
        )

        return child

    # =====================================================
    # INITIAL POPULATION
    # =====================================================

    population = [

        create_individual()

        for _ in range(population_size)
    ]

    best_solution = None

    convergence = []

    # =====================================================
    # EVOLUTION LOOP
    # =====================================================

    for gen in range(generations):

        scored = []

        for ch in population:

            feasible, score, nutrients, cost, violations = fitness(ch)

            scored.append({

                "chromosome": ch,

                "feasible": feasible,

                "score": score,

                "nutrients": nutrients,

                "cost": cost,

                "violations": violations
            })

        scored.sort(
            key=lambda x: (
                not x["feasible"],
                x["score"]
            )
        )

        best = scored[0]
        if gen % 10 == 0:
            convergence.append(
                round(best["cost"], 2)
        )

        if (
            best_solution is None
            or
            best["score"] < best_solution["score"]
        ):
            best_solution = best

        # Progress
        if gen % 50 == 0:

            print(
                f"Gen {gen} | "
                f"Cost={best['cost']:.2f} | "
                f"Feasible={best['feasible']} | "
                f"Violations={len(best['violations'])}"
            )

        # =================================================
        # NEXT GENERATION
        # =================================================

        new_population = []

        elites = scored[:elite_size]

        for e in elites:

            new_population.append(
                e["chromosome"].copy()
            )

        while len(new_population) < population_size:

            p1 = select_parent(scored)

            p2 = select_parent(scored)

            child = crossover(p1, p2)

            # MUTATION
            if random.random() < mutation_rate:

                idx = random.randint(0, n - 1)

                child[idx] += random.uniform(-5, 5)

            child = repair(child)

            new_population.append(child)

        population = new_population

    # =====================================================
    # FINAL RESULT
    # =====================================================

    final = best_solution

    ingredient_results = []

    for i, inclusion in enumerate(
        final["chromosome"]
    ):

        if inclusion > 0.1:

            ingredient_results.append({

                "name":
                    ingredients[i].name,

                "inclusion":
                    round(float(inclusion), 2),

                "cost":
                    round(
                        (
                            inclusion
                            *
                            ingredients[i].cost
                        ) / 100,
                        2
                    )
            })

    return {

        "success": True,

        "ingredients":
            ingredient_results,

        "total_cost":
            round(
                float(final["cost"]),
                2
            ),

        "achieved": {

            k: round(float(v), 3)

            for k, v
            in final["nutrients"].items()
        },

        "required_min": {

            k: getattr(
                req,
                f"{k}_min",
                None
            )

            for k in nutrient_keys
        },

        "required_max": {

            k: getattr(
                req,
                f"{k}_max",
                None
            )

            for k in nutrient_keys
        },

        "violations":
            final["violations"],

        "feasible":
            final["feasible"],

        "convergence":
            convergence
    }


# =========================================================
# SAVE FORMULA
# =========================================================

def save_feed_formula(

    user,
    animal_type,
    life_stage,
    result
):

    req = NutrientRequirement.objects.filter(
        animal_type__iexact=animal_type,
        life_stage__iexact=life_stage
    ).first()

    if not req:
        return None

    formula = FeedFormula.objects.create(

        user=user,

        requirement=req,

        animal_type=animal_type,

        life_stage=life_stage,

        total_cost=result["total_cost"]
    )

    for item in result["ingredients"]:

        ing = Ingredient.objects.filter(
            name=item["name"]
        ).first()

        if ing:

            FeedFormulaItem.objects.create(

                formula=formula,

                ingredient=ing,

                inclusion_rate=item["inclusion"],

                cost=item["cost"]
            )

    return formula