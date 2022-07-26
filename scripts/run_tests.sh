cd src/adapters/sourceAadapter;
python3 -m pytest -rx;
cd ../sourceBadapter;
python3 -m pytest -rx;
cd ../../consumer;
python3 -m pytest -rx;
