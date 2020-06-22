from curva.framework.spreadsheet.section import Section
from curva.spreadsheet.header_group import HeaderGroup
from curva.spreadsheet.empty_group import EmptyGroup
from curva.spreadsheet.fluxo_creditos.index_group import IndexGroup
from curva.spreadsheet.fluxo_creditos.value_group import ValueGroup
from curva.spreadsheet.fluxo_creditos.date_group import DateGroup


class FluxoCreditosSection(Section):
    def __init__(self, parent_sheet, inputs):
        super().__init__(
            parent_sheet,
            inputs,
            'fluxo-creditos-section',
            [0, 1],
            [2, 1]
        )

        self.add_row()

        header_group = HeaderGroup(
            self,
            'Fluxo de Créditos Imobiliários',
            'header',
            2,
            3
        )
        self.add_group(header_group)

        self.add_row()

        index_group = IndexGroup(
            self,
            self.inputs
        )
        self.add_group(index_group)

        value_group = ValueGroup(
            self,
            self.inputs
        )
        self.add_group(value_group),

        date_group = DateGroup(
            self,
            self.inputs
        )
        self.add_group(date_group)