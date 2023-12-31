import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel, PeftConfig

#peft 방식으로 fine tuning 한 모델 불러오기
peft_model_id = "./outputs_qg/checkpoint-1000"  #finetuned 모델 path  
config = PeftConfig.from_pretrained(peft_model_id)
bnb_config = BitsAndBytesConfig(     #test할때도 동일하게 4비트 양자화 사용 
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16
)
model = AutoModelForCausalLM.from_pretrained(config.base_model_name_or_path, quantization_config=bnb_config, device_map={"":0})
model = PeftModel.from_pretrained(model, peft_model_id)
tokenizer = AutoTokenizer.from_pretrained(config.base_model_name_or_path)

model.eval()

#모델 테스트를 위한 함수 (문맥을 input으로 받아 question을 output)
def gen(x):
    q = f"### 문맥: {x}\n\n위의 문맥에서 정답을 찾을 수 있는 질문 하나 생성해줘### 질문:"
    # print(q)
    gened = model.generate(
        **tokenizer(
            q, 
            return_tensors='pt', 
            return_token_type_ids=False
        ).to('cuda'), 
        max_new_tokens=100,
        early_stopping=True,
        do_sample=True,
        eos_token_id=2,
    )
    result = tokenizer.decode(gened[0]) #깔끔하게 질문 1개만을 출력하기 위한 전처리 코드 
    question_start_index = result.find('질문:')
    question_end_index = question_start_index + result[question_start_index:].find('?')
    print(result[question_start_index+3: question_end_index+1])

gen('운영체제는 파일 시스템 관리, 프로세스 스케줄링, 메모리 관리, 동기화 및 상호배제 등의 다양한 기능을 수행한다.')
