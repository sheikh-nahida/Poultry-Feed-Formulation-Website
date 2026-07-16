from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Min
from django.http import HttpResponse
from django.core.management import call_command
import traceback

from .models import (
    Ingredient,
    NutrientRequirement,
    FeedFormula,
    FeedFormulaItem
)

from .forms import NutrientRequirementForm

from .genetic_optimizer import (
    genetic_feed_optimizer,
    save_feed_formula
)


# =====================================================
# SAFE FLOAT
# =====================================================
def safe_float(val, default):

    try:
        return float(val)

    except (TypeError, ValueError):
        return default


# =====================================================
# HOME PAGE
# =====================================================
def index(request):

    return render(
        request,
        "formulation/index.html"
    )


# =====================================================
# EDIT INGREDIENTS
# =====================================================
@login_required
def edit_ingredients(request):

    ingredients = Ingredient.objects.all()

    if request.method == "POST":

        for ing in ingredients:

            try:

                fields = [

                    "protein",
                    "energy",
                    "calcium",
                    "phosphorus",
                    "a_phosphorus",

                    "ether_extract",
                    "crude_fiber",

                    "salt",
                    "sodium",
                    "chloride",

                    "lysine",
                    "methionine",
                    "cystine",
                    "methionine_cystine",

                    "threonine",
                    "arginine",
                    "leucine",
                    "tryptophan",

                    "linoleic",
                    "choline",

                    "cost",

                    "min_inclusion",
                    "max_inclusion"
                ]

                for field in fields:

                    setattr(
                        ing,
                        field,

                        safe_float(
                            request.POST.get(
                                f"{field}_{ing.id}"
                            ),
                            getattr(ing, field)
                        )
                    )

                ing.save()

            except Exception as e:

                print("Ingredient Update Error:", e)

        return redirect("edit_ingredients")

    return render(
        request,
        "formulation/edit_ingredients.html",
        {
            "ingredients": ingredients
        }
    )


# =====================================================
# ADD REQUIREMENT
# =====================================================
@login_required
def add_requirement(request):

    form = NutrientRequirementForm(
        request.POST or None
    )

    if form.is_valid():

        form.save()

        return redirect("formulation_home")

    return render(
        request,
        "formulation/add_requirement.html",
        {
            "form": form
        }
    )


# =====================================================
# MAIN FEED OPTIMIZATION VIEW
# =====================================================
@login_required
def optimize_feed(request):

    ingredients = Ingredient.objects.all()

    result = None
    error = None

    convergence = []

    combined_nutrients = {}

    ingredient_chart_data = {}

    # =================================================
    # HANDLE GET + POST
    # =================================================
    if request.method == "POST":

        animal_type = (
            request.POST.get("animal_type") or ""
        ).strip().title()

        life_stage = (
            request.POST.get("life_stage") or ""
        ).strip().title()

    else:

        animal_type = (
            request.GET.get("animal_type") or ""
        ).strip().title()

        life_stage = (
            request.GET.get("life_stage") or ""
        ).strip().title()

    # =================================================
    # DROPDOWNS
    # =================================================
    animal_types = NutrientRequirement.objects.values_list(
        "animal_type",
        flat=True
    ).distinct()

    life_stages = []

    if animal_type:

        life_stages = NutrientRequirement.objects.filter(
            animal_type__iexact=animal_type
        ).values_list(
            "life_stage",
            flat=True
        ).distinct()

    # =================================================
    # RUN OPTIMIZATION
    # =================================================
    if request.method == "POST":

        print("\n====================")
        print("POST RECEIVED")
        print("====================")

        print("Animal Type:", animal_type)
        print("Life Stage :", life_stage)

        # =============================================
        # VALIDATION
        # =============================================
        if not animal_type or not life_stage:

            error = (
                "Please select animal type "
                "and life stage."
            )

        else:

            nutrients = NutrientRequirement.objects.filter(

                animal_type__iexact=animal_type,

                life_stage__iexact=life_stage

            ).first()

            if not nutrients:

                error = (
                    "No nutrient requirement found."
                )

            else:

                try:

                    # =====================================
                    # RUN GA
                    # =====================================
                    result = genetic_feed_optimizer(
                        animal_type,
                        life_stage
                    )

                    print("Feasible:", result["feasible"])
                    print("Violations:", result["violations"])
                    print("\nGA RESULT:")
                    print(result)

                    # =====================================
                    # SUCCESS
                    # =====================================
                    if (
                        result
                        and result.get("success")
                    ):

                        convergence = result.get(
                            "convergence",
                            []
                        )

                        achieved = result.get(
                            "achieved",
                            {}
                        )

                        required_min = result.get(
                            "required_min",
                            {}
                        )

                        required_max = result.get(
                            "required_max",
                            {}
                        )

                        # =================================
                        # NUTRIENT TABLE
                        # =================================

                        TOL = 0.01

                        for nutrient in achieved:

                            min_v = required_min.get(nutrient)
                            max_v = required_max.get(nutrient)
                            val = achieved.get(nutrient)

                            status = True

                            if min_v is not None and val < (min_v - TOL):
                                status = False

                            if max_v is not None and val > (max_v + TOL):
                                status = False
                            
                            combined_nutrients[nutrient] = {

                                "min": min_v,

                                "max": max_v,

                                "achieved": val,

                                "status": status
                            }

                        # =================================
                        # CHART DATA
                        # =================================
                        for item in result["ingredients"]:

                            ingredient_chart_data[
                                item["name"]
                            ] = item["inclusion"]

                        # =================================
                        # SAVE FORMULA
                        # =================================
                        try:

                            save_feed_formula(
                                user=request.user,
                                animal_type=animal_type,
                                life_stage=life_stage,
                                result=result
                            )

                            print(
                                "FORMULA SAVED"
                            )

                        except Exception as e:

                            print(
                                "SAVE ERROR:",
                                e
                            )

                    else:

                        error = (
                            "Optimization failed."
                        )

                except Exception as e:

                    import traceback

                    traceback.print_exc()

                    error = str(e)

    # =================================================
    # HISTORY
    # =================================================
    history = []

    best_cost = None

    history_items = {}

    if animal_type and life_stage:

        history = FeedFormula.objects.filter(

            user=request.user,

            animal_type__iexact=animal_type,

            life_stage__iexact=life_stage

        ).order_by("-created_at")

        best_cost = history.aggregate(
            Min("total_cost")
        )["total_cost__min"]

        for formula in history:

            history_items[
                formula.id
            ] = FeedFormulaItem.objects.filter(
                formula=formula
            )

    # =================================================
    # RENDER PAGE
    # =================================================
    return render(

        request,

        "formulation/optimize-feed.html",

        {

            "ingredients": ingredients,

            "result": result,

            "animal_type": animal_type,

            "life_stage": life_stage,

            "animal_types": animal_types,

            "life_stages": life_stages,

            "error": error,

            "history": history,

            "best_cost": best_cost,

            "history_items": history_items,

            "combined_nutrients": combined_nutrients,

            "convergence": convergence,

            "ingredient_chart_data":
                ingredient_chart_data,
        }
    )
# =====================================================
# FORMULA HISTORY
# =====================================================
@login_required
def formula_history(request):

    formulas = FeedFormula.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(
        request,
        "formulation/history.html",
        {
            "formulas": formulas
        }
    )
# =====================================================
# FORMULA DETAIL
# =====================================================
@login_required
def formula_detail(request, pk):

    formula = FeedFormula.objects.get(
        pk=pk,
        user=request.user
    )

    items = FeedFormulaItem.objects.filter(
        formula=formula
    )

    return render(
        request,
        "formulation/formula_detail.html",
        {
            "formula": formula,
            "items": items
        }
    )
# =====================================================
# TEMPORARY IMPORT DATA
# =====================================================
@login_required
def import_data(request):
    try:
        # Delete old formulas first
        FeedFormulaItem.objects.all().delete()
        FeedFormula.objects.all().delete()

        # Delete old nutrient requirements
        NutrientRequirement.objects.all().delete()

        # Import fresh data
        call_command("import_ingredients")
        call_command("import_nutrient_constraints")

        return HttpResponse("Database updated successfully!")

    except Exception:
        return HttpResponse(
            "<pre>" + traceback.format_exc() + "</pre>",
            content_type="text/html",
        )