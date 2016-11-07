python model.py --action=boost_avg --prop_name=description --classify_outfile=recipe_data/recipe_index_predicted.json --windown_size=15 --model_file=recipe_data/model_round2/desc.model
python model.py --action=boost_avg --prop_name=title --classify_outfile=recipe_data/recipe_index_predicted.json --windown_size=15 --model_file=recipe_data/model_round2/title.model
python model.py --action=boost_avg --prop_name=recipeInstructions --classify_outfile=recipe_data/recipe_index_predicted.json --windown_size=15 --model_file=recipe_data/model_round2/instruction.model
python model.py --action=boost_avg --prop_name=ingredients --classify_outfile=recipe_data/recipe_index_predicted.json --windown_size=15 --model_file=recipe_data/model_round2/ingredient.model
