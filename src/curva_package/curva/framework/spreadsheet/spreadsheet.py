import xlsxwriter


class Spreadsheet():
    def __init__(self, inputs, props, padding):
        self.inputs = inputs 

        self.sections = []
        self.structure = []

        self.workbook = xlsxwriter.Workbook(props['output_path'])
        self.workbook.set_size(props['width'], props['height'])

        self.sheet = self.workbook.add_worksheet(props['sheet_title'])
        self.sheet.hide_gridlines(2)
        self.sheet.set_default_row(18)

        self.padding = padding

    def add_image(self, *args):
        self.sheet.insert_image(*args)

    def add_section(self, section):
        vertical_offset, horizontal_offset = self.padding

        for row in self.structure:
            max_height = 0
            for s in row:
                s_height = s.get_dimensions()[0]
                if s_height > max_height:
                    max_height = s_height

            vertical_offset += max_height

        for s in self.structure:
            horizontal_offset += s.get_dimensions()[1]

        section.set_bounds(
            vertical_offset,
            horizontal_offset
        )

        self.sections.append(section)
        self.structure.append(section)

    def query(self, section_id):
        search_generator = (section for section in self.sections if section.id == section_id)
        try:
            return next(search_generator)
        except StopIteration:
            return None

    def render(self):
        for section in self.sections:
            section.render(self.sheet, self.workbook)
        self.workbook.close()
