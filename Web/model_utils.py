import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import re

# Load cleaned dataset once
df = pd.read_csv("../recommend_model/cleaned_indian_food_1.csv")
df = df.drop(columns=['TranslatedInstructions', 'TranslatedIngredients'])

df.dropna(subset=["CleanedIngredients"], inplace=True)
df.reset_index(drop=True, inplace=True)

vectorizer = TfidfVectorizer(stop_words="english")
ingredient_vectors = vectorizer.fit_transform(df["CleanedIngredients"])

# Helper functions
def normalize_ingredient_name(text):
    text = text.lower().strip()
    # remove preparation words and descriptors
    text = re.sub(r'\b(chopped|finely|roughly|sliced|diced|grated|minced|crushed|powder|paste|optional|to taste|fresh|whole|small|medium|large|inch)\b', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# Main Recommendation Function
def recommend_recipe_precise(user_ingredients, top_n=10):
    if isinstance(user_ingredients, str):
        user_ingredients = [i.strip().lower() for i in user_ingredients.split(",")]
    else:
        user_ingredients = [i.strip().lower() for i in user_ingredients]

    user_set = set([normalize_ingredient_name(i) for i in user_ingredients])

    results = []
    for idx, row in df.iterrows():
        recipe_ingredients = [normalize_ingredient_name(i) for i in row["CleanedIngredients"].split(",")]
        recipe_set = set(recipe_ingredients)
        intersection = len(user_set & recipe_set)
        if intersection == 0:
            continue
        extra_ings = list(recipe_set - user_set)
        results.append((idx, intersection, len(extra_ings), extra_ings))

    if not results:
        return pd.DataFrame()

    results = sorted(results, key=lambda x: (x[2], -x[1]))
    indices = [r[0] for r in results]
    rec = df.iloc[indices][["TranslatedRecipeName", "CleanedIngredients", "Cuisine", "Course", "Diet", "RecipeSteps"]].copy()
    rec["ExtraIngredientsCount"] = [r[2] for r in results]
    rec["MissingIngredients"] = [", ".join(r[3]) if r[3] else "None" for r in results]
    rec["Rank"] = range(1, len(rec) + 1)
    return rec

# Recipe steps view
def get_recipe_steps(recipe_name):
    recipe = df[df["TranslatedRecipeName"].str.lower() == recipe_name.lower()]
    if recipe.empty:
        return None
    return recipe.iloc[0].to_dict()
