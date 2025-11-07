import os
import shutil

"""
Move Logo_tabacaria.png from Templates/ to static/ if present.
Run this script from the repository root (where app.py is) with:
    python .\scripts\move_logo.py

This script is non-destructive: it will not overwrite an existing file in static/ unless you confirm.
"""

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates_logo = os.path.join(ROOT, 'Templates', 'Logo_tabacaria.png')
static_logo = os.path.join(ROOT, 'static', 'Logo_tabacaria.png')

def main():
    if not os.path.exists(templates_logo):
        print(f'Arquivo não encontrado em Templates/: {templates_logo}')
        if os.path.exists(static_logo):
            print('Parece que o logo já está em static/. Nada a fazer.')
        return

    if os.path.exists(static_logo):
        print(f'Já existe um arquivo em static/: {static_logo}')
        confirm = input('Deseja sobrescrever? [s/N]: ').strip().lower()
        if confirm != 's':
            print('Operação cancelada.')
            return

    os.makedirs(os.path.dirname(static_logo), exist_ok=True)
    shutil.move(templates_logo, static_logo)
    print(f'Movido {templates_logo} -> {static_logo}')

if __name__ == '__main__':
    main()
