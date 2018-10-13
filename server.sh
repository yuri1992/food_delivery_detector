#!/usr/bin/env bash
cd /usr/web/food_delivery_detector
source venv/bin/activate
export FLASK_APP=server.py
flask run --host=0.0.0.0
