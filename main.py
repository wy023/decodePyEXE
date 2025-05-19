import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
import shutil
import warnings

# 忽略 RuntimeWarning
warnings.filterwarnings("ignore", category=RuntimeWarning)

def select_and_process_exe():
    # 选择 .exe 文件
    exe_path = filedialog.askopenfilename(title="Select EXE File", filetypes=[("Executable files", "*.exe")])
    if not exe_path:
        messagebox.showerror("Error", "No EXE file selected!")
        return

    # 获取当前脚本的目录
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # 解包 .exe 文件
    temp_dir = os.path.join(script_dir, "extracted_files")
    os.makedirs(temp_dir, exist_ok=True)

    # 获取 pyinstxtractor.py 的绝对路径
    pyinstxtractor_path = os.path.join(script_dir, "pyinstxtractor.py")
    print(f"pyinstxtractor.py path: {pyinstxtractor_path}")

    try:
        # 调用 pyinstxtractor.py
        subprocess.run(["python", pyinstxtractor_path, exe_path], check=True, cwd=temp_dir)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Failed to unpack EXE file: {e}")
        return

    # 自动弹出窗口让用户选择 .pyc 文件
    select_and_convert_pyc(temp_dir)

def select_and_convert_pyc(temp_dir):
    # 弹出窗口让用户选择 .pyc 文件
    pyc_path = filedialog.askopenfilename(
        title="Select PYC File",
        filetypes=[("Python compiled files", "*.pyc")],
        initialdir=temp_dir
    )
    if not pyc_path:
        messagebox.showerror("Error", "No PYC file selected!")
        return

    # 确保 pyc_path 是绝对路径
    pyc_path = os.path.abspath(pyc_path)
    print(f"Selected PYC file path: {pyc_path}")

    # 确保输出目录存在
    output_dir = os.path.join(os.getcwd(), "output")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "output.py")
    print(f"Output file path: {output_file}")

    # 使用 xdis 检查 .pyc 文件的 Python 版本
    try:
        xdis_output = subprocess.run(
            ["python", "-m", "xdis.magics", pyc_path], 
            check=True, 
            capture_output=True, 
            text=True
        )
        print(f"xdis output:\n{xdis_output.stdout}")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Failed to run xdis on PYC file: {e}")
        return

    # 获取 uncompyle6 和 decompyle3 的绝对路径
    uncompyle6_path = shutil.which("uncompyle6")
    decompyle3_path = shutil.which("decompyle3")

    if uncompyle6_path is None:
        messagebox.showerror("Error", "uncompyle6 is not installed or not found in PATH")
        return
    print(f"uncompyle6 path: {uncompyle6_path}")

    if decompyle3_path is None:
        messagebox.showerror("Error", "decompyle3 is not installed or not found in PATH")
        return
    print(f"decompyle3 path: {decompyle3_path}")

    # 尝试使用 uncompyle6 转换 .pyc 文件
    try:
        subprocess.run([uncompyle6_path, pyc_path, "-o", output_dir], check=True)
        messagebox.showinfo("Success", f"PYC file has been converted to PY using uncompyle6 and saved as {output_file}")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Failed to convert PYC file using uncompyle6: {e}")
        # 如果 uncompyle6 失败，尝试使用 decompyle3
        try:
            subprocess.run([decompyle3_path, pyc_path, "-o", output_dir], check=True)
            messagebox.showinfo("Success", f"PYC file has been converted to PY using decompyle3 and saved as {output_file}")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to convert PYC file using decompyle3: {e}")

# 创建一个隐藏的主窗口
root = tk.Tk()
root.withdraw()

# 直接调用选择和处理函数
select_and_process_exe()