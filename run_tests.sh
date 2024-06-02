. venv/bin/activate
IS_DEV=1 PYTHONPATH="$(pwd)/src" pytest "$@"
