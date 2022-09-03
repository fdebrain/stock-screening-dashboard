SHELL := /bin/bash

init:
	poetry init

install:
	poetry install

run:
	streamlit run app.py
