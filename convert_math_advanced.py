import os
import re
from pathlib import Path
from datetime import datetime

def convert_all_math(content):
    """
    最终版LaTeX数学表达式转换器
    特点：
    1. 只转换数学公式部分（保持原有所有转换功能）
    2. 完全保留非数学内容的原始格式
    3. 不处理标题、表格、图片等Markdown元素
    """
    # 保护所有非数学内容（代码块、表格、图片等）
    protected_blocks = []
    
    def protect_non_math(match):
        protected_blocks.append(match.group(0))
        return f"@@PROTECTED_BLOCK_{len(protected_blocks)-1}@@"
    
    # 保护以下内容不被处理：
    # 1. 代码块 ``` ```
    # 2. 图片 ![alt](src)
    # 3. 表格 | --- | --- |
    # 4. HTML标签 <...>
    # 5. 标题 # ## ###
    protection_pattern = r'```.*?```|!\[.*?\]\(.*?\)|<[^>]+>|#{1,6}\s.*?\n|(\|.*\|(\n|\r\n)?)+'
    content = re.sub(protection_pattern, protect_non_math, content, flags=re.DOTALL)
    
    # 原有数学公式转换逻辑（完全保持不变）
    # 0. 预处理多行公式环境
    def process_math_env(match):
        env_content = match.group(2).replace('\n', ' ').strip()
        return re.sub(r'\s+', ' ', env_content)  # 压缩多余空格
    
    content = re.sub(
        r'\\begin\{(equation\*?|align\*?|gather\*?|multline\*?)\}(.*?)\\end\{\1\}',
        process_math_env,
        content,
        flags=re.DOTALL
    )
    
    # 1. 替换数学环境标记
    content = re.sub(r'(?<!\\)\$(.*?)(?<!\\)\$', lambda m: m.group(1), content)  # 行内公式
    content = re.sub(r'\\\((.*?)\\\)', lambda m: m.group(1), content)            # \(...\)
    content = re.sub(r'\\\[(.*?)\\\]', lambda m: m.group(1), content)           # \[...\]
    
    # 2. 单位、文本和特殊符号
    content = re.sub(r'\\(mathrm|text|mbox)\{([^}]+)\}', r'\2', content)  # 各种文本命令
    content = re.sub(r'\\%', '%', content)                                # 百分号
    content = re.sub(r'\{\%\}', '%', content)                             # {\%}变体
    content = re.sub(r'\\degree', '°', content)                           # 度数符号
    content = re.sub(r'\^{\s*\\circ\s*}', '°', content)                   # ^{\circ}
    
    # 3. 希腊字母（完整集合）
    greek = {
        r'\\alpha': 'α', r'\\beta': 'β', r'\\gamma': 'γ', r'\\delta': 'δ',
        r'\\epsilon': 'ε', r'\\zeta': 'ζ', r'\\eta': 'η', r'\\theta': 'θ',
        r'\\kappa': 'κ', r'\\lambda': 'λ', r'\\mu': 'μ', r'\\nu': 'ν',
        r'\\xi': 'ξ', r'\\pi': 'π', r'\\rho': 'ρ', r'\\sigma': 'σ',
        r'\\tau': 'τ', r'\\phi': 'φ', r'\\chi': 'χ', r'\\psi': 'ψ',
        r'\\omega': 'ω', r'\\Gamma': 'Γ', r'\\Delta': 'Δ', r'\\Theta': 'Θ',
        r'\\Lambda': 'Λ', r'\\Sigma': 'Σ', r'\\Omega': 'Ω'
    }
    for latex, uni in greek.items():
        content = content.replace(latex, uni)
    
    # 4. 数学运算符和符号
    operators = {
        r'\\times': '×', r'\\div': '÷', r'\\cdot': '·', r'\\pm': '±', 
        r'\\mp': '∓', r'\\leq': '≤', r'\\geq': '≥', r'\\neq': '≠',
        r'\\approx': '≈', r'\\equiv': '≡', r'\\propto': '∝', r'\\in': '∈',
        r'\\subset': '⊂', r'\\rightarrow': '→', r'\\Rightarrow': '⇒',
        r'\\Leftrightarrow': '⇔', r'\\mapsto': '↦', r'\\partial': '∂',
        r'\\nabla': '∇', r'\\infty': '∞', r'\\forall': '∀', r'\\exists': '∃',
        r'\\emptyset': '∅', r'\\lceil': '⌈', r'\\rceil': '⌉', r'\\lfloor': '⌊',
        r'\\rfloor': '⌋', r'\\langle': '⟨', r'\\rangle': '⟩', r'\\ldots': '…',
        r'\\cdots': '⋯', r'\\vdots': '⋮', r'\\ddots': '⋱'
    }
    for latex, uni in operators.items():
        content = content.replace(latex, uni)
    
    # 5. 分数、根式和积分
    content = re.sub(r'\\[dv]?frac\{([^}]+)\}\{([^}]+)\}', r'\1/\2', content)
    content = re.sub(r'\\sqrt\{([^}]+)\}', r'√\1', content)
    content = re.sub(r'\\sqrt\[([^\]]+)\]\{([^}]+)\}', r'\1√\2', content)
    content = re.sub(r'\\int(?:_\{[^}]+\}\^\{[^}]+\}|)', '∫', content)
    content = re.sub(r'\\sum(?:_\{[^}]+\}\^\{[^}]+\}|)', 'Σ', content)
    content = re.sub(r'\\prod(?:_\{[^}]+\}\^\{[^}]+\}|)', '∏', content)
    
    # 6. 上下标处理（支持嵌套）
    def process_sup_sub(match):
        return match.group(1) + (match.group(3) or match.group(2))
    
    content = re.sub(r'(_|\^)(\{([^{}]+)\}|([^{}\s]))', process_sup_sub, content)
    
    # 7. 向量、矩阵和数组
    content = re.sub(r'\\[bv]ec\{([^}]+)\}', r'\1', content)
    content = re.sub(
        r'\\begin\{(pmatrix|bmatrix|matrix|array)\}.*?\\end\{\1\}',
        lambda m: re.sub(r'\s*&\s*', ',', m.group(0).replace('\\\\', ';')),
        content,
        flags=re.DOTALL
    )
    
    # 8. 括号和定界符
    content = re.sub(r'\\left([([{}<|])', r'\1', content)
    content = re.sub(r'\\right([)\]}>|])', r'\1', content)
    content = re.sub(r'\\[lr]vert', '|', content)
    
    # 恢复所有被保护的非数学内容
    for i, block in enumerate(protected_blocks):
        content = content.replace(f'@@PROTECTED_BLOCK_{i}@@', block)
    
    return content

def process_files(input_dir, output_dir=None):
    """
    处理Markdown文件
    :param input_dir: 输入目录
    :param output_dir: 输出目录（None时覆盖原文件）
    """
    processed_files = 0
    log_entries = []
    
    for filepath in Path(input_dir).rglob('*.md'):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            new_content = convert_all_math(content)
            
            if output_dir:
                relative_path = filepath.relative_to(input_dir)
                output_path = Path(output_dir) / relative_path
                os.makedirs(output_path.parent, exist_ok=True)
            else:
                output_path = filepath
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            log_entries.append(f"成功处理: {filepath} → {output_path}")
            processed_files += 1
            
        except Exception as e:
            log_entries.append(f"处理失败: {filepath} - {str(e)}")
    
    # 写入日志
    log_content = f"LaTeX公式转换日志 - {datetime.now()}\n\n"
    log_content += f"共处理文件: {processed_files}个\n"
    log_content += "\n".join(log_entries)
    
    log_path = Path(output_dir if output_dir else input_dir) / "math_conversion_log.txt"
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write(log_content)
    
    return processed_files

if __name__ == '__main__':
    input_dir = input("请输入要处理的目录路径（留空为当前目录）: ").strip() or '.'
    output_dir = input("请输入输出目录路径（留空则覆盖原文件）: ").strip() or None
    
    print(f"\n开始处理: {input_dir}")
    if output_dir:
        print(f"修改后的文件将保存到: {output_dir}")
    else:
        print("警告: 将直接覆盖原文件！")
    
    confirm = input("确认继续？(y/n): ").strip().lower()
    if confirm == 'y':
        processed_count = process_files(input_dir, output_dir)
        print(f"\n处理完成！共转换 {processed_count} 个文件")
        print(f"日志已保存到: {output_dir if output_dir else input_dir}/math_conversion_log.txt")
    else:
        print("操作已取消")