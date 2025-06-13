#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app_maritaca_correto import extrair_palavras_chave_maritaca_correto

api_key = '108166562600938940893_f947d1e4a1fb3013'

casos = [
    'Mauad Franqueadora Ltda.',
    'Vipex Transportes Ltda.',
    'Máquinas Furtan Ltda.',
    'Galeria Química e Farmacêutica Ltda.',
    'José Pupin Agropecuária'
]

print("🧪 TESTE RÁPIDO DO PROMPT CORRIGIDO")
print("=" * 50)

for caso in casos:
    resultado = extrair_palavras_chave_maritaca_correto(caso, api_key)
    print(f"{caso} → {resultado}")
    print() 