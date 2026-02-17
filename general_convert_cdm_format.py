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
def load_pred_to_dict(file_path):
    """
    读取 pred 文件，存为 {id: tex} 的字典格式，方便后续快速查找。
    """
    pred_dict = {}
    print(f"正在建立 Pred 索引: {file_path} ...")
    
    if not os.path.exists(file_path):
        print(f"[Warning] Pred 文件不存在: {file_path}")
        return {}

    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
                if 'id' in item:
                    # 注意：如果存在重复ID，后读取的会覆盖先读取的
                    pred_dict[item['id']] = item.get('tex', "")
            except json.JSONDecodeError:
                # 跳过非 JSON 行
                continue
    
    print(f"Pred 索引建立完成，共 {len(pred_dict)} 条数据。")
    return pred_dict

def align_results(pred_path, label_path, output_path):
    # 1. 先把 Pred 数据加载到内存字典中
    pred_dict = load_pred_to_dict(pred_path)
    
    results = []
    matched_count = 0
    missing_count = 0
    total_labels = 0

    print(f"正在根据 Label 文件生成最终结果: {label_path} ...")
    
    # 2. 逐行读取 Label 文件，保证输出顺序和数量与 Label 一致
    with open(label_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                label_item = json.loads(line)
                
                # 提取必要字段
                img_id = label_item.get('id')
                gt_tex = label_item.get('tex', "")

                # 如果这行数据没有id，通常是坏数据，但也可能需要保留结构，
                # 这里假设没有ID的label行我们无法匹配，选择跳过或保留（视情况而定），
                # 下面逻辑为：必须有ID才处理
                if img_id:
                    total_labels += 1
                    
                    # 在 Pred 字典中查找
                    if img_id in pred_dict:
                        pred_tex = pred_dict[img_id]
                        matched_count += 1
                    else:
                        # 找不到对应的 pred，置为空字符串
                        pred_tex = ""
                        missing_count += 1
                    
                    # 构建结果对象
                    results.append({
                        "img_id": img_id,
                        "gt": clean_latex_spaces(gt_tex),
                        "pred": clean_latex_spaces(pred_tex)
                    })
            
            except json.JSONDecodeError:
                # 忽略 Label 文件中的非 JSON 行（如 shell 输出信息）
                continue

    # 3. 写入文件
    print(f"正在写入结果到: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    print("-" * 30)
    print(f"处理完成！")
    print(f"Label总数: {total_labels}")
    print(f"成功匹配 Pred: {matched_count}")
    print(f"缺失 Pred (置空): {missing_count}")
    print(f"输出文件条数: {len(results)}")

if __name__ == "__main__":
    # --- 请在此处修改文件路径 ---
    pred_file = "/cdm/code/latex_infer_output/latex_infer_result_31.jsonl"      # 你的预测文件路径
    label_file = "/cdm/data/CMER_Bench_1_0_total.jsonl"    # 你的标签文件路径
    output_file = "/cdm/code/cdm_infer_result/cdm_infer_result_31.json"   # 输出结果路径
    
    if not os.path.exists(label_file):
        print(f"错误: 找不到 Label 文件 {label_file}")
    else:
        align_results(pred_file, label_file, output_file)