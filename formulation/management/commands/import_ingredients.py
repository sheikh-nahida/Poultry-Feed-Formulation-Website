from pathlib import Path

from django.core.management.base import BaseCommand
import pandas as pd
from formulation.models import Ingredient


class Command(BaseCommand):
    help = "Import ingredients from Excel"

    def safe_float(self, val, default=0):
        try:
            if pd.isna(val) or val == "":
                return default
            return float(val)
        except:
            return default

    def handle(self, *args, **kwargs):

        # Project root directory
        BASE_DIR = Path(__file__).resolve().parents[3]

        # Excel file inside GitHub repository
        file_path = BASE_DIR / "data" / "Ingredients Name.xlsx"

        self.stdout.write(f"Reading: {file_path}")

        if not file_path.exists():
            self.stdout.write(
                self.style.ERROR(f"Excel file not found: {file_path}")
            )
            return

        df = pd.read_excel(file_path)

        # =========================
        # CLEAN COLUMN NAMES
        # =========================
        df.columns = (
            df.columns
            .str.strip()
            .str.lower()
            .str.replace(" ", "_")
            .str.replace("%", "_pct")
            .str.replace("/", "_per_")
            .str.replace(".", "", regex=False)
        )

        print("FOUND COLUMNS:", list(df.columns))

        # =========================
        # DETECT NAME COLUMN
        # =========================
        if "name" in df.columns:
            name_col = "name"
        elif "ingredient" in df.columns:
            name_col = "ingredient"
        elif "poultary_feed_ingredients" in df.columns:
            name_col = "poultary_feed_ingredients"
        elif "poultry_feed_ingredients" in df.columns:
            name_col = "poultry_feed_ingredients"
        else:
            self.stdout.write(
                self.style.ERROR("❌ No ingredient name column found")
        )
        return

        # =========================
        # LOOP THROUGH ROWS
        # =========================
        for _, row in df.iterrows():

            name = str(row[name_col]).strip().upper()

            if not name or name == "NAN":
                continue

            protein = self.safe_float(row.get("protein_pct"))
            energy = self.safe_float(row.get("energy_kcal_per_kg"))

            ether_extract = self.safe_float(row.get("ether_extract_pct"))
            crude_fiber = self.safe_float(row.get("crude_fibre_pct"))

            calcium = self.safe_float(row.get("calcium_pct"))
            phosphorus = self.safe_float(row.get("phosphorus_pct"))
            a_phosphorus = self.safe_float(row.get("a_phosphorus_pct"))

            lysine = self.safe_float(row.get("lysine_pct"))
            methionine = self.safe_float(row.get("methionine_pct"))
            cystine = self.safe_float(row.get("cystine_pct"))

            methionine_cystine = self.safe_float(row.get("methionine_cystine__pct"))

            threonine = self.safe_float(row.get("threonine_pct"))
            arginine = self.safe_float(row.get("arginine_pct"))
            leucine = self.safe_float(row.get("leucine_pct"))
            tryptophan = self.safe_float(row.get("tryptophan_pct"))

            linoleic = self.safe_float(row.get("linoleic_pct"))
            choline = self.safe_float(row.get("choline_pct"))

            sodium = self.safe_float(row.get("sodium_pct"))
            chloride = self.safe_float(row.get("chloride_pct"))
            salt = self.safe_float(row.get("salt_pct"))

            cost = self.safe_float(row.get("cost_per_kg"))

            if cost <= 0:
                print(f"Skipping {name} (invalid cost)")
                continue

            min_inclusion = self.safe_float(row.get("min_inclusion"))
            max_inclusion = self.safe_float(row.get("max_inclusion"))

            if max_inclusion <= 1:
                min_inclusion *= 100
                max_inclusion *= 100

            if min_inclusion > max_inclusion:
                print(f"Invalid inclusion range for {name}")
                continue

            Ingredient.objects.update_or_create(
                name=name,
                defaults={
                    "protein": protein,
                    "energy": energy,
                    "ether_extract": ether_extract,
                    "crude_fiber": crude_fiber,
                    "calcium": calcium,
                    "phosphorus": phosphorus,
                    "a_phosphorus": a_phosphorus,
                    "lysine": lysine,
                    "methionine": methionine,
                    "cystine": cystine,
                    "methionine_cystine": methionine_cystine,
                    "threonine": threonine,
                    "arginine": arginine,
                    "leucine": leucine,
                    "tryptophan": tryptophan,
                    "linoleic": linoleic,
                    "choline": choline,
                    "sodium": sodium,
                    "chloride": chloride,
                    "salt": salt,
                    "cost": cost,
                    "min_inclusion": min_inclusion,
                    "max_inclusion": max_inclusion,
                },
            )

        self.stdout.write(self.style.SUCCESS("✅ Ingredients imported successfully"))
