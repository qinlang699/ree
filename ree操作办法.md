# Real-ESRGAN 操作指南

## 一、简介

Real-ESRGAN 是一个用于图像超分辨率的开源工具，它通过人工智能技术将低分辨率图像提升为高分辨率图像，同时保持良好的视觉质量。该工具由腾讯ARC实验室和中国科学院深圳先进技术研究院联合开发。

Real-ESRGAN 相比于传统的 ESRGAN，在处理真实世界图像时表现更佳，能够有效去除噪点、压缩伪影，并产生更自然的纹理细节。

## 二、模型说明

目前我们已下载的模型包括：

1. **RealESRGAN_x4plus.pth** (64MB) - 通用模型，放大4倍
2. **RealESRGAN_x2plus.pth** (64MB) - 通用模型，放大2倍
3. **realesr-general-x4v3.pth** (4.7MB) - 通用小型模型，放大4倍，第三版
4. **RealESRGAN_x4plus_anime_6B.pth** (17MB) - 动漫图像专用模型，放大4倍
5. **realesr-animevideov3.pth** (2.4MB) - 动漫视频专用模型，放大4倍

这些模型各有特点：
- **x4plus**: 通用场景的高质量放大，细节还原较好
- **x2plus**: 适合轻度放大，保持原图风格
- **general-x4v3**: 体积小，适合快速处理，支持降噪强度调整
- **x4plus_anime_6B**: 专为动漫图像优化，保持线条清晰
- **animevideov3**: 专为动漫视频优化，保持帧间一致性

## 三、使用方法

### 3.1 基础命令

使用 Real-ESRGAN 的基本命令格式为：

```bash
# Windows环境下推荐用法
python inference_realesrgan.py -n 模型名称 -i 输入图片/文件夹 -o 输出文件夹 [其他选项]
```

常用选项说明：
- `-n, --model_name`: 指定使用的模型名称
- `-i, --input`: 输入图片或文件夹路径（在Windows中推荐使用正斜杠"/"而非反斜杠"\"）
- `-o, --output`: 输出文件夹路径（不指定时默认为"results"）
- `-s, --outscale`: 最终输出的放大倍数，默认为4
- `--face_enhance`: 是否使用GFPGAN增强面部
- `--fp32`: 使用FP32精度进行推理（默认使用FP16半精度）
- `-t, --tile`: 分块大小，0表示不分块处理
- `--ext`: 输出图像格式，可选auto|jpg|png

### 3.2 处理普通照片

使用通用模型处理普通照片：

```bash
# 通用方式
python inference_realesrgan.py -n RealESRGAN_x4plus -i inputs/your_image.jpg -o results

# 推荐方式
python inference_realesrgan.py -n RealESRGAN_x4plus -i inputs/your_image.jpg --fp32
```

如果需要增强人脸，可以添加 `--face_enhance` 参数：

```bash
python inference_realesrgan.py -n RealESRGAN_x4plus -i inputs/your_image.jpg -o results --face_enhance --fp32
```

### 3.3 处理动漫图像

使用动漫专用模型处理动漫图像：

```bash
python inference_realesrgan.py -n RealESRGAN_x4plus_anime_6B -i inputs/0030.jpg -o results --fp32
```

### 3.4 处理视频

处理普通视频：

```bash
python inference_realesrgan_video.py -n RealESRGAN_x4plus -i inputs/your_video.mp4 -o results/output_video.mp4 --fp32
```

处理动漫视频：

```bash
python inference_realesrgan_video.py -n realesr-animevideov3 -i inputs/your_anime_video.mp4 -o results/output_video.mp4 --fp32
```

### 3.5 调整放大倍数

可以使用 `--outscale` 参数调整最终输出的放大倍数：

```bash
python inference_realesrgan.py -n RealESRGAN_x4plus -i inputs/your_image.jpg -o results --outscale 2.5 --fp32
```

这将使用x4plus模型处理，但最终输出为原图的2.5倍大小。

### 3.6 使用小型模型并调整降噪强度

对于 `realesr-general-x4v3` 模型，可以使用 `-dn` 参数调整降噪强度：

```bash
python inference_realesrgan.py -n realesr-general-x4v3 -i inputs/your_image.jpg -o results -dn 0.5 --fp32
```

降噪强度范围为0-1，0表示弱降噪（保留更多细节和噪点），1表示强降噪（更平滑的结果）。

## 四、常见问题与解决方案

1. **内存不足错误 (包括 `Memory allocation failure`)**
   - **原因**: 通常是由于同时处理的任务过多，耗尽了显存(VRAM)或系统内存(RAM)。特别是在处理视频时，`--num_process_per_gpu` 参数设置过高是主要原因。
   - **解决方案**:
       - 降低视频处理的并发数，例如，将 `--num_process_per_gpu` 设置为 `1` 或 `2` 再尝试。
       - 对于图片处理，可尝试使用 `-t` 参数设置分块处理，例如 `-t 512`。
       - 减小输入图像/视频的尺寸或使用更小的模型。

2. **CUDA 错误 (包括 `Torch not compiled with CUDA enabled`)**
   - **原因**:
       - `AssertionError: Torch not compiled with CUDA enabled`: 这表示您安装的PyTorch是"纯CPU"版本，无法使用NVIDIA显卡。
       - 其他CUDA错误：可能是显卡驱动版本过旧。
   - **解决方案**:
       - 若要使用GPU加速，必须安装支持CUDA的PyTorch版本。请参考第7点的"库版本冲突"解决方案来安装正确的版本。
       - 更新您的NVIDIA显卡驱动到最新版。
       - 添加 `--fp32` 参数可提高稳定性。

3. **处理速度慢**
   - 使用体积更小的模型，如 `realesr-general-x4v3`
   - 减小输入图像尺寸
   - 使用功能更强的GPU

4. **结果过于平滑/锐化**
   - 对于过于平滑的结果，使用 `-dn 0` 减弱降噪
   - 对于过于锐化的结果，可以尝试其他模型或后期调整

5. **面部不自然**
   - 添加 `--face_enhance` 参数增强面部

6. **Windows系统特定问题**
   - 使用正斜杠"/"替代反斜杠"\"作为路径分隔符
   - 如果未将Python添加至系统Path，建议使用 `py -3.9` 明确指定Python版本
   - 添加 `--fp32` 参数提高稳定性

7. **依赖库版本冲突 (如 `ModuleNotFoundError`)**
   - **原因**: 本项目依赖于特定版本的Python库。如果安装了过新或不兼容的库（特别是`torch`, `torchvision`, `basicsr`），会导致`ModuleNotFoundError`之类的错误。
   - **解决方案**: 强烈建议使用一个经过验证的、稳定的依赖版本组合。可使用以下命令一次性安装所有兼容的库（在执行前建议先卸载已有版本）：
       ```bash
       # 卸载命令 (可选，但推荐)
       pip uninstall basicsr facexlib gfpgan numpy opencv-python Pillow torch torchvision tqdm -y
       # 安装兼容版本命令 (推荐使用此组合以发挥NVIDIA显卡性能)
       pip install basicsr==1.4.2 facexlib==0.3.0 gfpgan==1.3.8 numpy==1.23.5 opencv-python==4.9.0.80 Pillow==9.5.0 torch==1.12.1+cu113 torchvision==0.13.1+cu113 torchaudio==0.12.1 --extra-index-url https://download.pytorch.org/whl/cu113
       ```
   - **注意**: `+cu113` 表示这个PyTorch版本支持CUDA 11.3，能够利用NVIDIA显卡进行加速，对RTX 20、30、40系显卡均有良好兼容性。

8. **找不到 FFmpeg (`FileNotFoundError`)**
   - **原因**: 在处理视频时，程序需要`ffmpeg.exe`来解码和编码，但没有在系统中找到它。
   - **解决方案**:
       1. 下载 FFmpeg：从 [gyan.dev/ffmpeg/builds/](https://www.gyan.dev/ffmpeg/builds/) 下载 `ffmpeg-release-full.7z`。
       2. 解压并放置：解压后，将文件夹放到一个固定位置，例如 `C:\ffmpeg`。
       3. 添加至环境变量：将 `C:\ffmpeg\bin` 添加到系统的 `Path` 环境变量中。

## 五、实际操作示例

### 示例1：处理单张照片（Windows环境）

```bash
python inference_realesrgan.py -n RealESRGAN_x4plus -i inputs/0014.jpg --fp32
```

### 示例2：处理单张照片并增强面部

```bash
python inference_realesrgan.py -n RealESRGAN_x4plus -i inputs/00017_gray.png -o results --face_enhance --fp32
```

### 示例3：处理整个文件夹的动漫图片

```bash
python inference_realesrgan.py -n RealESRGAN_x4plus_anime_6B -i inputs/ -o results/anime_results --fp32
```

### 示例4：处理视频并调整放大倍数

```bash
# --num_process_per_gpu 参数可调整并发数，建议从1开始尝试，根据显存大小适当增加
python inference_realesrgan_video.py -n realesr-animevideov3 -i inputs/video/onepiece_demo.mp4 -o results/onepiece_upscaled.mp4 --outscale 2 --fp32 --num_process_per_gpu 2
```

### 示例5：批量处理并保存为PNG格式

```bash
python inference_realesrgan.py -n RealESRGAN_x4plus -i inputs/ -o results --ext png --fp32
```

## 六、注意事项

1. **依赖安装**: 首次运行前，请务必根据"常见问题与解决方案"第7点的指导，安装兼容的依赖库版本，这是避免各类错误的最佳实践。
2. **GPU内存**: 对于大型图像或视频，确保有足够的GPU内存。视频处理时，请从 `--num_process_per_gpu 1` 开始尝试，避免内存分配失败。
3. **Python环境**:
   - 为了方便直接使用 `python` 和 `pip` 命令，建议将Python的安装路径（如 `F:\VS2\Python39_64`）及其下的 `Scripts` 文件夹添加到系统的 `Path` 环境变量中。
   - 如果未配置系统Path，在Windows系统中，建议使用`py -3.9`指定Python版本并添加`--fp32`参数以提高稳定性。
4. **FFmpeg依赖**: 处理视频时，需要正确安装FFmpeg并将其添加到系统`Path`环境变量，详情请参考"常见问题与解决方案"第8点。
5. **模型选择**: 不同模型适用于不同类型的图像，请根据实际需求选择。
6. **路径格式**: 在Windows系统中使用正斜杠`/`而非反斜杠`\`可以避免许多路径问题。

通过以上指南，您应该能够顺利使用Real-ESRGAN处理各种图像和视频。如有更多问题，请参考[官方GitHub仓库](https://github.com/xinntao/Real-ESRGAN)获取最新信息。
