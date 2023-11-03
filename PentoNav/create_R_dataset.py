import argparse

import pandas as pd
import numpy as np


def main(args):
    df = pd.read_csv(args.path, sep="\t")
    df[df == -1] = np.NaN

    # multiply accuracy column to get a percentage
    df["accuracy"] = df["accuracy"].multiply(100)

    # convert level to number
    df = df.replace(
        {
            "easy": 1,
            "medium": 2,
            "hard": 3
        }
    )

    # map design to [0-4]
    mapping = dict(zip(df["design"].unique(), range(len(df["design"].unique()))))
    
    # map file id to a number [0-..]
    mapping2 = dict(zip(df["file id"].unique(), range(len(df["file id"].unique()))))

    # map target piece to a number [0-..]
    mapping3 = dict(zip(df["target"].unique(), range(len(df["target"].unique()))))

    # replace spaces with _
    df.columns = [i.replace(" ", "_") for i in df.columns]

    print(
        df.replace(mapping | mapping2 | mapping3)
            .drop(columns=["board_id"])
            .to_csv(index=False)
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="path to tsv file")
    args = parser.parse_args()

    main(args)
