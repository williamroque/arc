from curva.framework.spreadsheet.section import Section
from curva.spreadsheet.groups.header_group import HeaderGroup
from curva.spreadsheet.groups.empty_group import EmptyGroup
from curva.spreadsheet.tranches.column_header_group import ColumnHeaderGroup


class TrancheSection(Section):
    def __init__(self, parent_sheet, inputs, section_id, tranche):
        super().__init__(parent_sheet, inputs, section_id, [0, 1], [2, 0])

        self.add_row()

        column_count = len(tranche.row_list[0].get_values()) + 3

        header_group = HeaderGroup(self, tranche.title, 'header', 2, column_count)
        self.add_group(header_group)

        self.add_row()

        empty_group = EmptyGroup((1, column_count), set(['w', 'e']))
        self.add_group(empty_group)

        #self.add_row()

        #column_header_group = ColumnHeaderGroup(self, self.inputs, )

