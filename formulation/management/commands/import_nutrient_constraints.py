# formulation/management/commands/import_requirements.py

from django.core.management.base import BaseCommand
import pandas as pd
from formulation.models import NutrientRequirement


class Command(BaseCommand):

    help = 'Import nutrient requirements from Excel file'

    # =========================
    # SAFE VALUE FUNCTION
    # =========================
    def val(self, x, default=None):

        if pd.isna(x):
            return default

        try:
            return float(x)

        except:
            return default

    # =========================
    # MAIN FUNCTION
    # =========================
    def handle(self, *args, **kwargs):

        # =========================
        # FILE PATH
        # =========================
        file_path = r"C:\Users\welcome\feed_website\formulation\management\commands\nutrient_constraints.xlsx"

        print("\nUsing file:")
        print(file_path)

        # =========================
        # LOAD EXCEL
        # =========================
        df = pd.read_excel(
            file_path,
            sheet_name="Nutrient_Constraints"
        )

        print("\nRows Loaded:")
        print(df.shape)

        # =========================
        # CLEAN COLUMN NAMES
        # =========================
        df.columns = (
            df.columns
            .str.strip()
            .str.lower()
        )

        print("\nColumns Found:")
        print(df.columns)

        # =========================
        # LOOP THROUGH ROWS
        # =========================
        for _, row in df.iterrows():

            # =========================
            # BASIC FIELDS
            # =========================
            animal_type = str(
                row.get('animal_type')
            ).strip().lower()

            life_stage = str(
                row.get('life_stage')
            ).strip().lower()

            # =========================
            # SKIP INVALID ROWS
            # =========================
            if animal_type in ["", "nan"] \
               or life_stage in ["", "nan"]:

                continue

            # =========================
            # STANDARDIZE VALUES
            # =========================
            ANIMAL_TYPE_MAP = {

                "broiler": "Broiler",

                "layer": "Layer",

                "b breeder": "B Breeder",

                "l breeder": "L Breeder",
            }

            animal_type = ANIMAL_TYPE_MAP.get(
                animal_type,
                animal_type.title()
            )

            life_stage = life_stage.title()

            print(f"\nImporting: {animal_type} - {life_stage}")

            # =========================
            # SAVE TO DATABASE
            # =========================
            NutrientRequirement.objects.update_or_create(

                animal_type=animal_type,

                life_stage=life_stage,

                defaults={

                    # =========================
                    # PROTEIN
                    # =========================
                    'protein_min':
                        self.val(row.get('protein_min')),

                    'protein_max':
                        self.val(row.get('protein_max')),

                    # =========================
                    # ENERGY
                    # =========================
                    'energy_min':
                        self.val(row.get('energy_min')),

                    'energy_max':
                        self.val(row.get('energy_max')),

                    # =========================
                    # ETHER EXTRACT
                    # =========================
                    'ether_extract_min':
                        self.val(row.get('ether_extract_min')),

                    'ether_extract_max':
                        self.val(row.get('ether_extract_max')),

                    # =========================
                    # CRUDE FIBER
                    # =========================
                    'crude_fiber_min':
                        self.val(row.get('crude_fiber_min')),

                    'crude_fiber_max':
                        self.val(row.get('crude_fiber_max')),

                    # =========================
                    # CALCIUM
                    # =========================
                    'calcium_min':
                        self.val(row.get('calcium_min')),

                    'calcium_max':
                        self.val(row.get('calcium_max')),

                    # =========================
                    # PHOSPHORUS
                    # =========================
                    'phosphorus_min':
                        self.val(row.get('phosphorus_min')),

                    'phosphorus_max':
                        self.val(row.get('phosphorus_max')),

                    # =========================
                    # AVAILABLE PHOSPHORUS
                    # =========================
                    'a_phosphorus_min':
                        self.val(row.get('a_phosphorus_min')),

                    'a_phosphorus_max':
                        self.val(row.get('a_phosphorus_max')),

                    # =========================
                    # SALT
                    # =========================
                    'salt_min':
                        self.val(row.get('salt_min')),

                    'salt_max':
                        self.val(row.get('salt_max')),

                    # =========================
                    # SODIUM
                    # =========================
                    'sodium_min':
                        self.val(row.get('sodium_min')),

                    'sodium_max':
                        self.val(row.get('sodium_max')),

                    # =========================
                    # CHLORIDE
                    # =========================
                    'chloride_min':
                        self.val(row.get('chloride_min')),

                    'chloride_max':
                        self.val(row.get('chloride_max')),

                    # =========================
                    # LYSINE
                    # =========================
                    'lysine_min':
                        self.val(row.get('lysine_min')),

                    'lysine_max':
                        self.val(row.get('lysine_max')),

                    # =========================
                    # METHIONINE
                    # =========================
                    'methionine_min':
                        self.val(row.get('methionine_min')),

                    'methionine_max':
                        self.val(row.get('methionine_max')),

                    # =========================
                    # METHIONINE + CYSTINE
                    # =========================
                    'methionine_cystine_min':
                        self.val(
                            row.get(
                                'methionine_cystine_min'
                            )
                        ),

                    'methionine_cystine_max':
                        self.val(
                            row.get(
                                'methionine_cystine_max'
                            )
                        ),

                    # =========================
                    # THREONINE
                    # =========================
                    'threonine_min':
                        self.val(row.get('threonine_min')),

                    'threonine_max':
                        self.val(row.get('threonine_max')),

                    # =========================
                    # ARGININE
                    # =========================
                    'arginine_min':
                        self.val(row.get('arginine_min')),

                    'arginine_max':
                        self.val(row.get('arginine_max')),

                    # =========================
                    # LEUCINE
                    # =========================
                    'leucine_min':
                        self.val(row.get('leucine_min')),

                    'leucine_max':
                        self.val(row.get('leucine_max')),

                    # =========================
                    # TRYPTOPHAN
                    # =========================
                    'tryptophan_min':
                        self.val(row.get('tryptophan_min')),

                    'tryptophan_max':
                        self.val(row.get('tryptophan_max')),

                    # =========================
                    # LINOLEIC
                    # =========================
                    'linoleic_min':
                        self.val(row.get('linoleic_min')),

                    'linoleic_max':
                        self.val(row.get('linoleic_max')),

                }
            )

        # =========================
        # SUCCESS
        # =========================
        self.stdout.write(

            self.style.SUCCESS(
                '\n✅ Nutrient constraints imported successfully!'
            )
        )