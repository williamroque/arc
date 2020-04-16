import session
import flux
import parse_input

import time
import locale


inputs = parse_input.Input()

flux = flux.Flux(inputs.saldo_files, inputs.starting_date)
flux_total = flux.collapse()

sess = session.Session(3, 14270000, [.15, .15, .7], 1, [.0157616486240146, .00682149336596227, .00565414538740527], .92, 10000, flux_total)
sess.run()
