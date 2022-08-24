import os
import time

from . import config
from typing import List, Optional

class Sample:
    timestamp: float
    value: float = 0.0
    valueType: type = float

    def __init__(self, value: any, timestamp: Optional[float] = None):
        value_type = type(value)
        if not value_type == self.valueType:
            raise ValueError(f"Wrong type '{value_type}' for Sample class '{self.__class__}' with type '{self.valueType}'")
        self.timestamp = timestamp if timestamp else time.time()
        self.value = value

class EventTypes:
    START = "start"
    STOP = "stop"
    CONTACT = "contact"

class EventSample(Sample):
    valueType: type = str
    events = [
        EventTypes.START, EventTypes.STOP, EventTypes.CONTACT
    ]

    def __init__(self, value, timestamp=None):
        super().__init__(value, timestamp)
        if value not in self.events:
            raise ValueError(f"Unrecognized Event: '{value}'. Valid options are {list(self.events)}")


class Timeserries:
    name: str
    sampleClass: type
    values: List[Sample]

    def append(self, value: Sample):
        if not isinstance(value, self.sampleClass):
            raise ValueError(f"Value {value} (type={type(value)} is wrong type for timeseries {self.name} with type {self.sampleClass}")
        value: Sample
        self.values.append(value)

    def __init__(self, name: str, sampleClass: type):
        self.name = name
        self.values = []
        self.sampleClass = sampleClass


class Approach:
    """ Represents an approach for the system
    Should track motor position
    Should track
    """
    TS_EVENT_KEY = "events"
    TS_MOTOR_KEY = "motor"
    TS_ALGO_KEY = "algo"
    TS_TEMP_KEY = "temp"

    contact_detected: bool = False
    running = False

    def __init__(self):
        self.tracked = {
            self.TS_ALGO_KEY: Timeserries(self.TS_ALGO_KEY, Sample),
            self.TS_EVENT_KEY: Timeserries(self.TS_EVENT_KEY, EventSample),
            self.TS_MOTOR_KEY: Timeserries(self.TS_MOTOR_KEY, Sample),
            self.TS_TEMP_KEY: Timeserries(self.TS_TEMP_KEY, Sample)
        }
        self.start()

    def start(self):
        self.running = True
        self.tracked[self.TS_EVENT_KEY].append(EventSample(EventTypes.START))

    def stop(self):
        self.running = False
        self.tracked[self.TS_EVENT_KEY].append(EventSample(EventTypes.STOP))

    def save(self):
        """
        Save the sample to disk
        """
        start_time = None
        events = self.tracked[self.TS_EVENT_KEY].values
        for e in events:
            e: EventSample
            if e.value == EventTypes.START:
                start_time = e.timestamp
        assert start_time
        path = os.path.join(config.APPROACH_DIR, f"approach_{start_time}")
        print(f"Saving approach to {path}")


    def marshall(self):
        ...

    def unmarshall(self):
        ...
