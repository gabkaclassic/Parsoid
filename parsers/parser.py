from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, List, Union, Tuple
from random import randint as random


class Parser(ABC):

    @abstractmethod
    def parse(self, data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    def get_field(
        self, data: Dict[str, Any], path: Union[List[str], str], default: Any = None
    ) -> Any:

        if isinstance(path, str):
            path = [path]

        if len(path) == 1:
            return data.get(path[0], default or {})

        return self.get_field(data.get(path[0], {}), path[1:], default)


class MIETScheduleToTimetable(Parser):
    MIET_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
    TIMETABLE_TIME_FORMAT = "%H:%M"

    def convert_time_format(self, time_str):
        dt = datetime.strptime(time_str, self.MIET_TIME_FORMAT)

        new_time_str = dt.strftime(self.TIMETABLE_TIME_FORMAT)
        return new_time_str

    @staticmethod
    def generate_time_slots() -> List[Dict[str, Any]]:
        time_slots = [
            ("09:00", "10:20"),
            ("10:30", "11:50"),
            ("12:00", "13:50"),
            ("14:00", "15:20"),
            ("15:30", "16:50"),
            ("17:00", "18:20"),
            ("18:30", "19:50"),
            ("20:00", "21:20"),
        ]

        result = []
        for i, (start, end) in enumerate(time_slots, start=1):
            slot = {"id": i, "start": start, "end": end}
            result.append(slot)

        return result

    @staticmethod
    def get_lesson_number(time: str) -> int:
        try:
            return int(time[0])
        except ValueError:
            return 0
        except Exception as e:
            print("Parsing lesson error:", e)

    @staticmethod
    def get_color(size: int) -> int:
        COLOR_NUMBER = 20
        return size % COLOR_NUMBER + 1

    @staticmethod
    def get_lesson_title_and_type(input_str: str) -> Tuple[str, str]:
        start_index = input_str.find("[")
        end_index = input_str.find("]")

        if start_index != -1 and end_index != -1:
            value = input_str[start_index + 1 : end_index]
        else:
            return "???", "Другое"

        if value == "Лек":
            mapped_value = "Лекция"
        elif value == "Лаб":
            mapped_value = "Лабораторная работа"
        elif value == "Пр":
            mapped_value = "Семинар"
        else:
            mapped_value = "Другое"

        prefix = input_str[:start_index].strip()

        return prefix, mapped_value

    def parse(self, data: Dict[str, Any]) -> Dict[str, Any]:

        data = self.get_field(data, "Data", [])

        teachers = dict()
        rooms = dict()
        timetables = dict()
        lessons = dict()
        types = dict()
        times = self.generate_time_slots()
        day_weeks = dict()

        for item in data:
            cls = self.get_field(item, "Class")
            lesson, lesson_type = self.get_lesson_title_and_type(
                self.get_field(cls, "Name", "???")
            )
            len_lessons = len(lessons)
            if lesson not in lessons:
                lessons[lesson] = {
                    "id": len_lessons + 1,
                    "color": self.get_color(len_lessons),
                    "name": lesson,
                }
            lesson_id = lessons.get(lesson).get("id")
            teacher = self.get_field(cls, "Teacher", "???")
            if teacher not in teachers:
                teachers[teacher] = {
                    "id": len(teachers) + 1,
                    "name": teacher,
                }
            teacher_id = teachers.get(teacher).get("id")

            if lesson_type not in types:
                types[lesson_type] = {
                    "id": len(types) + 1,
                    "name": lesson_type,
                }
            type_id = types.get(lesson_type).get("id")

            room = self.get_field(item, ["Room", "Name"], "???")
            if room not in rooms:
                rooms[room] = {
                    "id": len(rooms) + 1,
                    "name": room,
                }
            room_id = rooms.get(room).get("id")

            time = times[
                self.get_lesson_number(self.get_field(item, ["Time", "Time"], 1)) - 1
            ]
            time_id = time.get("id")

            timetable = f"{lesson_id}-{teacher_id}-{type_id}-{room_id}-{time_id}"
            if timetable not in timetables:
                timetables[timetable] = {
                    "id": len(timetables) + 1,
                    "lessonId": lesson_id,
                    "roomId": room_id,
                    "teacherId": teacher_id,
                    "timeId": time_id,
                    "typeId": type_id,
                }
            timetable_id = timetables.get(timetable).get("id")
            week = self.get_field(item, "DayNumber")
            day = self.get_field(item, "Day") + 1
            day_week = f"{day}-{week}-{timetable_id}"
            if day_week not in day_weeks:
                day_weeks[day_week] = {
                    "id": len(day_weeks) + 1,
                    "day": day,
                    "week": week,
                    "timetableId": timetable_id,
                }
        result = {
            "dayWeekList": list(day_weeks.values()),
            "lessonList": list(lessons.values()),
            "roomList": list(rooms.values()),
            "teacherList": list(teachers.values()),
            "timeList": times,
            "typeList": list(types.values()),
            "timetableList": list(timetables.values()),
            "attendList": [],
            "dateList": [],
            "examGroupList": [],
            "examList": [],
            "gradeList": [],
            "gradeStatisticList": [],
            "homeworkList": [],
            "imageList": [],
            "noteList": [],
            "weekendList": [],
            "version": 3,
        }

        return result
