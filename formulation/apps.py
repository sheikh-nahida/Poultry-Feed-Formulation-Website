from django.apps import AppConfig


class FormulationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "formulation"

    def ready(self):
        from django.core.management import call_command

        try:
            call_command("import_ingredients")
            call_command("import_nutrient_constraints")
        except Exception as e:
            print("Auto import error:", e)