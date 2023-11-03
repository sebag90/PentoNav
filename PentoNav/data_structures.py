from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class DataPoint:
    board_id: int
    target: int
    target_type: str
    timestamp: datetime
    version: str
    filename: str
    order: int
    level: str
    aborted: bool = False
    descriptions: list = field(default_factory=list)

    @property
    def correct(self):
        return int(self.target) == int(self.selection.obj)

    @property
    def selection(self):
        for descr in reversed(self.descriptions):
            if descr.selection is not None:
                return descr.selection

    @property
    def all_descriptions(self):
        descriptions = [i.string for i in self.descriptions]
        return ". ".join(descriptions)

    @property
    def lag_to_description(self):
        first_message = self.descriptions[0].timestamp
        delta = first_message - self.timestamp
        return delta.seconds

    @property
    def lag_to_typing(self):
        if self.descriptions[0].typing:
            first_typing = self.descriptions[0].typing[0].start
            delta = first_typing - self.timestamp
            return delta.seconds
        return None

    @property
    def last_description(self):
        return self.descriptions[-1]

    @property
    def reaction_time(self):
        first_message = self.descriptions[0].timestamp
        firse_selection = self.first_selection.timestamp
        return (firse_selection - first_message).seconds

    @property
    def first_selection(self):
        for desc in self.descriptions:
            if desc.selection is not None:
                return desc.selection

    @property
    def last_selection(self):
        for desc in reversed(self.descriptions):
            if desc.selection is not None:
                return desc.selection

    @property
    def dict(self):
        return dict(
            timestamp=self.timestamp.isoformat(),
            target=self.target,
            target_type=self.target_type,
            descriptions=[desc.dict for desc in self.descriptions],
            filename=self.filename,
            version=self.version,
            board_id=self.board_id,
            order=self.order,
            level=self.level
        )

    def remove_last_description(self):
        self.descriptions.pop()

    @classmethod
    def from_dict(cls, data):
        return cls(
            board_id=data["board_id"],
            target=data["target"],
            target_type=data["target_type"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            version=data["version"],
            filename=data["filename"],
            aborted=False,
            descriptions=[Description.from_dict(i) for i in data["descriptions"]],
            order=data["order"],
            level=data["level"]
        )


@dataclass
class Selection:
    obj: int
    timestamp: datetime
    position: dict = field(default_factory=dict)
    confirmed: bool = None

    @property
    def dict(self):
        return dict(
            obj=self.obj,
            timestamp=self.timestamp.isoformat(),
            confirmed=self.confirmed,
            position=self.position
        )

    @classmethod
    def from_dict(cls, data):
        if data is None:
            return None
        return cls(
            obj=data["obj"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            confirmed=data["confirmed"],
            position=data["position"]
        )


@dataclass
class Description:
    string: str
    timestamp: datetime
    typing: list
    selection: Selection = None
    gripper_position: dict = field(default_factory=dict)

    def __post_init__(self):
        self.string = self.string.strip()

    @property
    def empty(self):
        return self.string == "" and self.timestamp is None

    @property
    def dict(self):
        return dict(
            string=self.string,
            timestamp=self.timestamp.isoformat(),
            selection=self.selection.dict if self.selection else None,
            typing=[interval.dict for interval in self.typing],
            gripper_position=self.gripper_position
        )

    @classmethod
    def from_dict(cls, data):
        return cls(
            string=data["string"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            typing=[Interval.from_dict(i) for i in data["typing"]],
            selection=Selection.from_dict(data["selection"]),
            gripper_position=data["gripper_position"]
        )


@dataclass
class LogInfo:
    filename: Path
    version: str = ""
    users: dict = field(default_factory=dict)


@dataclass
class Interval:
    start: datetime = None
    stop: datetime = None

    @property
    def dict(self):
        return dict(start=self.start.isoformat(), stop=self.stop.isoformat())

    @property
    def valid(self):
        return self.start is not None and self.stop is not None

    @classmethod
    def from_dict(cls, data):
        return cls(
            start=datetime.fromisoformat(data["start"]),
            stop=datetime.fromisoformat(data["stop"])
        )

