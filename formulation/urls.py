from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='formulation_home'),

    path('import-data/', views.import_data, name='import_data'),
    path("update-constraints/", views.import_data),
    # ==========================
    # Ingredient management
    # ==========================
    path('add-ingredient/', views.edit_ingredients, name='add_ingredient'),
    path('edit-ingredients/', views.edit_ingredients, name='edit_ingredients'),
    # ==========================
    # Nutrient requirements
    # ==========================
    path('add-requirement/', views.add_requirement, name='add_requirement'),
    # ==========================
    # MAIN FEATURE (GA vs LP)
    # ==========================
    path('optimize-feed/', views.optimize_feed, name='optimize_feed'),
    path('history/', views.formula_history, name='formula_history'),
    # ==========================
    # FORMULA DETAILS
    # ==========================
    path('formula/<int:pk>/', views.formula_detail, name='formula_detail'),
    # ==========================
    # FORMULA
    # ==========================
    path('formula/<int:pk>/', views.formula_detail, name='formula_detail')
]