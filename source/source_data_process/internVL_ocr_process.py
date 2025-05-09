import shutil

from openai import OpenAI
import os
from docx import Document
from tqdm import tqdm
from loguru import logger

logger.remove()
logger.add(
    "docx_process.log",
    rotation="30 MB",
    retention="10 days",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)

client = OpenAI(api_key='YOUR_API_KEY', base_url='http://172.25.34.208:23333/v1')
model_name = client.models.list().data[0].id

# ocr识别
def get_ocr_text(image_path):
    response = client.chat.completions.create(
        model=model_name,
        messages=[{
            'role':
            'user',
            'content': [{
                'type': 'text',
                'text': 'ocr识别pdf文本,只需要输出识别的文本，不需要输出其他内容',
            }, {
                'type': 'image_url',
                'image_url': {
                    'url':
                    image_path,
                },
            }],
        }],
        temperature=0,
        top_p=0.8)
    result = response.choices[0].message.content
    return result

def save_text_to_docx(text,docx_path):
    document = Document()
    document.add_paragraph(text)
    document.save(docx_path)
    print(f"已保存文档: {docx_path}")

def process_dir(main_path, image_extensions=None):
    if image_extensions is None:
        image_extensions = ['.jpg']
    for entry in tqdm(os.scandir(main_path),desc='Dir Processing...',total=len(os.listdir(main_path))):
        if entry.is_dir():
            subfolder_path = entry.path
            subfolder_name = os.path.basename(subfolder_path)
            print(f'正在处理卷宗：{subfolder_path}')

            combined_text = ''
            # 筛选出符合条件的文件并按数字顺序排序
            try:
                # 获取所有符合条件的文件
                image_files = [
                    file_entry for file_entry in os.scandir(subfolder_path)
                    if file_entry.is_file() and os.path.splitext(file_entry.name)[1].lower() in image_extensions
                ]

                # 对文件按数字排序
                sorted_image_files = sorted(
                    image_files,
                    key=lambda e: int(os.path.splitext(e.name)[0]) if os.path.splitext(e.name)[0].isdigit() else float('inf')
                )
            except Exception as e:
                print(f"在处理文件夹 {subfolder_path} 时出错: {e}")
                continue  # 跳过当前子文件夹，继续下一个

            for file_entry in tqdm(sorted_image_files,total=len(sorted_image_files)):
                if file_entry.is_file():
                    file_extension = os.path.splitext(file_entry.name)[1].lower()
                    if file_extension in image_extensions:
                        image_path = file_entry.path
                        ocr_text = get_ocr_text(image_path)
                        combined_text += ocr_text

            if combined_text:
                docx_filename = f"{subfolder_name}-ts.docx"
                docx_path = os.path.join(subfolder_path, docx_filename)
                if not os.path.exists(docx_path):
                    save_text_to_docx(combined_text, docx_path)
                else:
                    print(f"文档 {docx_filename} 已存在，跳过保存。")
            else:
                print(f"文件夹 {subfolder_path} 中没有找到指定格式的图片。\n")

def collect_docx(main_path,output_dir,pattern='-ts.docx',overwrite=False):
    if not os.path.exists(main_path):
        logger.error(f"主目录{main_path}不存在。")
        return
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            logger.info(f"已创建输出目录：{output_dir}")
        except Exception as e:
            logger.error(f"无法创建输出目录{output_dir}:{e}")

    subdirs = [entry.path for entry in os.scandir(main_path) if entry.is_dir()]
    if not subdirs:
        logger.warning(f'主目录{main_path}下没有子目录')
        return

    docx_files = []
    for subdir in subdirs:
        try:
            for file in os.scandir(subdir):
                if file.is_file() and file.name.endswith(pattern):
                    full_path = file.path
                    docx_files.append(full_path)
                    logger.debug(f"找到符合条件的 DOCX 文件：{file}")
        except Exception as e:
            logger.error(f"无法访问子目录{subdir}:{e}")

    if not docx_files:
        logger.warning(f"在 {main_path} 下的子目录中未找到符合模式 '{pattern}' 的 DOCX 文件。")
        return

    logger.info(f"找到 {len(docx_files)} 个符合条件的 DOCX 文件。开始复制...")

    for docx_file in tqdm(docx_files,desc='copy docx...',total=len(docx_files)):
        try:
            filename = os.path.basename(docx_file)
            destination = os.path.join(output_dir,filename)

            if os.path.exists(destination):
                if overwrite:
                    shutil.copy2(docx_file,destination)
                    logger.info(f"文件{filename}已覆盖")
                else:
                    logger.info(f"文件{filename}存在于输出目录，跳过复制")
                    continue
            else:
                shutil.copy2(docx_file, destination)
                logger.debug(docx_file,destination)
        except Exception as e:
            logger.error(f"复制文件{docx_file}出错:{e}")
    logger.info(f"所有符合条件的 DOCX 文件已复制到 {output_dir}。")

if __name__ == '__main__':
    main_paths = [
        '/home/hsy/AI_arbitration/data/2021年仲裁0300-0399-done',
        '/home/hsy/AI_arbitration/data/2021年仲裁0400-0451-done',
        '/home/hsy/AI_arbitration/data/2021年仲裁0673-0699-done',
        '/home/hsy/AI_arbitration/data/2021年仲裁0700-0799-done',
        '/home/hsy/AI_arbitration/data/2021年仲裁0800-0899-done',
        '/home/hsy/AI_arbitration/data/2021年仲裁0900-0999-done',
        '/home/hsy/AI_arbitration/data/2021年仲裁1000-1099-done',
        '/home/hsy/AI_arbitration/data/2021年仲裁1100-1199-done',
        '/home/hsy/AI_arbitration/data/2021年仲裁1200-1299-done',
        '/home/hsy/AI_arbitration/data/2021年仲裁1300-1399-done',
        '/home/hsy/AI_arbitration/data/2021年仲裁1400-1499-done',
        '/home/hsy/AI_arbitration/data/2021年仲裁1500-1599-done',
        '/home/hsy/AI_arbitration/data/2021年仲裁1600-1695-done',
        '/home/hsy/AI_arbitration/data/2021年仲裁1700-1790-done',
        '/home/hsy/AI_arbitration/data/2021年仲裁1800-1899-done',
        '/home/hsy/AI_arbitration/data/2021年仲裁1900-1999-done',
        '/home/hsy/AI_arbitration/data/2021年仲裁2000-2099-done',
        '/home/hsy/AI_arbitration/data/2021年仲裁2100-2199-done',
        '/home/hsy/AI_arbitration/data/2021年仲裁2200-2256-done',
        '/home/hsy/AI_arbitration/data/2021年仲裁2303-2399-done',
        '/home/hsy/AI_arbitration/data/2021年仲裁2406-2488-done',
    ]
    output_dir = '/home/hsy/AI_arbitration/data/docx/'
    for main_path in tqdm(main_paths,desc='Total Processing...',total=len(main_paths)):
        process_dir(main_path)
        collect_docx(main_path,output_dir)














