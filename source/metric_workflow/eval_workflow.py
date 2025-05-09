import requests
import os
import json
from openai_chat import OpenAIChat
from loggerManager import LoggerManager
from tqdm import tqdm
import time
import concurrent.futures

eval_prompt = """

"""
extract_prompt_without_label = """

"""

extract_prompt = """

"""

# 处理ds输出的思维链数据
def deepseek_data_process(response):
    response = response.content
    data = response.split('\n</think>\n\n')[-1]
    data = data.replace('json', '').replace('```', '')
    return data

# 抽取模型
def model_extract(messages,name='qwen',port=8000):
    base_url = f'http://127.0.0.1:{port}/v1'
    api_key = 'EMPTY'
    model_name = name
    openai_chat = OpenAIChat(base_url,api_key,model_name)
    response = openai_chat.chat(messages)
    return response.choices[0].message

# 评测模型
def model_response(messages):
    base_url = 'http://127.0.0.1:8000/v1'
    api_key = 'EMPTY'
    model_name = 'deepseek'
    openai_chat = OpenAIChat(base_url,api_key,model_name)
    response = openai_chat.chat(messages)
    return response.choices[0].message

def facts_format(extract_result):
    try:
        text = extract_result.content
    except AttributeError:
        text = extract_result
    try:
        # facts = json.loads(text)
        if text.startswith('(') and text.endswith(')'):
            text = text.replace("(", "[", 1)  # 替换第一个匹配项
            # 替换最后一个 ) 为 ]
            text = text[::-1].replace(")", "]", 1)[::-1]
        # 替换掉错误输出
        if len(text) >= 2 and text[-2] == ",":
            text = text[:-2] + text[-1]
        facts = json.loads(text.replace("'",'"'))
        facts = get_facts(facts)
        return facts

    except Exception as e:
        logger.debug("输出格式有误！无法通过json.loads进行转换")
        return [
            {
                "事实认定": "None"
            }
        ]

def get_facts(data):
    if isinstance(data,dict):
        return {key: get_facts(value) for key, value in data.items() if key == "事实认定"}
    elif isinstance(data,list):
        return [get_facts(item) for item in data]
    else:
        return data

# 先抽测试集笔录
def extract_test_set(annotated_path,tmp_path,if_deepseek=False,name='qwen',port=8000):
    with open(annotated_path,'r',encoding='utf-8') as f:
        json_data = f.read()
    data = json.loads(json_data)
    for item in tqdm(data,total=len(data),desc='评测模型抽取测试庭审笔录文本'):       
        messages = [
                {"role": "system", "content": extract_prompt_without_label},
                {
                    "role": "user",
                    "content": item['庭审笔录']
                }
            ]
        extract_result = model_extract(messages,name,port)
        if if_deepseek:
            extract_result = deepseek_data_process(extract_result)
            facts = facts_format(extract_result)
        else:
            facts = facts_format(extract_result)
        item['抽取结果'] = facts
    with open(tmp_path, 'w', encoding='utf-8') as f:
        json.dump(data,f,ensure_ascii=False,indent=4)


# 获得模型评估结果
def metric(tmp_path,save_path):
    
    # 标注数据加载
    with open(tmp_path,'r',encoding='utf-8') as f:
        json_data = f.read()
    data = json.loads(json_data)

    total_cor_num = 0
    total_incor_num = 0
    total_label_facts_num = 0

    for item in tqdm(data,total=len(data)):
        correct_num = 0
        incorrect_num = 0
        label_facts_num = len(item['事实标注'])
        item['评估结果'] = []
        for fact in item['抽取结果']:
            try:
                messages=[
                    {"role": "system", "content": eval_prompt},
                    {
                        "role": "user",
                        "content": f"### 事实：{fact['事实认定']}### 人工标注列表：{item['事实标注']}" 
                    }
                ]
            except KeyError:
                messages=[
                    {"role": "system", "content": eval_prompt},
                    {
                        "role": "user",
                        "content": f"### 事实：{fact}### 人工标注列表：{item['事实标注']}" 
                    }
                ]
            response = model_response(messages)
            item['评估结果'].append(response.content)
            if 'True' in response.content:
                correct_num += 1
                logger.info(f"卷宗编号:{item['卷宗编号']} | 模型抽取事实:{fact} | 评测CoT:{response.content} | 正确")
            else:
                incorrect_num += 1
                logger.info(f"卷宗编号:{item['卷宗编号']} | 模型抽取事实:{fact} | 评测CoT:{response.content} | 错误")
        total_cor_num += correct_num
        total_incor_num += incorrect_num
        total_label_facts_num += label_facts_num
        logger.info(f"卷宗编号:{item['卷宗编号']} | 正确个数:{correct_num} | 错误个数:{incorrect_num} | 标注数量:{label_facts_num} | 准确率:{correct_num / (correct_num + incorrect_num)} ｜ 召回率:{min(correct_num / label_facts_num, 1)}")
    
    logger.info(f"Total Correct: {total_cor_num}")
    logger.info(f"Total Incorrect: {total_incor_num}")
    logger.info(f"Total Label: {total_label_facts_num}")
    logger.info(f"Precision:{total_cor_num / (total_cor_num + total_incor_num)}")
    logger.info(f"Recall:{total_cor_num / total_label_facts_num}")
    precision = total_cor_num / (total_cor_num + total_incor_num)
    recall = total_cor_num / total_label_facts_num
    logger.info(f"F1-score:{2 * (precision * recall) / (precision + recall)}")


    with open(save_path,'w',encoding='utf-8') as f:
        json.dump(data,f,ensure_ascii=False,indent=4)
    logger.info(f'文件保存成功，路径为:{save_path}')

def process_model(name,port):
        model_name = f"qwen1.5B-{name.split('_')[-1]}sft-augment-two_level"
        logger_manager = LoggerManager(f'/home/hsy/AI_arbitration/metric/log/log_{model_name}_extract_ds32B_eval.txt')
        logger = logger_manager.get_logger()
        annotated_data_path = '/home/hsy/AI_arbitration/data_annotated/data/annotated_data_V03.json'
        tmp_path = f'/home/hsy/AI_arbitration/metric/data/tmp_{model_name}.json'
        save_path = f"/home/hsy/AI_arbitration/metric/data/eval_{model_name}_extract_ds32B_eval.json"
        extract_test_set(annotated_data_path,tmp_path,False,name,port)
        # metric(tmp_path,save_path)

if __name__ == '__main__':
    model_name = "qwen"
    logger_manager = LoggerManager(f'/home/hsy/AI_arbitration/metric/log/log_{model_name}_without_label_extract_ds32B_eval.txt')
    logger = logger_manager.get_logger()
    annotated_data_path = '/home/hsy/AI_arbitration/data_annotated/data/annotated_data_V03.json'
    tmp_path = f'/home/hsy/AI_arbitration/metric/data/tmp_{model_name}_without_label.json'
    save_path = f"/home/hsy/AI_arbitration/metric/data/eval_{model_name}_without_label_extract_ds32B_eval.json"
    extract_test_set(annotated_data_path,tmp_path,True,port=8000)
    metric(tmp_path,save_path)
