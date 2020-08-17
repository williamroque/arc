from curva.framework.spreadsheet.spreadsheet import Spreadsheet
from curva.spreadsheet.util.empty_section import EmptySection
from curva.spreadsheet.prelude.section import PreludeSection
from curva.spreadsheet.taxa_emissao.section import TaxaEmissaoSection
from curva.spreadsheet.fluxo_creditos.section import FluxoCreditosSection
from curva.spreadsheet.tranches.section import TrancheSection
from curva.spreadsheet.fluxo_financeiro.section import FluxoFinanceiroSection

import importlib.resources
import curva.assets


class CurveSheet(Spreadsheet):
    def __init__(self, inputs):
        super().__init__(
            inputs,
            {
                'output_path': inputs.get('output-path'),
                'width': 1400,
                'height': 1000,
                'sheet_title': 'Curva'
            },
            [0, 0]
        )

        prelude_section = PreludeSection(
            self,
            self.inputs
        )
        self.add_section(prelude_section)

        with importlib.resources.path(curva.assets, 'logo.png') as p:
            logo_path = str(p)
        self.add_image(
            'F2',
            logo_path,
            {
                'x_scale': 0.75,
                'y_scale': 0.85,
                'x_offset': 10,
                'y_offset': -10
            }
        )

        taxa_emissao_section = TaxaEmissaoSection(
            self,
            self.inputs
        )
        self.add_section(taxa_emissao_section)

        empty_section = EmptySection((1, 1), 4)
        self.add_section(empty_section)

        fluxo_creditos_section = FluxoCreditosSection(
            self,
            self.inputs
        )
        self.add_section(fluxo_creditos_section)

        for tranche_i, tranche in enumerate(self.inputs.get('tranche-list')):
            empty_section = EmptySection((1, 1), 4)
            self.add_section(empty_section)

            tranche_section = TrancheSection(
                self,
                self.inputs,
                tranche,
                tranche_i
            )
            self.add_section(tranche_section)

        empty_section = EmptySection((1, 1), 4)
        self.add_section(empty_section)

        fluxo_financeiro_section = FluxoFinanceiroSection(
            self,
            self.inputs
        )
        self.add_section(fluxo_financeiro_section)
