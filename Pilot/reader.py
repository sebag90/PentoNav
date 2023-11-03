import argparse
import json
from datetime import datetime
from pathlib import Path

import pandas as pd


def read_log_file(filename):
    bot_id = 0
    temp = dict()
    data = list()
    with filename.open(encoding="utf-8") as infile:
        for line in infile:
            linedict = json.loads(line)

            # load new state (a message from the bot to the bot)
            if (linedict["receiver_id"] == linedict["user_id"] and
                    linedict["user_id"] is not None):

                # save last data point
                if temp != dict():
                    temp.pop("t")
                    data.append([i for i in temp.values()])
                temp = dict()

                # extract info from this state
                state = json.loads(linedict["data"]["message"])
                level = state["board_info"]["difficoulty"]
                temp["level"] = level
                temp["t"] = datetime.fromisoformat(linedict["date_created"])
                bot_id = linedict["user_id"]

            # we get a description for the state
            elif (linedict["user_id"] != bot_id and
                    "message" in linedict["data"]):

                # this is not the first message from the user about this state
                # add it to the one already present
                if "description" in temp:
                    temp["description"] += f' {linedict["data"]["message"]}'
                else:
                    temp["description"] = linedict["data"]["message"]

                # calculate time in seconds from when
                # the state was loaded by the bot
                temp["time"] = (
                    datetime.fromisoformat(
                        linedict["date_created"]
                    ) - temp["t"]
                ).seconds

    return data


def main(args):
    data = list()

    for filename in Path(args.path).iterdir():
        if filename.suffix == ".jsonl":
            log_data = read_log_file(filename)
            data.extend(log_data)

    df = pd.DataFrame(data, columns=["level", "description", "time"])

    print("level\ttime(s)\twords")
    for level in ["easy", "medium", "hard"]:
        mean_time = df[df["level"] == level]["time"].mean()
        mean_w = (
            df[df["level"] == level]["description"]
            .str.split()
            .apply(len)
            .mean()
        )
        print(f"{level}\t{round(mean_time, 2)}\t{round(mean_w, 2)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Path to the directory containing the logs")
    args = parser.parse_args()
    main(args)
