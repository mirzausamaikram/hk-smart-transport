import os
import re
from pathlib import Path

def remove_python_comments(content):
    lines = content.split('\n')
    result = []
    in_docstring = False
    docstring_char = None
    
    for line in lines:
        stripped = line.lstrip()
        
        if '"""' in stripped or "'''" in stripped:
            if not in_docstring:
                in_docstring = True
                docstring_char = '"""' if '"""' in stripped else "'''"
                result.append(line)
            elif docstring_char in stripped:
                in_docstring = False
                result.append(line)
            else:
                result.append(line)
            continue
        
        if in_docstring:
            result.append(line)
            continue
        
        if stripped.startswith('#'):
            if stripped.startswith('#!'):
                result.append(line)
            continue
        
        if '#' in line:
            code_part = line.split('#')[0]
            if code_part.strip():
                result.append(code_part.rstrip())
            continue
        
        result.append(line)
    
    return '\n'.join(result)

def remove_js_ts_comments(content):
    content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    
    lines = [line.rstrip() for line in content.split('\n')]
    return '\n'.join(lines)

def remove_svelte_comments(content):
    content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
    content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    
    lines = [line.rstrip() for line in content.split('\n')]
    return '\n'.join(lines)

def process_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_size = len(content)
    
    if file_path.endswith('.py'):
        new_content = remove_python_comments(content)
    elif file_path.endswith(('.ts', '.js')):
        new_content = remove_js_ts_comments(content)
    elif file_path.endswith('.svelte'):
        new_content = remove_svelte_comments(content)
    else:
        return False
    
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✓ {file_path} ({original_size} -> {len(new_content)} bytes)")
        return True
    return False

def main():
    project_root = Path(__file__).parent
    
    target_dirs = [
        project_root / 'backend' / 'routers',
        project_root / 'frontend' / 'src' / 'routes',
        project_root / 'frontend' / 'src' / 'lib' / 'components'
    ]
    
    target_files = [
        project_root / 'backend' / 'main.py'
    ]
    
    extensions = ['.py', '.ts', '.js', '.svelte']
    
    modified_count = 0
    
    for target_dir in target_dirs:
        if target_dir.exists():
            for file_path in target_dir.rglob('*'):
                if file_path.is_file() and file_path.suffix in extensions:
                    if process_file(str(file_path)):
                        modified_count += 1
    
    for file_path in target_files:
        if file_path.exists():
            if process_file(str(file_path)):
                modified_count += 1
    
    print(f"\nModified {modified_count} files")

if __name__ == '__main__':
    main()
