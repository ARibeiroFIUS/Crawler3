import pandas as pd

data = {'Nome do Cliente': ['Cliente A', 'Cliente B', 'Cliente C', 'Cliente D', 'Cliente E']}
df = pd.DataFrame(data)
df.to_excel('clientes.xlsx', index=False)


