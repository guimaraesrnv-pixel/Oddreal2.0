import sys
import os

# Força o Python a enxergar as pastas do projeto na raiz
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.main import main

if __name__ == "__main__":
    main()
