import customtkinter as ctk
import tkinter
from tkinter import filedialog, messagebox
import os
import subprocess
import threading


class RealESRGAN_GUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Real-ESRGAN 智能可视化工具")
        self.geometry("850x650")

        # --- 数据映射 ---
        self.model_map = {
            "通用模型 (x4)": "RealESRGAN_x4plus",
            "通用模型 (x2)": "RealESRGAN_x2plus",
            "通用小型模型 (可降噪)": "realesr-general-x4v3",
            "动漫图片模型": "RealESRGAN_x4plus_anime_6B",
            "动漫视频模型": "realesr-animevideov3"
        }

        # --- 设置布局 ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # --- 输入/输出 框架 ---
        self.io_frame = ctk.CTkFrame(self)
        self.io_frame.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="ew")
        self.io_frame.grid_columnconfigure(1, weight=1)

        # 输入路径
        self.input_label = ctk.CTkLabel(self.io_frame, text="输入路径:")
        self.input_label.grid(row=0, column=0, padx=(20, 10), pady=10, sticky="w")
        self.input_entry = ctk.CTkEntry(self.io_frame, placeholder_text="选择图片、视频或文件夹...")
        self.input_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.input_button = ctk.CTkButton(self.io_frame, text="浏览...", width=100, command=self.select_input_path)
        self.input_button.grid(row=0, column=2, padx=(10, 20), pady=10)

        # 输出路径
        self.output_label = ctk.CTkLabel(self.io_frame, text="输出路径:")
        self.output_label.grid(row=1, column=0, padx=(20, 10), pady=10, sticky="w")
        self.output_entry = ctk.CTkEntry(self.io_frame, placeholder_text="选择一个根目录用于保存...")
        self.output_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        self.output_button = ctk.CTkButton(self.io_frame, text="浏览...", width=100, command=self.select_output_path)
        self.output_button.grid(row=1, column=2, padx=(10, 20), pady=10)

        # --- 选项 框架 ---
        self.options_frame = ctk.CTkFrame(self)
        self.options_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ns")
        self.options_label = ctk.CTkLabel(self.options_frame, text="核心选项", font=ctk.CTkFont(size=14, weight="bold"))
        self.options_label.grid(row=0, column=0, padx=20, pady=(10, 5))

        # 模型选择
        self.model_label = ctk.CTkLabel(self.options_frame, text="AI模型:")
        self.model_label.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="w")
        self.model_menu = ctk.CTkOptionMenu(
            self.options_frame, values=list(self.model_map.keys()), command=self.update_ui_for_model)
        self.model_menu.grid(row=2, column=0, padx=20, pady=(5, 10))

        # 放大倍数
        self.outscale_label = ctk.CTkLabel(self.options_frame, text="放大倍数:")
        self.outscale_label.grid(row=3, column=0, padx=20, pady=(10, 0), sticky="w")
        self.outscale_entry = ctk.CTkEntry(self.options_frame, placeholder_text="默认自动")
        self.outscale_entry.grid(row=4, column=0, padx=20, pady=(5, 10))

        # 人脸增强
        self.face_enhance_check = ctk.CTkCheckBox(self.options_frame, text="人脸增强 (非动漫模型)")
        self.face_enhance_check.grid(row=5, column=0, padx=20, pady=10)

        # --- 动态参数 框架 ---
        self.dynamic_frame = ctk.CTkFrame(self)
        self.dynamic_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.dynamic_label = ctk.CTkLabel(self.dynamic_frame, text="动态参数", font=ctk.CTkFont(size=14, weight="bold"))
        self.dynamic_label.grid(row=0, column=0, padx=20, pady=(10, 5))

        # 降噪强度 (realesr-general-x4v3)
        self.dn_label = ctk.CTkLabel(self.dynamic_frame, text="降噪强度 (0-1):")
        self.dn_slider_val = ctk.CTkLabel(self.dynamic_frame, text="0.5")
        self.dn_slider = ctk.CTkSlider(
            self.dynamic_frame, from_=0, to=1, number_of_steps=100, command=lambda val: self.dn_slider_val.configure(
                text=f"{val:.2f}"))
        self.dn_slider.set(0.5)

        # 视频处理并发数 (realesr-animevideov3)
        self.num_process_label = ctk.CTkLabel(self.dynamic_frame, text="视频处理并发数:")
        self.num_process_entry = ctk.CTkEntry(self.dynamic_frame)
        self.num_process_entry.insert(0, "2")

        # 图片输出格式 (非视频模型)
        self.ext_label = ctk.CTkLabel(self.dynamic_frame, text="图片输出格式:")
        self.ext_menu = ctk.CTkOptionMenu(self.dynamic_frame, values=["auto", "png", "jpg"])

        # --- 日志和执行 框架 ---
        self.run_log_frame = ctk.CTkFrame(self)
        self.run_log_frame.grid(row=1, column=1, rowspan=3, padx=(10, 20), pady=10, sticky="nsew")
        self.run_log_frame.grid_rowconfigure(1, weight=1)
        self.run_log_frame.grid_columnconfigure(0, weight=1)

        self.run_button = ctk.CTkButton(
            self.run_log_frame, text="开始处理", font=ctk.CTkFont(size=14, weight="bold"),
            command=self.start_processing_thread)
        self.run_button.grid(row=0, column=0, padx=20, pady=10)
        self.log_textbox = ctk.CTkTextbox(self.run_log_frame, state="disabled", wrap="word")
        self.log_textbox.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")

        # 初始化UI
        self.update_ui_for_model(self.model_menu.get())

    def update_ui_for_model(self, selected_display_name):
        model_name = self.model_map[selected_display_name]

        # Hide all dynamic widgets first
        for widget in [self.dn_label, self.dn_slider, self.dn_slider_val, self.num_process_label,
                       self.num_process_entry, self.ext_label, self.ext_menu]:
            widget.grid_forget()

        # Show relevant widgets based on model
        if model_name == 'realesr-general-x4v3':
            self.dn_label.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="w")
            self.dn_slider.grid(row=2, column=0, padx=20, pady=5, sticky="ew")
            self.dn_slider_val.grid(row=2, column=1, padx=(0, 20), pady=5)

        if model_name == 'realesr-animevideov3':
            self.num_process_label.grid(row=3, column=0, padx=20, pady=(10, 0), sticky="w")
            self.num_process_entry.grid(row=4, column=0, padx=20, pady=5, sticky="ew")
        else:  # All other models are for images
            self.ext_label.grid(row=5, column=0, padx=20, pady=(10, 0), sticky="w")
            self.ext_menu.grid(row=6, column=0, padx=20, pady=5, sticky="ew")

        # Disable face enhance for anime models
        if 'anime' in model_name:
            self.face_enhance_check.deselect()
            self.face_enhance_check.configure(state="disabled")
        else:
            self.face_enhance_check.configure(state="normal")

    def select_input_path(self):
        # Allow selecting a file or a directory
        # For simplicity, we ask the user what they want to select first
        path_type = tkinter.messagebox.askquestion(
            "选择类型", "是否要选择一个文件夹？\n'是' - 选择文件夹\n'否' - 选择单个文件")
        if path_type == 'yes':
            path = filedialog.askdirectory()
        else:
            path = filedialog.askopenfilename()

        if path:
            self.input_entry.delete(0, "end")
            self.input_entry.insert(0, path)

    def select_output_path(self):
        path = filedialog.askdirectory()
        if path:
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, path)

    def log(self, message):
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", message + "\n")
        self.log_textbox.configure(state="disabled")
        self.log_textbox.see("end")

    def start_processing_thread(self):
        # Disable button to prevent multiple runs
        self.run_button.configure(state="disabled", text="处理中...")
        # Clear log
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.configure(state="disabled")

        thread = threading.Thread(target=self.process_images)
        thread.daemon = True
        thread.start()

    def process_images(self):
        try:
            # --- 1. Get all settings from UI ---
            input_path = self.input_entry.get()
            base_output_path = self.output_entry.get()
            model_display_name = self.model_menu.get()
            model_name = self.model_map[model_display_name]
            outscale = self.outscale_entry.get()

            if not input_path or not base_output_path:
                self.log("错误: 输入和输出根路径不能为空！")
                messagebox.showerror("错误", "输入和输出根路径不能为空！")
                return

            # --- 2. Determine script and output subfolder ---
            output_subfolder = ""
            is_video = any(input_path.lower().endswith(ext) for ext in ['.mp4', '.mkv', '.flv', '.mov', '.avi'])
            is_folder = os.path.isdir(input_path)

            if is_video:
                script_to_run = "inference_realesrgan_video.py"
                output_subfolder = "video_outscale"
            else:
                script_to_run = "inference_realesrgan.py"
                if is_folder:
                    if self.ext_menu.get() == 'png':
                        output_subfolder = "total_png"
                    else:
                        output_subfolder = "total_cant"
                else:  # single image
                    if self.face_enhance_check.get():
                        output_subfolder = "single_face"
                    else:
                        output_subfolder = "singlenor"

            final_output_path = os.path.join(base_output_path, output_subfolder)
            os.makedirs(final_output_path, exist_ok=True)
            self.log(f"结果将保存至: {final_output_path}")

            # --- 3. Construct the command dynamically ---
            command = ["python", script_to_run, "-n", model_name, "-i", input_path,
                       "-o", final_output_path, "--fp32"]

            if self.face_enhance_check.get() and self.face_enhance_check.cget('state') == 'normal':
                command.append("--face_enhance")

            if outscale and outscale.strip():
                command.extend(["-s", outscale])

            # Add dynamic parameters
            if model_name == 'realesr-general-x4v3':
                command.extend(["-dn", f"{self.dn_slider.get():.2f}"])

            if is_video:
                if self.num_process_entry.get().strip():
                    command.extend(["--num_process_per_gpu", self.num_process_entry.get()])
            else:  # Image or Folder
                if self.ext_menu.get() != "auto":
                    command.extend(["--ext", self.ext_menu.get()])

            # --- 4. Execute and Log ---
            self.log(f"执行命令: {' '.join(command)}")

            process = subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                encoding='utf-8', creationflags=subprocess.CREATE_NO_WINDOW)

            for line in iter(process.stdout.readline, ''):
                if line:
                    self.log(line.strip())

            process.wait()
            rc = process.poll()

            if rc == 0:
                self.log("\n处理完成！")
                messagebox.showinfo("成功", f"处理完成！\n结果已保存至: {final_output_path}")
            else:
                self.log(f"\n处理失败，返回码: {rc}")
                messagebox.showerror("失败", "处理失败，请查看日志获取详情。")

        except Exception as e:
            self.log(f"发生未知错误: {e}")
            messagebox.showerror("未知错误", f"发生未知错误: {e}")

        finally:
            self.run_button.configure(state="normal", text="开始处理")


if __name__ == "__main__":
    app = RealESRGAN_GUI()
    app.mainloop()
