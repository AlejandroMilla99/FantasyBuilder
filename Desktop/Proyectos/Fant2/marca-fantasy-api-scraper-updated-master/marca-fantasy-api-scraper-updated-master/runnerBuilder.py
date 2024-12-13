import subprocess

# Ejecutar el archivo fantasy_scraper.py
subprocess.run(["python", "fantasy_scraper.py"])

# Ejecutar el archivo tableStats.py después de fantasy_scraper.py
subprocess.run(["python", "tableStats.py"])