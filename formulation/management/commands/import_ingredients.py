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

        # Header is on SECOND row
        df = pd.read_excel(file_path, header=1)

        # Clean column names
        df.columns = (
            df.columns.astype(str)
            .str.strip()
            .str.upper()
        )

        print("\nColumns Found:")
        print(df.columns.tolist())

        imported = 0

        for _, row in df.iterrows():

            name = str(row["NAME"]).strip().upper()

            if name == "" or name == "NAN":
                continue

            inclusion = self.safe_float(row["INCLUSION RATE"])

            price = self.safe_float(row["TOTAL PRICE PER KG"])

            # Skip invalid ingredients
            if price <= 0:
                print(f"Skipping {name} (Price <= 0)")
                continue

            Ingredient.objects.update_or_create(

                name=name,

                defaults={

                    "protein": self.safe_float(row["PROTEIN%"]),
                    "energy": self.safe_float(row["ENERGY KCAL/KG"]),

                    "ether_extract": self.safe_float(row["ETHER.EXTRACT%"]),
                    "crude_fiber": self.safe_float(row["CRUDE.FIBER%"]),

                    "calcium": self.safe_float(row["CALCIUM%"]),
                    "phosphorus": self.safe_float(row["PHOSPHORUS%"]),
                    "a_phosphorus": self.safe_float(row["A.PHOSP.%"]),

                    "lysine": self.safe_float(row["LYSINE%"]),
                    "methionine": self.safe_float(row["METHIONINE%"]),
                    "cystine": self.safe_float(row["CYSTINE%"]),
                    "methionine_cystine": self.safe_float(row["M+C %"]),

                    "threonine": self.safe_float(row["THREONINE%"]),
                    "arginine": self.safe_float(row["ARGININE%"]),
                    "leucine": self.safe_float(row["LEUCINE%"]),
                    "tryptophan": self.safe_float(row["TRYPTOPHAN%"]),

                    "linoleic": self.safe_float(row["LINOLEIC%"]),

                    # Excel doesn't contain choline
                    "choline": 0,

                    "sodium": self.safe_float(row["SODIUM%"]),
                    "chloride": self.safe_float(row["CHLORIDE%"]),
                    "salt": self.safe_float(row["SALT%"]),

                    "cost": price,

                    # Your Excel has only one inclusion value
                    "min_inclusion": 0,
                    "max_inclusion": inclusion,
                }
            )

            imported += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ Successfully imported {imported} ingredients."
            )
        )