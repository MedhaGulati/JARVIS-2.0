import plac
import spacy
import random
import logging

from pathlib import Path
from src.constants import *
from spacy.util import minibatch, compounding


class Language:

    def __init__(self, model="model/"):
        self.model = model

        try:
            logging.debug("Trying to load model...")
            self.nlp = spacy.load(model)
            logging.info("Model Loaded!")
        except Exception as e:
            logging.exception(e)
            logging.error("No model found, training with data...")
            self.train(output_dir=self.model, n_iter=50)
            self.nlp = spacy.load(model)

    def parse(self, text):

        logging.debug(f"Loading from {self.model}")

        if self.nlp is None:
            self.nlp = spacy.load(self.model)

        doc = self.nlp(text)
        result = {ent.label_: ent.text for ent in doc.ents}

        logging.info("Message parsed successfully!")

        return result

    def train(self, model=None, new_model_name="jarvis", output_dir=None, n_iter=30):

        logging.debug("Training Model...")

        if model is not None:
            nlp = spacy.load(model)
            logging.debug(f"Loaded model from {model}")
        else:
            nlp = spacy.blank("en")
            logging.debug("Created a blank model")

        if "ner" not in nlp.pipe_names:
            ner = nlp.create_pipe("ner")
            nlp.add_pipe(ner)
        else:
            ner = nlp.get_pipe("ner")

        logging.debug("Adding labels...")
        ner.add_label(QUERY)
        ner.add_label(TIME)
        ner.add_label(LOCATION)
        ner.add_label(ENTITY)
        ner.add_label(COURSE)
        ner.add_label(WHO)

        if model is None:
            optimizer = nlp.begin_training()
        else:
            optimizer = nlp.resume_training()

        move_names = list(ner.move_names)

        pipe_exceptions = ["ner", "trf_wordpiecer", "trf_tok2vec"]
        other_pipes = [
            pipe for pipe in nlp.pipe_names if pipe not in pipe_exceptions
        ]
        with nlp.disable_pipes(*other_pipes):
            sizes = compounding(1.0, 4.0, 1.001)
            for itn in range(n_iter):
                random.shuffle(TRAIN_DATA)
                batches = minibatch(TRAIN_DATA, size=sizes)
                losses = {}
                for batch in batches:
                    texts, annotations = zip(*batch)
                    nlp.update(texts, annotations, sgd=optimizer,
                               drop=0.35, losses=losses)
                logging.debug(f"Losses - {losses}")

        if output_dir is not None:
            logging.debug("Saving model to disk...")
            output_dir = Path(output_dir)
            if not output_dir.exists():
                output_dir.mkdir()

            nlp.meta["name"] = new_model_name
            nlp.to_disk(output_dir)
            logging.info(f"Saved model to {output_dir}.")
