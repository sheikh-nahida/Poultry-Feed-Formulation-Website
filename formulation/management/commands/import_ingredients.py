from pathlib import Path

import pandas as pd
from django.core.management.base import BaseCommand

from formulation.models import Ingredient


class Command(BaseCommand):
    help = "Import ingredients from Excel"

    def safe_float(self, value, default=0):
        try:
            if pd.isna(value) or value == "":
                return default
            return float(value)
        except:
            return default

    def handle(self, *args, **kwargs):

        BASE_DIR = Path(__file__).resolve().parents[3]
        file_path = BASE_DIR / "data" / "Ingredients Name.xlsx"

        self.stdout.write(f"Reading: {file_path}")

        # Read first row as header
        df = pd.read_excel(file_path, header=0)

        # Clean column names
        df.columns = (
            df.columns.astype(str)
            .str.strip()
            .str.upper()
        )

        self.stdout.write(f"\nColumns Found:\n{df.columns.tolist()}")

        imported = 0

        for _, row in df.iterrows():

            # Ingredient name
            name = str(row["INGREDIENT"]).strip().upper()

            if name == "" or name == "NAN":
                continue

            min_inclusion = self.safe_float(row["MIN_INCLUSION"])
            max_inclusion = self.safe_float(row["MAX_INCLUSION"])
            price = self.safe_float(row["COST_PER_KG"])

            if price <= 0:
                print(f"Skipping {name} (Cost <= 0)")
                continue

            Ingredient.objects.update_or_create(
                name=name,
                defaults={
                    "protein": self.safe_float(row["PROTEIN%"]),
                    "energy": self.safe_float(row["ENERGY KCAL/KG"]),

                    "lysine": self.safe_float(row["LYSINE%"]),
                    "methionine": self.safe_float(row["METHIONINE%"]),
                    "cystine": self.safe_float(row["CYSTINE%"]),
                    "methionine_cystine": self.safe_float(row["METHIONINE_CYSTINE %"]),

                    "arginine": self.safe_float(row["ARGININE%"]),
                    "leucine": self.safe_float(row["LEUCINE%"]),
                    "threonine": self.safe_float(row["THREONINE%"]),
                    "tryptophan": self.safe_float(row["TRYPTOPHAN%"]),

                    "ether_extract": self.safe_float(row["ETHER_EXTRACT%"]),
                    "linoleic": self.safe_float(row["LINOLEIC%"]),
                    "crude_fiber": self.safe_float(row["CRUDE_FIBRE%"]),

                    "calcium": self.safe_float(row["CALCIUM%"]),
                    "phosphorus": self.safe_float(row["PHOSPHORUS%"]),
                    "a_phosphorus": self.safe_float(row["A_PHOSPHORUS%"]),

                    "sodium": self.safe_float(row["SODIUM%"]),
                    "chloride": self.safe_float(row["CHLORIDE%"]),
                    "salt": self.safe_float(row["SALT%"]),

                    "choline": self.safe_float(row["CHOLINE%"]),

                    "cost": price,
                    "min_inclusion": min_inclusion,
                    "max_inclusion": max_inclusion,
                },
            )

            imported += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ Successfully imported {imported} ingredients."
            )
        )