# CS3611-Final-Project

这里是上海交通大学CS3611课程的期末项目, 主要为流式视频传输系统设计与码率自适应优化。

## 环境配置

- Python 3.8+
- ffmpeg
- numpy
- pycryptodome 
- psutil
- matplotlib
- scikit-video
- VLC

提供了一个 `requirements.txt` 文件来帮助你安装所需的 Python 库。你可以使用以下命令来安装：

```bash
pip install -r requirements.txt
```

对于ffmpeg和VLC，你还需要额外的安装步骤。

### Windows

#### ffmpeg

1. 前往[ffmpeg官网](https://ffmpeg.org/download.html)下载 Windows Bulid (推荐使用 gyan.dev)
2. 解压后将 `bin\ffmpeg.exe` 所在路径添加到环境变量 `PATH` ；
3. 可在终端输入 `ffmpeg -version` 来检查是否安装成功。

#### VLC
1. 前往[VLC官网](https://www.videolan.org/vlc/)下载最新版本的 VLC 播放器；
2. 安装完成后，确保 VLC 的安装路径已添加到系统的环境变量中；
3. 可在终端输入 `vlc --version` 来检查是否安装成功。

### Ubuntu / Debian

在终端中使用以下命令安装

```bash
sudo apt update 
sudo apt install ffmpeg
sudo apt install vlc
```

6.1更新：更新了client这一块，目前会依次播放四种画质的视频，中间有难以忽视的间隙，而且若其中一个slider剪出了失败的ts文件(部分测试视频中出现问题)会产生大量垃圾信息。
且没有日志模块，日志和可视化界面这些的后面会做进去。大概这样。
你也应当在main分支中创建以下文件夹：
```data
data/raw
data/segments
data/download
data/logs
```
