from py.functions import controller
import sys
sys.path.append(r'C:\Users\thefu\Documents\nLinal-\gui')


print('Testing Vector...')
v = controller.json_a_operando('{"type":"Vector","contents":["2","5"]}')
print(type(v), v, len(v))

print('\nTesting Matrix...')
m = controller.json_a_operando(
    '{"type":"Matrix","contents":[["2","4"],["6 - \\pi","7"]]}')
print(type(m), m.filas, m.columnas, m.at(2, 1))

print('\nTesting variable env + evaluar_latex...')
varjson = '{"A": {"type": "Matrix", "contents": [["1","0"],["0","1"]]}, "x": {"type": "Vector", "contents": ["2","3"]}}'
res = controller.evaluar_latex('A x', varjson)
print('Result (latex):', res)
