. env/bin/activate
nohup python src/main.py &> run.log 2> run.err &
disown

