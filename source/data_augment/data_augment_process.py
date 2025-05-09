import json
from tqdm import tqdm
import random
import itertools
from loguru import logger

logger.add('/home/hsy/AI_arbitration/model_train/sft_data/logs/aug_plus.log',mode='a')

instruct = """

主题需要严格在【{{topic}}】中选择

"""

dict = {
        "工伤": ["工伤赔偿程度", "工伤认定程度"],
        "经济补偿": ["经济补偿条件", "经济补偿时间", "经济补偿标准"],
        "劳动报酬": ["劳动报酬计算标准", "劳动报酬支付情况", "劳动报酬约定期限"],
        "赔偿金": ["赔偿条件", "赔偿金标准", "赔偿金支付期限"],
        "劳动合同": ["劳动合同认定", "劳动合同合法性"],
    }

labels = [item for sublist in dict.values() for item in sublist]

def augment_process_one_level(path,save_path):
    with open(path,'r',encoding='utf-8') as f:
        data = f.read()
    source_data = json.loads(data)

    all_data = []

    for item in tqdm(source_data,desc="Processing",total=len(source_data)):
        input = item['input']
        try:
            fact_data = json.loads(item['output'])
        except:
            continue
        for nums in range(1,len(fact_data)):
            random_sample = random.sample(fact_data,nums)

            # get topic
            topic = [i['主题'] for i in random_sample]
            topic_str = '、'.join(topic)

            filtered_labels = [i for i in labels if i not in topic]

            num_to_add = random.randint(2, 3)
            additional_topics = random.sample(filtered_labels, num_to_add)
            topic_str += '、' + '、'.join(additional_topics)

            data = {
                    "instruction": instruct.replace("{{topic}}",topic_str),
                    "input": input,
                    "output": str(random_sample).replace("'",'\"'),
                    "system": "You are a helpful assistant",
                    "history": []
                }
            all_data.append(data)
    random_sample_data = all_data
    random_sample_data.extend(source_data)

    with open(save_path,'w',encoding='utf-8') as f:
        f.write(json.dumps(random_sample_data,ensure_ascii=False,indent=4))

def augment_process_two_level(path,save_path):
    with open(path,'r',encoding='utf-8') as f:
        data = f.read()
    source_data = json.loads(data)

    all_data = []

    for item in tqdm(source_data,desc="Processing",total=len(source_data)):
        input = item['input']
        try:
            fact_data = json.loads(item['output'])
        except:
            continue
        for nums in range(1,len(fact_data)):
            random_sample_1 = random.sample(fact_data, nums)
            random_sample_2 = random_sample_1.copy()
          
            while random_sample_2 == random_sample_1:
                random_sample_2 = random.sample(fact_data, nums)
                
            random_sample_1 = list(random_sample_1)
            random_sample_2 = list(random_sample_2)
            for random_sample in [random_sample_1,random_sample_2]:
                # get topic
                topic = [i['主题'] for i in random_sample]
                topic_str = '、'.join(topic)

                filtered_labels = [i for i in labels if i not in topic]

                num_to_add = random.randint(nums+2, nums+5)
                additional_topics = random.sample(filtered_labels, min(num_to_add,len(filtered_labels)))
                topic_str += '、' + '、'.join(additional_topics)

                data = {
                        "instruction": instruct.replace("{{topic}}",topic_str),
                        "input": input,
                        "output": str(random_sample).replace("'",'\"'),
                        "system": "You are a helpful assistant",
                        "history": []
                    }
                all_data.append(data)
    random_sample_data = all_data
    random_sample_data.extend(source_data)

    with open(save_path,'w',encoding='utf-8') as f:
        f.write(json.dumps(random_sample_data,ensure_ascii=False,indent=4))

def augment_process_three_level(path,save_path):
    with open(path,'r',encoding='utf-8') as f:
        data = f.read()
    source_data = json.loads(data)

    all_data = []

    for item in tqdm(source_data,desc="Processing",total=len(source_data)):
        input = item['input']
        try:
            fact_data = json.loads(item['output'])
        except:
            continue
        for nums in range(1,len(fact_data)):
            random_sample_1 = random.sample(fact_data, nums)
            random_sample_2 = random_sample_1.copy()
          
            while random_sample_2 == random_sample_1:
                random_sample_2 = random.sample(fact_data, nums)

            samples = [list(random_sample_1), list(random_sample_2)]

            if len(fact_data) > 2:
                random_sample_3 = random_sample_1.copy()
                while random_sample_3 == random_sample_1 or random_sample_3 == random_sample_2:
                    random_sample_3 = random.sample(fact_data, nums)
                samples.append(list(random_sample_3))
                
            for random_sample in samples:
                # get topic
                topic = [i['主题'] for i in random_sample]
                topic_str = '、'.join(topic)

                filtered_labels = [i for i in labels if i not in topic]

                num_to_add = random.randint(nums+2, nums+5)
                additional_topics = random.sample(filtered_labels, min(num_to_add,len(filtered_labels)))
                topic_str += '、' + '、'.join(additional_topics)

                data = {
                        "instruction": instruct.replace("{{topic}}",topic_str),
                        "input": input,
                        "output": str(random_sample).replace("'",'\"'),
                        "system": "You are a helpful assistant",
                        "history": []
                    }
                all_data.append(data)
    random_sample_data = all_data
    random_sample_data.extend(source_data)

    with open(save_path,'w',encoding='utf-8') as f:
        f.write(json.dumps(random_sample_data,ensure_ascii=False,indent=4))

def augment_process_four_level(path,save_path):
    with open(path,'r',encoding='utf-8') as f:
        data = f.read()
    source_data = json.loads(data)

    all_data = []

    for item in tqdm(source_data,desc="Processing",total=len(source_data)):
        input = item['input']
        try:
            fact_data = json.loads(item['output'])
        except:
            continue
        for nums in range(1,len(fact_data)):
            random_sample_1 = random.sample(fact_data, nums)
            random_sample_2 = random_sample_1.copy()
          
            while random_sample_2 == random_sample_1:
                random_sample_2 = random.sample(fact_data, nums)

            samples = [list(random_sample_1), list(random_sample_2)]

            if len(fact_data) > 2:
                random_sample_3 = random_sample_1.copy()
                while random_sample_3 == random_sample_1 or random_sample_3 == random_sample_2:
                    random_sample_3 = random.sample(fact_data, nums)
                samples.append(list(random_sample_3))
            
            if len(fact_data) > 3:
                random_sample_4 = random_sample_1.copy()
                while random_sample_4 == random_sample_1 or random_sample_4 == random_sample_2 or random_sample_4 == random_sample_3:
                    random_sample_4 = random.sample(fact_data,nums)
                samples.append(list(random_sample_4))
                
            for random_sample in samples:
                # get topic
                topic = [i['主题'] for i in random_sample]
                topic_str = '、'.join(topic)

                filtered_labels = [i for i in labels if i not in topic]

                num_to_add = random.randint(nums+2, nums+5)
                additional_topics = random.sample(filtered_labels, min(num_to_add,len(filtered_labels)))
                topic_str += '、' + '、'.join(additional_topics)

                data = {
                        "instruction": instruct.replace("{{topic}}",topic_str),
                        "input": input,
                        "output": str(random_sample).replace("'",'\"'),
                        "system": "You are a helpful assistant",
                        "history": []
                    }
                all_data.append(data)
    random_sample_data = all_data
    random_sample_data.extend(source_data)

    with open(save_path,'w',encoding='utf-8') as f:
        f.write(json.dumps(random_sample_data,ensure_ascii=False,indent=4))

def augment_process_five_level(path,save_path):
    with open(path,'r',encoding='utf-8') as f:
        data = f.read()
    source_data = json.loads(data)

    all_data = []

    for item in tqdm(source_data,desc="Processing",total=len(source_data)):
        input = item['input']
        try:
            fact_data = json.loads(item['output'])
        except:
            continue
        for nums in range(1,len(fact_data)):

            all_combos = list(itertools.combinations(fact_data,nums))
            sample_nums = 5
            sample_combos = random.sample(all_combos,min(len(fact_data),sample_nums))
            samples = [list(i) for i in sample_combos]
            
            for random_sample in samples:
                # get topic
                topic = [i['主题'] for i in random_sample]
                topic_str = '、'.join(topic)

                filtered_labels = [i for i in labels if i not in topic]

                num_to_add = random.randint(nums+2, nums+5)
                additional_topics = random.sample(filtered_labels, min(num_to_add,len(filtered_labels)))
                topic_str += '、' + '、'.join(additional_topics)

                data = {
                        "instruction": instruct.replace("{{topic}}",topic_str),
                        "input": input,
                        "output": str(random_sample).replace("'",'\"'),
                        "system": "You are a helpful assistant",
                        "history": []
                    }
                all_data.append(data)
            

    random_sample_data = all_data
    random_sample_data.extend(source_data)

    with open(save_path,'w',encoding='utf-8') as f:
        f.write(json.dumps(random_sample_data,ensure_ascii=False,indent=4))

def augment_process_plus(path,save_path,sample_proportion=None):
    with open(path,'r',encoding='utf-8') as f:
        data = f.read()
    source_data = json.loads(data)

    all_data = []
    topic_str_set = set() 

    level_totals = {}

    for item in tqdm(source_data,desc="Processing",total=len(source_data)):
        input = item['input']
        try:
            fact_data = json.loads(item['output'])
        except:
            continue
        for nums in range(1,len(fact_data)):
            data_num = 0
            for random_sample in itertools.combinations(fact_data,nums):
        
                # get topic
                topic = [i['主题'] for i in random_sample]
                topic_str = '、'.join(topic)

                filtered_labels = [i for i in labels if i not in topic]

                num_to_add = random.randint(2, 5)
                additional_topics = random.sample(filtered_labels, min(num_to_add, len(filtered_labels)))
                topic_str += '、' + '、'.join(additional_topics)

                if topic_str in topic_str_set:
                    continue  

                topic_str_set.add(topic_str) 
                random_sample = list(random_sample) 
                data = {
                        "instruction": instruct.replace("{{topic}}",topic_str),
                        "input": input,
                        "output": str(random_sample).replace("'",'\"'),
                        "system": "You are a helpful assistant",
                        "history": []
                    }
                all_data.append(data)
                data_num += 1
            level_totals[nums] = level_totals.get(nums, 0) + data_num
    
    if sample_proportion is not None:
        sample_num = int(len(source_data) * sample_proportion)
        sample_num = min(sample_num,len(all_data))
        random_sample_data = random.sample(all_data,sample_num)

    else:
        random_sample_data = all_data

    random_sample_data.extend(source_data)

    logger.info(f"{path}的所有数据处理完成，各阶数据总量如下:")
    for nums, total in sorted(level_totals.items()):
        logger.info(f"第{nums}阶数据总量: {total}")

    # with open(save_path,'w',encoding='utf-8') as f:
    #     f.write(json.dumps(random_sample_data,ensure_ascii=False,indent=4))

def augment_custom_num(custom_size):
    '''
    custom_size
    指定比例，如果为1，则意味着按照1:1的数据进行扩,原来有50条种子数据，扩增数据也是50条
    '''
    num_list = [50,100,200,300,500,800]
    for num in num_list:
        path = f'/home/hsy/AI_arbitration/model_train/sft_data/source_data/tingshen-qwen72B_V04_{num}.json'
        save_path = f'/home/hsy/AI_arbitration/model_train/sft_data/augment_data_V01/tingshen_V05_{num}_augment_num_{num}.json'
        augment_process_one_level(path,save_path)

def augment_all():
    num_list = [50,100,200,300,500,800,1255]
    for num in num_list:
        path = f'/home/hsy/AI_arbitration/model_train/sft_data/source_data/tingshen-qwen72B_V04_{num}.json'
        save_path = f'/home/hsy/AI_arbitration/model_train/sft_data/augment_data_V01/tingshen_V13_{num}_augment.json'
        augment_process_five_level(path,save_path)

def aug():
    num_list = [50,100,200,300,500,800,1255]
    for num in num_list:
        path = f'/home/hsy/AI_arbitration/model_train/sft_data/source_data/tingshen-qwen72B_V04_{num}.json'
        save_path = f'/home/hsy/AI_arbitration/model_train/sft_data/augment_data_V01/tingshen_test_{num}_augment.json'
        augment_process_plus(path,save_path,5)


if __name__ == '__main__':
    # augment_custom_num(1)
    augment_all()
    # aug()
    