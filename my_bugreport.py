import subprocess
import sys
import re
from datetime import timedelta
pairs = {}

def execute_commands(dates, input_file, output_file, num_context_lines):
    # 将日期参数转化为grep可以识别的格式
    dates_arg_list = ['-e ' + d for d in dates]

    # 执行第一个命令
    command1 = ['grep', '-A', num_context_lines, '-B', num_context_lines] + dates_arg_list + [input_file]
    with open(output_file, "w") as outfile:
        subprocess.run(command1, stdout=outfile, shell=False)

    # # 执行第二个命令
    # command2 = f"awk '/com\\.android\\.providers\\.media\\.module\\/com\\.android\\.providers\\.media\\.MediaProvider\\}} pid=/ {{p=1; print; next}} /PROVIDER/ && p {{exit}} p' {input_file}"
    # with open(output_file, "a") as outfile: # 注意这里是 "a" 而不是 "w"，以保证结果的追加而不是覆盖
    #     subprocess.run(command2, stdout=outfile, shell=True)


    A, B = read_config("rule2.txt")

    A_escaped = A.replace('.', '\\.').replace('/', '\\/').replace('{', '\\{').replace('}', '\\}')
    command2 = f"awk '/{A_escaped}/ {{p=1; print; next}} /{B}/ && p {{exit}} p' {input_file}"

    with open(output_file, "a") as outfile:
        subprocess.run(command2, stdout=outfile, shell=True) 

    # 从配置文件中读取键值对        
    with open('rule.txt', 'r') as f:
        for line in f:
            try:
                key, value = line.strip().split(':')
                pairs[key] = value
            except ValueError:
                pass  # 如果不能正确分割就跳过

    # 先将文件内容读入内存
    with open(output_file, 'r') as file_in:
        lines = file_in.readlines()

    # 进行替换操作
    for i in range(len(lines)):
        for key, value in pairs.items():
            lines[i] = lines[i].replace(key, value)
            # 进行时间替换操作
            lines[i] = replace_time_strings_in_file(lines[i])

    # 将处理过的内容写回文件
    with open(output_file, 'w') as file_out:
        for line in lines:
            file_out.write(line) 
             
    replace_time_strings_in_file(output_file)               
    
def read_config(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        A, B = lines[0].strip().split(":")
        return A, B            

#处理时间
def parse_time(time_str):  
    time_str = time_str.strip()

    day = 0
    hour = 0
    minute = 0
    second = 0
    ms = 0

    matches = re.findall(r'(-?\d+)(d|h|m|s|ms)', time_str)
    
    for val, unit in matches:
        val = int(val)
        if unit == 'd':
            day = val
        elif unit == 'h':
            hour = val
        elif unit == 'm':
            minute = val
        elif unit == 's':
            second = val
        elif unit == 'ms':
            ms = val  

    time_parts = []
    if day:
        time_parts.append(f'{day}天')
    if hour:
        time_parts.append(f'{hour}小时')
    if minute:
        time_parts.append(f'{minute}分钟')
    if second:
        time_parts.append(f'{second}秒')
    if ms:
        time_parts.append(f'{ms}毫秒')

    return ''.join(time_parts)

def replace_time_strings_in_file(line):
    regex = r"(-?\d+d|-?\d+h|-?\d+m|-?\d+s|-?\d+ms)"
    matches = re.findall(regex, line)
    
    for match_str in matches:
        time_length = parse_time(match_str)
        line = line.replace(match_str, str(time_length))
    line = re.sub(r'(\d+)分钟s', r'\1毫秒', line)
    return line             
            
            

if __name__ == "__main__":
    dates = sys.argv[1:-3]
    input_file = sys.argv[-3]
    output_file = sys.argv[-2]
    # 如果行数参数未输入，使用默认值
    if len(sys.argv) > 4:
        num_context_lines = sys.argv[-1]
    else:
        num_context_lines = '1'  # 默认值: 上下各一行

    execute_commands(dates, input_file, output_file, num_context_lines)