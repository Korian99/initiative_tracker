# initiative_tracker

## Levantar el proyecto Backend

### Local
Posicionado en la carpeta Raiz
Crear un entorno virtual
python -m venv venv
Activar entorno virtual
```bash
venv\Scripts\activate.bat
```
Instalar dependencias, si fuese necesario
```bash
pip install -r requirements.txt

Crear migraciones
```bash
python manage.py makemigrations
python manage.py migrate --database=gym_db
```
Crear super usuario
```bash
python manage.py createsuperuser
```
Inicaiar servidor
```bash
python manage.py runserver
```

## Ejecutar Frontend: 🚀

```Posicionarse
cd frontend
  configurar proxy, en caso de haber uno:
```bash
  npm config set proxy http://proxy_host:port
```
Dentro de cpa usar:
```bash
  npm config set proxy http://134.14.0.1:3128
```
Instalar dependencias
```bash
  npm install
```

 correr proyecto
 ```bash
  npm start
```

## Pre-commit
El pre-commit es una herramienta que ayuda a mantener la calidad del código, mejora la consistencia y evita problemas, realizando controles antes de hacer un commit.

## Configuracion de pre-commit
Debera tener:
A nivel raiz del proyecto
--> Carpeta "scritps"
--> .pre-commit-config.yaml
En carpeta frontend
--> .prettierrc

## En la carpeta raiz del proyecto initiative_tracker correr el comando:
pip install pre-commit

## En la carpeta backend, dentro del entorno virtual correr el comando:
```bash
pip install pre-commit
pre-commit install
```

## En la carpeta frontend del proyecto correr el comando:
```bash
npm install
npm install eslint-plugin-react --save-dev
```
