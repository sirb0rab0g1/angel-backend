# python3 -m venv myenv : >>> only once if creating new env

source myenv/bin/activate
# gunicorn -w 4 -b 0.0.0.0:5000 app:app