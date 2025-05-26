# Flet app

Para crear el entorno virtual
```
python3.13 -m venv myenv 
```

Para activar el entorno virtual
```
source myenv/bin/activate 
```

Para actualizar pip
```
pip install --upgrade pip  
```


To run the app:

1. Install dependencies from pyproject.toml:

```
poetry install

```

2. Build app:

```
poetry run flet build macos -v
```

3. Run app:

```
flet run
```# AgendaLenguajes
