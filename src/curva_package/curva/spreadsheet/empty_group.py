from curva.framework.spreadsheet.group import Group


class EmptyGroup(Group):
    def __init__(self):
        self.id = None

    def set_bounds(self, vertical_offset, horizontal_offset):
        self.vertical_offset = vertical_offset
        self.horizontal_offset = horizontal_offset

    def get_dimensions(self):
        return (1, 1)

    def render(self, *_):
        pass
