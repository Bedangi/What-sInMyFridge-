from flask import Flask, render_template, request, session
from model_utils import recommend_recipe_precise, get_recipe_steps
from flask_session import Session

app = Flask(__name__)
app.secret_key = "supersecretkey123"
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False

Session(app)
# Routes
@app.route('/')
def home():
    return render_template('dashboard.html')

@app.route('/ingredients')
def ingredients():
    return render_template('ingredient_input.html')

@app.route('/recommend', methods=['GET', 'POST'])
def recommend():
    if request.method == 'POST':
        user_input = request.form.get('ingredients', '').strip()
        recommendations = recommend_recipe_precise(user_input)
        if recommendations.empty:
            session['last_recipes'] = []
        else:
            recipes = []
            for _, row in recommendations.iterrows():
                recipe_data = {
                    "TranslatedRecipeName": str(row.get("TranslatedRecipeName", "")),
                    "ExtraIngredientsCount": str(row.get("ExtraIngredientsCount", "")),
                    "Cuisine": str(row.get("Cuisine", "")),
                    "Course": str(row.get("Course", "")),
                    "Diet": str(row.get("Diet", ""))
                }
                recipes.append(recipe_data)

            session['last_recipes'] = recipes
        session['last_query'] = user_input
        return render_template('recommend.html', recipes=session['last_recipes'], query=user_input)
    
    recipes = session.get('last_recipes', [])
    query = session.get('last_query', "")
    return render_template('recommend.html', recipes = recipes, query = query)

@app.route('/recipe/<name>')
def recipe_steps(name):
    recipe = get_recipe_steps(name)
    if not recipe:
        return "Recipe not found", 404
    steps = recipe["RecipeSteps"].strip("[]").strip("''").split("', '")
    detailed_steps = [ sentence.strip() for step in steps for sentence in step.split('.') if sentence.strip() ]
    return render_template('dish_detail.html', recipe=recipe, steps=detailed_steps)

if __name__ == '__main__':
    app.run(debug=True)
