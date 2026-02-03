import json
import os
import re


def clean_latex_spaces(latex_str):
    """
    清理LaTeX数学公式中多余的空格，保留必要的语义空格。
    """
    if not latex_str:
        return ""
    # 1. 预处理
    s = re.sub(r'\s+', ' ', latex_str).strip()
    # 2. 保护机制 (\alpha b -> \alpha<KEEP>b)
    s = re.sub(r'(\\[a-zA-Z]+) (?=[a-zA-Z])', r'\1@@SPACE@@', s)
    # 保护转义空格 "\ "
    s = s.replace(r'\ ', '@@CONTROL_SPACE@@')
    # 3. 删除所有空格
    s = s.replace(' ', '')
    # 4. 还原
    s = s.replace('@@SPACE@@', ' ')
    s = s.replace('@@CONTROL_SPACE@@', r'\ ')
    return s
def load_jsonl_to_dict(file_path):
    """
    读取 label 文件，存为 {id: tex} 的字典格式。
    增加了 try-except 以跳过非 json 行（如 shell 里的 warning 或命令）。
    """
    data_dict = {}
    print(f"正在加载 Label 文件: {file_path} ...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
                # 提取 id 和 tex
                if 'id' in item and 'tex' in item:
                    data_dict[item['id']] = item['tex']
            except json.JSONDecodeError:
                # 跳过无法解析的行（例如命令行输出的 header）
                print(f"[Warning] Label文件第 {line_num} 行不是有效的JSON，已跳过: {line[:50]}...")
                continue
    
    print(f"Label 加载完成，共索引 {len(data_dict)} 条数据。")
    return data_dict

def convert_results(pred_path, label_path, output_path):
    # 1. 加载 Label 数据
    gt_dict = load_jsonl_to_dict(label_path)
    
    results = []
    matched_count = 0
    missing_count = 0

    print(f"正在处理 Pred 文件: {pred_path} ...")
    
    # 2. 遍历 Pred 文件并匹配
    with open(pred_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                pred_item = json.loads(line)
                img_id = pred_item.get('id')
                pred_tex = pred_item.get('tex')

                if img_id:
                    # 在 gt_dict 中查找对应的 label
                    if img_id in gt_dict:
                        results.append({
                            "img_id": img_id,
                            "gt": clean_latex_spaces(gt_dict[img_id]),
                            "pred": clean_latex_spaces(pred_tex)
                        })
                        matched_count += 1
                    else:
                        # 如果 pred 有 id 但 label 里没找到
                        missing_count += 1
                        # 可选：如果你希望即使没有 GT 也保留记录，可以取消下面注释
                        # results.append({
                        #     "img_id": img_id,
                        #     "gt": "", # 或者 None
                        #     "pred": pred_tex
                        # })

            except json.JSONDecodeError:
                continue

    # 3. 输出结果到 JSON 文件
    print(f"正在写入结果到: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        # ensure_ascii=False 保证中文或特殊字符正常显示，indent=4 美化输出
        json.dump(results, f, indent=4, ensure_ascii=False)

    print("-" * 30)
    print(f"处理完成！")
    print(f"成功匹配: {matched_count} 条")
    print(f"未找到GT: {missing_count} 条")
    print(f"结果已保存至: {output_path}")

if __name__ == "__main__":
    # --- 在这里修改你的文件路径 ---
    pred_file = "/home/baiweikang/Projects/Taichi/latex_infer_result_18.jsonl"      # 你的预测文件路径
    label_file = "/remote-home/baiweikang/CMER_Bench_1_0_total.jsonl"    # 你的标签文件路径
    output_file = "cdm_infer_result_18.json"   # 输出结果路径
    
    # 检查文件是否存在
    if not os.path.exists(pred_file) or not os.path.exists(label_file):
        print("错误: 找不到输入文件，请检查代码底部的路径配置。")
    else:
        convert_results(pred_file, label_file, output_file)