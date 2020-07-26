from typing import List
from _collections import OrderedDict

''':
Trieda uchovava timetable a obsahuje funkcie na pracu s nim. 
'''


class Timetable:
    """ _lessons: zoznam (list) hodin (objekty triedy Lesson)"""
    __lessons: List = None

    """_layout: 2-rozmerny zoznam (list) hodin usporiadanych pre graficke zobrazenie rozvrhu. 
    Jednotlive urovne su: dni->stlpce. Kazdy stlpec je slovnik (OrderedDict) obsahujuci hodiny ulozene podla kluca (casu), 
    kedy zacinaju v rozvrhu."""
    __layout = None

    def __init__(self, lessons_objects):
        self.__set_lessons_list(lessons_objects)
        self.__set_break_times()  # kazdej hodine nastavime breaktime (dlzka prestavky po skonceni lesson):

        self.__init_layout()
        lessons_sorted_by_days = self.__sort_lessons_by_days()  # usporiadame si hodiny podla dni v tyzdni
        self.__set_layout(lessons_sorted_by_days)


    def __set_lessons_list(self, lessons_objects):
        self.__lessons = lessons_objects

    def __init_layout(self):
        """ Inicializuje 2d list, ktoreho prvky su slovniky (dni -> stlpce -> slovnik)."""
        for i in range(5):
            # pouzivam OrderedDict miesto klasickeho dict, kedze chcem lahko pristupovat k poslednemu vlozenemu prvku:
            od = OrderedDict()
            self.__layout.append([od])

    def __sort_lessons_by_days(self):
        """Rozdelime hodiny podla dni v tyzdni. Kazdy den bude predstavovat zoznam hodin."""

        if self.__lessons is None:
            raise Exception("Attribute _lessons cannot be None")

        days: List[List] = []
        for i in range(5):  # 5 dni v tyzdni
            days.append([])
        for lesson in self.__lessons:
            days[lesson['day']].append(lesson)
        return days


    def __set_layout(self, lessons_sorted_by_days):
        """ Nastavi layout rozvrhu: vlozi lessons do _layout, tak, ze ich roztriedi podla dni do stlpcov. Kazdy
        stlpec je OrderedDict. Algoritmus sa vzdy snazi pridavat hodiny do co "najviac laveho" stlpca. """

        # Rozdelime hodiny do stlpcov:
        # pre kazdy den v tyzdni
        for i, lessons in enumerate(lessons_sorted_by_days):
            # pre kazdu hodinu v danom dni:
            for lesson in lessons:
                added = False
                # pre kazdy stlpec v danom dni:
                for column in self.__layout[i]:
                    # ak mozes, skus don dat hodinu
                    if self.__can_add_lesson(lesson, column):
                        column[lesson.start] = lesson  #
                        added = True
                        break
                # ak neslo dat, vytvor novy stlpec a vloz ju don
                if not added:
                    new_dict = {lesson.start: lesson}
                    self.__layout[i].append(new_dict)

    def __can_add_lesson(self, lesson, column: OrderedDict):
        ''' Vrati True, ak sa hodina da vlozit do stlpca (neprebieha momentalne ina hodina v danom stlpci).
        Pre spravnu funkcnost musi byt column zoradeny podla casu.'''

        if len(column) == 0:
            return True
        if self.__get_last_added_lesson(column).end < lesson.start:
            return True
        return False

    def __get_last_added_lesson(self, column):
        """Vrati lesson, ktora bola naposledy pridana do daneho column."""
        last_lesson_key = next(reversed(column))
        return column[last_lesson_key]


    def __set_break_times(self):
        """Prejde vsetky lessons a prida im atribut "breaktime" (dlzka prestavky po skonceni lesson)."""

        # TODO dame to vyssie niekam do configuration?:
        shortest_lesson = 45  # najkratsia hodina ma 45 min
        shortest_breaktime = 5  # najkratsia prestavka je 5 min

        for lesson in self.__lessons:
            hours_count = lesson.end - lesson.start / shortest_lesson
            lesson.breaktime = shortest_breaktime * hours_count


    ########################### "Public" metody: ###########################
    def get_layout(self):
        return self.__layout

    def pop_next_lesson(self, column):
        """Vrati (a zmaze) dalsiu lesson z column v poradi FIFO (najskor tie, ktore boli vlozene ako prve)."""
        return column.popitem(last=False)