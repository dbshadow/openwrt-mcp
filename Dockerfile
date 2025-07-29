# 使用官方 Python 映像檔作為基礎
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 將相依套件檔案複製到工作目錄
COPY requirements.txt requirements.txt

# 在單一 RUN 指令中完成安裝與執行
# 1. 更新套件列表並安裝 curl
# 2. 下載並執行 uv 安裝腳本
# 3. 使用 uv 的正確絕對路徑並加上 --system 參數安裝 Python 相依套件
RUN apt-get update && apt-get install -y curl && \
    curl -LsSf https://astral.sh/uv/install.sh | sh && \
    /root/.local/bin/uv pip install --no-cache --system -r requirements.txt

# 將您的應用程式程式碼複製到工作目錄
COPY openwrt.py .

# 開放您應用程式運行的 port
EXPOSE 8181

# 設定容器啟動時執行的命令
CMD ["python", "./openwrt.py"]