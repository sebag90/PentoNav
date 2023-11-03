import argparse
import json
from pathlib import Path

from data_structures import *


def main(args):
    for filename in Path(args.input).iterdir():
        with filename.open(encoding="utf-8") as infile:
            # variables that are used for each file
            log_info = LogInfo(filename)
            typing_temp = list()
            last_movement = None
            counter = 1

            for line in infile:
                data = json.loads(line)
                event = data["event"]
                user_id = data["user_id"]

                # collect user_ids from join events
                if event == "join":
                    user_id = data["user_id"]
                    if user_id not in log_info.users:
                        log_info.users[user_id] = None

                # new board -> new datapoint
                if event == "board_log":
                    board_id = data["data"]["board"]["state"]["state_id"]
                    timestamp = datetime.fromisoformat(data["date_created"])
                    target = data["data"]["board"]["target"]
                    target_type = data["data"]["board"]["state"]["objs"][str(target)]["type"]
                    level = data["data"]["board"]["board_info"]["difficoulty"]
                    datapoint = DataPoint(
                        board_id=board_id,
                        target=target,
                        target_type=target_type,
                        timestamp=timestamp,
                        version=log_info.version,
                        filename=str(log_info.filename.name),
                        order=counter,
                        level=level,
                    )
                    counter += 1

                # collect the version of this bot
                elif event == "bot_version_log":
                    log_info.version = data["data"]["version"]

                # catch gripper and mouse movements and save the last position
                elif event == "gripper_movement":
                    coordinates = data["data"]["coordinates"]
                    coordinates["type"] = "gripper"
                    last_movement = coordinates

                elif event == "mouse":
                    if log_info.users[user_id] == "wizard":
                        if data["data"]["type"] == "click":
                            coordinates = data["data"]["coordinates"]
                            coordinates["type"] = "mouse"
                            last_movement = coordinates

                # capture which object the wizard selected
                elif event == "wizard_piece_selection":
                    if list(data["data"].keys()) == ["coordinates", "piece"]:
                        # new logs format (coordinates are saved in the event)
                        selected_piece = list(data["data"]["piece"].keys())[0]
                        timestamp = datetime.fromisoformat(data["date_created"])
                        current_description = datapoint.last_description
                        current_description.selection = Selection(
                            selected_piece, timestamp, data["data"]["coordinates"]
                        )

                    else:
                        # old logs format (use coordinates from last_movement)
                        selected_piece = list(data["data"].keys())[0]
                        timestamp = datetime.fromisoformat(data["date_created"])
                        current_description = datapoint.last_description
                        current_description.selection = Selection(
                            selected_piece, timestamp, last_movement
                        )

                elif event == "text_message":
                    # only the bot can send html texts
                    if data["data"]["html"] is True:
                        user_id = data["user_id"]
                        log_info.users[user_id] = "bot"

                    # we get a new description
                    user_id = data["user_id"]
                    if log_info.users[user_id] == "player":
                        description = data["data"]["message"]
                        timestamp = datetime.fromisoformat(data["date_created"])

                        if typing_temp:
                            last_interval = typing_temp[-1]
                            if last_interval.stop is None:
                                last_interval.stop = timestamp

                        # start a new description
                        this_description = Description(
                            description,
                            timestamp,
                            [i for i in typing_temp if i.valid is True],
                        )
                        datapoint.descriptions.append(this_description)

                        # add position of this gripper to the description as a reference
                        # for descriptions like "just above your gripper"
                        if log_info.version == "show_gripper":
                            this_description.gripper_position = last_movement

                        typing_temp = list()

                    if log_info.users[user_id] == "bot":
                        end_turn = {
                            "That was the right piece",
                            "That was the wrong piece",
                            "The experiment is over",
                            "Let's get you to the next board",
                        }
                        if any(
                            data["data"]["message"].startswith(end) for end in end_turn
                        ):
                            # end of turn, save this datapoint
                            if datapoint.aborted is False:
                                print(json.dumps(datapoint.dict, ensure_ascii=False))
                                typing_temp = list()

                elif event == "command":
                    user_id = data["user_id"]
                    if data["data"]["command"] == "role:wizard":
                        for usr, role in log_info.users.items():
                            if role is None:
                                if usr == user_id:
                                    log_info.users[usr] = "wizard"
                                else:
                                    log_info.users[usr] = "player"

                    if isinstance(data["data"]["command"], dict):
                        if data["data"]["command"]["event"] == "abort":
                            datapoint.aborted = True

                        elif data["data"]["command"]["event"] == "confirm_selection":
                            answer = (
                                True
                                if data["data"]["command"]["answer"] == "yes"
                                else False
                            )
                            if datapoint.descriptions:
                                last_selection = datapoint.last_selection
                                if last_selection.confirmed is None:
                                    last_selection.confirmed = answer

                elif event in {"stop_typing", "start_typing"}:
                    user_id = data["data"]["user"]["id"]

                    if log_info.users[user_id] == "player":
                        if event == "start_typing":
                            # start a new interval
                            interval = Interval()
                            interval.start = datetime.fromisoformat(
                                data["date_created"]
                            )
                            typing_temp.append(interval)

                        elif event == "stop_typing":
                            # catch random stop events
                            if typing_temp:
                                last_interval = typing_temp[-1]
                                if last_interval.stop is None:
                                    last_interval.stop = datetime.fromisoformat(
                                        data["date_created"]
                                    )

                elif event == "reset_description":
                    datapoint.remove_last_description()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input", "-i", required=True, help="directory containing the log files"
    )
    args = parser.parse_args()
    main(args)
