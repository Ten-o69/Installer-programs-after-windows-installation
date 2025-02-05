from pathlib import Path

from common.constants import PARSER_TAGS

BUFFER_HANDLER_PARSER_FUNC = {}

def set_buffer(name: str, value: any) -> None:
    global BUFFER_HANDLER_PARSER_FUNC

    BUFFER_HANDLER_PARSER_FUNC[name] = value

def get_buffer(name: str) -> any:
    global BUFFER_HANDLER_PARSER_FUNC

    return BUFFER_HANDLER_PARSER_FUNC[name]

def clear_buffer():
    global BUFFER_HANDLER_PARSER_FUNC

    BUFFER_HANDLER_PARSER_FUNC = {}


class ListProgramParser:
    def __init__(self, path_to_list_program_file: str | Path):
        if type(path_to_list_program_file) == str:
            path_to_list_program_file = Path(path_to_list_program_file)

        self.path_to_list_program_file: Path = path_to_list_program_file

    def __new__(cls, *args, **kwargs):
        instance: ListProgramParser = super().__new__(cls)
        instance.__init__(*args, **kwargs)

        result: list = instance.__parse()

        return result

    @staticmethod
    def _init_data_dict_for_parser(parser_tags: list[str] = PARSER_TAGS) -> dict[str, list[str]]:
        data = {}

        for parser_tag in parser_tags:
            if not parser_tag.endswith("\\"):
                data[parser_tag] = []

        return data

    def __parse(self):
        """
        Функция для парса списка программ из определённого файла
        :return:
        """

        with open(self.path_to_list_program_file, "r", encoding="utf-8") as list_program_file:
            list_program_file_lines = list_program_file.readlines()

            data = self._init_data_dict_for_parser()
            tag_parse = False
            tag: str | None = None
            tag_line_num: int = 0

            set_buffer("parser_func_for_urls_tag", {})

            for num, line in enumerate(list_program_file_lines):
                line = line.strip("\n")

                if line in PARSER_TAGS and tag_parse is False and tag is None:
                    tag_parse = True
                    tag_line_num = num + 1
                    tag = line
                    print(tag, tag_line_num)

                    continue

                elif line in PARSER_TAGS and not line.endswith("\\") and tag_parse is True and tag is not None:
                    print(line)
                    raise

                elif line in PARSER_TAGS and line.endswith("\\") and tag == line.split("\\")[0] and \
                        tag_parse is True and tag is not None:
                    tag_parse = False
                    tag_line_num = 0
                    tag = None
                    print(tag, tag_line_num)

                elif line in PARSER_TAGS and line.endswith("\\") and tag != line.split("\\")[0] and \
                        tag_parse is True and tag is not None:
                    print(line)
                    raise

                elif line not in PARSER_TAGS and tag_parse is True and tag is not None:
                    data = self.__handler_parser_func(line, tag, data)
                    print(data)

            clear_buffer()

            return self.__compiling_parser_data_into_list(parser_data=data)

    def __handler_parser_func(self, line: str, tag: str, data: dict[str, list[str]]) -> dict[str, list[str]]:
        """
        Функция обработчик для функций использующейся для парсенга данных внутри парсера.
        :param line: Текущая линия на которой остановился парсер.
        :param tag: Текущий тег на который обрабатывает парсер.
        :param data:
        :return:
        """
        if tag == "priority-da":
            parse_result = self._parser_func_for_priority_da_tag(line)

        elif tag == "urls":
            parse_result = self._parser_func_for_urls_tag(line)

        else:
            parse_result = []

        if tag:
            data[tag] = parse_result
            return data

        else:
            return data

    @staticmethod
    def __compiling_parser_data_into_list(parser_data: dict[str, list[str] | dict[str, str]]) -> list[str]:
        priority_list = parser_data["priority-da"]
        links_to_download_programs: dict = parser_data["urls"]
        list_links_to_download_programs_output = []

        for name_program in priority_list:
            list_links_to_download_programs_output.append(links_to_download_programs[name_program])
            del links_to_download_programs[name_program]

        for name_program, link in links_to_download_programs.items():
            list_links_to_download_programs_output.append(link)

        return list_links_to_download_programs_output


    @staticmethod
    def _parser_func_for_priority_da_tag(line: str) -> list[str]:
        return line.strip(" ").split(",")

    @staticmethod
    def _parser_func_for_urls_tag(line: str) -> dict[str, str]:
        buffer: dict = get_buffer("parser_func_for_urls_tag")

        line = line.strip(" ")
        name_program, url_program = line.split(":")
        url_program = url_program.strip(" ")

        buffer[name_program] = url_program

        return buffer
