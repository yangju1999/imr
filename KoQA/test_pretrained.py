#fine tuning 한 모델과의 비교를 위한 pretrained 모델 성능 test 코드 

import torch
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

MODEL = "EleutherAI/polyglot-ko-5.8b"   #hugging face에서 pretrained 모델 path  

bnb_config = BitsAndBytesConfig(    #test할때도 동일하게 4비트 양자화 사용 
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16
)

#hugging face에서 pretrained 모델 load 
model = AutoModelForCausalLM.from_pretrained(
    MODEL,
    quantization_config=bnb_config,
    torch_dtype=torch.float16,
    low_cpu_mem_usage=True,
    device_map={"":0}
)
model.eval()

pipe = pipeline(
    'text-generation', 
    model=model,
    tokenizer=MODEL
)

#모델 테스트를 위한 함수 (문맥(optional), 질문을 input으로 받아 answer를 output)
def ask(x, context='', is_input_full=False):
    ans = pipe(
        f"### 질문: {x}\n\n### 맥락: {context}\n\n### 답변:" if context else f"### 질문: {x}\n\n### 답변:", 
        do_sample=True, 
        max_new_tokens=100,
        temperature=0.7,
        top_p=0.9,
        return_full_text=False,
        eos_token_id=2,
    )
    print(f"### 질문: {x} \n\n ### 답변: {ans[0]['generated_text']} " )

ask('건강하게 살기 위한 세 가지 방법은?')
ask('피부가 좋아지는 방법은?')
ask('파이썬과 c 언어중에 코드 실행속도 측면에서 빠른 언어는?')
ask('축구를 가장 잘하는 나라는?')







