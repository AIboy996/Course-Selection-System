FROM python:3.10-alpine3.17
ENV PYTHONUNBUFFERED 1
WORKDIR /xk
RUN python3 -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple django pymysql