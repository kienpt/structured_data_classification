python model.py --action=train --confusion_matrix --prop_name=title --index_file=../data_collection/commoncrawl/recipe_data/recipe_index.json --model_file=../data_collection/commoncrawl/recipe_data/model_round1_05/title.model --vect_file=../data_collection/commoncrawl/recipe_data/model_round1_05/title.vect
python model.py --action=train --prop_name=description --index_file=../data_collection/commoncrawl/recipe_data/recipe_index.json --model_file=../data_collection/commoncrawl/recipe_data/model_round1_05/description.model --vect_file=../data_collection/commoncrawl/recipe_data/model_round1_05/description.vect
python model.py --action=train --prop_name=ingredients --index_file=../data_collection/commoncrawl/recipe_data/recipe_index.json --model_file=../data_collection/commoncrawl/recipe_data/model_round1_05/ingredients.model --vect_file=../data_collection/commoncrawl/recipe_data/model_round1_05/ingredients.vect
python model.py --action=train --prop_name=recipeInstructions --index_file=../data_collection/commoncrawl/recipe_data/recipe_index.json --model_file=../data_collection/commoncrawl/recipe_data/model_round1_05/recipeInstructions.model --vect_file=../data_collection/commoncrawl/recipe_data/model_round1_05/recipeInstructions.vect
