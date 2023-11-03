import argparse
from collections import defaultdict
from io import TextIOWrapper
import json
from pathlib import Path
import sys

import enchant
from enchant.checker import SpellChecker
import spacy
import lftk

from data_structures import *

def main(args):
    if args.input is not None:
        input_stream = Path(args.input).open(encoding="utf-8")
    else:
        input_stream = TextIOWrapper(sys.stdin.buffer, encoding='utf-8')

    header = [
        "board id",
        "file id",
        "design",
        "level",
        "batch position",
        "accuracy",
        "target",
        "lag to typing",
        "lag to description",
        "reaction time",
        "n tokens",
        "n adjectives",
        "n adverbs",
        "n nouns"
    ]

    print("\t".join(header))

    chkr = enchant.checker.SpellChecker("en_US")
    nlp = spacy.load("en_core_web_sm")

    for i, line in enumerate(input_stream):
        # print(line, file=sys.stderr)
        data = json.loads(line)
        datapoint = DataPoint.from_dict(data)

        # spell checking
        chkr.set_text(datapoint.all_descriptions)
        for err in chkr:
            sug = err.suggest()[0]
            #print(f"{err.word} -> {sug}")
            err.replace(sug)
        description = chkr.get_text()

        doc = nlp(description)
        LFTK = lftk.Extractor(docs = doc)

        features = LFTK.extract()

        datapoint_line = [
            datapoint.board_id,
            datapoint.filename,
            datapoint.version,
            datapoint.level,
            datapoint.order,
            1 if datapoint.correct else 0,
            datapoint.target_type,
            -1 if datapoint.lag_to_typing is None else datapoint.lag_to_typing,
            datapoint.lag_to_description,
            datapoint.reaction_time,
            features["t_word"],
            features["n_adj"],
            features["n_adv"],
            features["n_noun"]
        ]

        print("\t".join([str(i) for i in datapoint_line]))

        # print progress
        if i % 100 == 0:
            print(i, end="", file=sys.stderr, flush=True)

        elif i % 10 == 0:
            print(".", end="", file=sys.stderr, flush=True)

    input_stream.close()
    print()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input", "-i",
        help="Path to the directory containing the logs"
    )
    args = parser.parse_args()
    main(args)
