


all:
	python ./filter_pure_mavlab.py
	make -C ./website
	python filter_by_user.py
