import httpx

from dumpers.file_dumpers import ZIPDumper
from loaders.web_loaders import MIETScheduleLoader
from parsers.parser import MIETScheduleToTimetable

with httpx.Client() as client:
    group = input("Your group: ")
    loader = MIETScheduleLoader(group=group)
    raw_data = loader.load_data()
    parser = MIETScheduleToTimetable()
    parsed_data = parser.parse(raw_data)
    dumper = ZIPDumper()
    dumper.dump(parsed_data, filename="timetable_data")
