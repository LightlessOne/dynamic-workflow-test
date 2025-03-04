set -e
python -m venv .venv
source .venv/Scripts/activate

export PIPELINE_VARS=$(cat ./inputs/PIPELINE_VARS.txt)
export PIPELINE_DATA=$(cat ./inputs/PIPELINE_DATA.txt)

#echo "$PIPELINE_VARS" >> qwe.yaml

pip install python-gitlab pyyaml
python -m github_generator
