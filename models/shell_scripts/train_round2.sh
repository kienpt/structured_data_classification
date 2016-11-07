python model.py --action=boost --prop_name=description --classify_outfile=recipe_data/recipe_index_predicted.json --windown_size=15
python model.py --action=boost --prop_name=title --classify_outfile=recipe_data/recipe_index_predicted.json --windown_size=15
python model.py --action=boost --prop_name=recipeInstructions --classify_outfile=recipe_data/recipe_index_predicted.json --windown_size=15
python model.py --action=boost --prop_name=ingredients --classify_outfile=recipe_data/recipe_index_predicted.json --windown_size=15
