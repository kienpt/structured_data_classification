import pickle
import sys
import traceback

def load_models(model_files, vect_files):
    for f in model_files:
        logger.info("Loading model " + f)
        classifier = pickle.load(open(model_file, "rb"))
        classifiers.append(classifier)

    for f in vect_files:
        logger.info("Loading vectorizer " + f)
        vectorizer = pickle.load(open(vectorizer_file, "rb"))
        vects.append(vectorizer)
    return classifiers, vects

def classify(args):
    
    text = mixutility.clean_str(text)
    vector = vectorizer.decision_function([text])

if __name__=="__main__":
    main(sys.argv[1:])
