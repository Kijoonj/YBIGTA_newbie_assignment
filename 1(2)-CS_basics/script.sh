# anaconda(또는 miniconda)가 존재하지 않을 경우 설치해주세요!
MINICONDA_DIR="$HOME/miniconda3"
ENV_NAME="myenv"
if [ ! -d "$MINICONDA_DIR" ]; then
  wget -q https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
  bash miniconda.sh -b -p "$MINICONDA_DIR"
  rm -f miniconda.sh
fi
export PATH="$MINICONDA_DIR/bin:$PATH"

eval "$(conda shell.bash hook)"

conda env list | awk '{print $1}' | grep -qx "$ENV_NAME" \
  || conda create -y -n "$ENV_NAME" python=3.10

conda activate "$ENV_NAME"



## 건드리지 마세요! ##
python_env=$(python -c "import sys; print(sys.prefix)")
if [[ "$python_env" == *"/envs/myenv"* ]]; then
    echo "[INFO] 가상환경 활성화: 성공"
else
    echo "[INFO] 가상환경 활성화: 실패"
    exit 1 
fi


# 필요한 패키지 설치
## TODO
python -m pip install --upgrade pip
pip install mypy


# Submission 폴더 파일 실행
cd submission || { echo "[INFO] submission 디렉토리로 이동 실패"; exit 1; }

for file in *.py; do
    prob="${file%.py}"   
    num="${prob#*_}"       

    input_file="../input/${num}_input"
    output_file="../output/${num}_output"

    python "$file" < "$input_file" > "$output_file"
done


# mypy 테스트 실행 및 mypy_log.txt 저장
## TODO
mypy . > ../mypy_log.txt 2>&1


# conda.yml 파일 생성
## TODO
conda env export > ../conda.yml 


# 가상환경 비활성화
## TODO
conda deactivate
