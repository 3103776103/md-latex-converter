# Markdown LaTeX 公式批量转换工具

🚀 自动扫描目录并转换所有Markdown文件中的LaTeX公式

=== 使用说明 ===

1. 基本命令格式：
   python convert.py [输入目录] [输出目录(可选)]

2. 使用示例：
   # 转换到新目录（推荐）
   python convert.py ./papers ./converted
   
   # 覆盖原目录（谨慎使用）
   python convert.py ./papers

3. 安全提示：
   ▶ 覆盖模式会直接修改原始文件
   ▶ 建议先备份重要文档
   ▶ 程序会自动创建.bak备份文件

=== 工作流程 ===
1. 扫描输入目录（包括子目录）
2. 查找所有.md文件
3. 转换LaTeX公式为纯文本格式
4. 根据参数保存到：
   - 指定输出目录（保留原目录结构）
   - 或覆盖原文件（添加.bak备份）

=== 参数详解 ===
必需参数：
  input_path  输入目录路径

可选参数：
  -o OUTPUT   输出目录路径
  --force     强制覆盖已存在文件
  --verbose   显示详细处理日志

=== 典型使用场景 ===
1. 转换论文合集：
   python convert.py ./PhD_papers ./converted_papers

2. 批量更新Wiki文档：
   python convert.py ./wiki --force

=== 注意事项 ===
✔ 支持递归处理子目录
✔ 自动跳过非Markdown文件
✔ 保留原始文件时间戳
✔ 转换日志保存在convert.log

=== 错误处理 ===
遇到错误时会：
1. 跳过当前文件继续处理
2. 在终端显示警告
3. 记录到error_log.txt
4. 保持原文件不变

（使用前请确保已安装Python 3.8+和所需依赖包）
