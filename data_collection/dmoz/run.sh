wget http://rdf.dmoz.org/rdf/content.rdf.u8.gz
gunzip content.rdf.u8.gz
python extract_dmoz_urls.py recipe_topics.txt recipe_urls.txt
python expand_urls.py recipe_urls.txt expanded_recipe_urls.txt
python common/download.py expanded_recipe_urls.txt
python detect_structured_data.py html recipe
