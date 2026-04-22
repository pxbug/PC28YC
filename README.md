# PC28 预测

这是一个基于 Python 3.9.6 开发的PC28项目，专门设计用于在宝塔 Linux 面板上部署。

## 环境要求

- Python 3.9.6
- 宝塔 Linux 面板

## 安装步骤

1. 确保已安装 Python 3.9.6
```bash
python3 --version
```

2. 创建并激活虚拟环境
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 运行应用
```bash
python3 app.py
```

## 宝塔面板部署说明

1. 在宝塔面板中添加网站
2. 设置网站运行目录为项目根目录
3. 配置Python项目
   - 项目路径：/path/to/pc28
   - 启动文件：app.py
   - 运行命令：python app.py

## 访问项目

启动后访问：http://localhost:5000 

python3 app.py
