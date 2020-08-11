class Tranche():
    def __init__(self, inputs, taxa_juros, razao, tranche_id):
        self.id = tranche_id

        self.saldo_original = inputs.get('curve')['total'] * razao

        self.inputs = inputs
        self.saldo = self.saldo_original
        self.taxa_juros = taxa_juros

        self.is_finished = False
        self.phase_list = []
        self.row_list = []

        self.queue = None

        self.i = 0
        self.phase_first_index = 0

    def create_row(self):
        raise NotImplementedError

    def next_phase(self):
        self.phase_list = self.phase_list[1:]
        self.phase_first_index = self.i + 1

    def integrate_row(self):
        if self.queue:
            self.row_list.append(self.queue)
            self.i += 1

    def get_previous_row(self):
        return self.row_list[-1]

    def get_completion_state(self):
        if self.saldo <= 0:
            self.is_finished = True
            return True
        return False

    def calculate(self, tranche_list, tranche_i):
        if len(self.phase_list):
            while self.phase_list[0](self, tranche_list, tranche_i):
                pass
        else:
            self.queue = None


class TrancheRow():
    def __init__(self):
        self.columns = {}

    def add_column(self, column_id, title, column_width, formulae, style):
        self.columns[column_id] = {
            'title': title,
            'column_width': column_width,
            'formulae': formulae,
            'style': style
        }

    def fill(self, column_id, value, formula, substitution_map={}):
        self.columns[column_id]['value'] = value

        formulae = self.columns[column_id]['formulae']
        self.columns[column_id]['formula'] = (
            formulae[formula], substitution_map)

    def get_columns(self):
        return self.columns

    def get_value(self, column_id):
        return self.columns[column_id]['value']

    def get_values(self):
        return [self.get_value(col) for col in self.columns]
