# 丰巢快递助手

![丰巢快递助手](https://img.shields.io/badge/版本-1.0.0-blue)
![AI辅助开发](https://img.shields.io/badge/AI辅助开发-Claude_3.7-purple)
![开发时间](https://img.shields.io/badge/开发周期-2天-green)
![python](https://img.shields.io/badge/版本-3.13.0-blue)

这是一个基于Vue和FastAPI开发的丰巢快递查询和开箱助手，帮助用户快速查看、管理和取出快递。
项目地址： [点我传送](https://github.com/telegramtool/fengchao) 

## 示例图

![image](https://github.com/user-attachments/assets/a7e8dc7b-b915-4d11-ac6d-4a20f9dd3303)
![image](https://github.com/user-attachments/assets/96427567-baf2-407f-b136-449e45165029)
![image](https://github.com/user-attachments/assets/f6340763-c7cf-4055-a1de-78de30c8a288)
![image](https://github.com/user-attachments/assets/3ab373e5-7d3c-4e46-9763-5c02cfe433ae)

## 作者
有问题可以在issue进行交流
### 联系
如若侵权 或 项目开发 请联系微信：lpsssk
![102487ced4cadfcf7709b2f0a068119c](https://github.com/user-attachments/assets/c676f28a-cc43-4521-8dbc-4352fcaa017c)
### 打赏
支付宝：![image](https://github.com/user-attachments/assets/2005d2c0-14fc-4c97-8ada-40dc7514b47d)

## 技术栈

### 后端

- Python FastAPI  [python版本可向下兼容 开发环境为3.13.0版本]
- 使用 RESTful API 设计
- 加密方式: RSA + MD5 + Base64
- Uvicorn 异步服务器

### 前端

- Vue.js 3
- Vuex 4 状态管理
- Vue Router 4 路由
- Vite 构建工具
- 响应式设计
- 支持亮色/暗色主题切换

## 功能特点

- 📱 手机验证码登录，无需记住复杂密码
- 📦 查看待取快递和已取快递列表
- 🔍 直观展示快递存放位置和柜机可视化布局
- 🚪 一键开箱取件，无需手动输入取件码
- 🌓 支持亮色/暗色主题切换，舒适的用户体验
- 💫 现代化UI设计，平滑动画和光感效果
- 🔄 下拉刷新和加载更多功能，流畅的用户体验

## AI辅助开发说明

本项目在短短两天的空闲时间内完成，主要通过AI辅助加速开发流程：

- 界面设计和交互逻辑由AI辅助完成
- 前后端API接口和数据流设计
- 响应式布局和主题切换功能
- 部分复杂算法和数据处理逻辑

## 使用教程

### 安装运行

1. 克隆仓库

```bash
git clone https://github.com/telegramtool/fengchao.git
cd fengchao
```

2. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

3. 安装前端依赖

```bash
cd frontend
npm install
```

4. 运行后端服务

```bash
cd backend
python app.py
```

或者直接使用 uvicorn:

```bash
uvicorn app:app --host 0.0.0.0 --port 5000 --reload
```

5. 运行前端开发服务器

```bash
cd frontend
npm run dev
```

6. 在浏览器中访问: <http://localhost:3000>

### 使用方法

1. 在登录页面输入您的手机号码并获取验证码
2. 输入收到的验证码完成登录
3. 在主页查看您的待取快递和已取快递
4. 点击任意快递卡片可查看详细的柜机位置信息
5. 点击"打开柜门"按钮可直接远程开箱取件
6. 使用右上角的主题切换按钮可以切换暗色/亮色模式

## API 文档

FastAPI 自动生成的 API 文档可以在以下地址访问:

- Swagger UI: <http://localhost:5000/docs>
- ReDoc: <http://localhost:5000/redoc>

### 主要 API

#### 发送验证码

- 请求: POST /send_verification_code
- 参数: phoneNumber, sliderTicket(可选), sliderRandstr(可选),同ip发送太多会需要腾讯验证码
- 返回: 验证参数和状态信息

#### 登录验证

- 请求: POST /login
- 参数: phoneNumber, verificationCode, rsaPublicKey, clientIp, requestCode, timestamp
- 返回: 登录状态和授权信息

#### 获取已取订单

- 请求: GET /completed_orders
- 头信息: Authorization
- 返回: 已取订单列表

#### 获取待取订单

- 请求: GET /pending_orders
- 头信息: Authorization
- 返回: 待取订单列表

## 打包部署教程

### 前端打包

1. 修改前端环境变量（如果需要）

```bash
# 在frontend/.env文件中设置API地址
VITE_API_URL=http://your-api-domain.com
```

2. 构建前端应用

```bash
cd frontend
npm run build
```

3. 构建完成后，dist目录包含所有静态资源文件

### 后端打包

1. 使用PyInstaller打包（Windows）

```bash
pip install pyinstaller
cd backend
pyinstaller --onefile app.py
```

2. 使用Docker容器化（推荐）

```bash
# 在backend目录创建Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]
```

```bash
cd backend
docker build -t fengchao-backend .
docker run -d -p 5000:5000 fengchao-backend
```

## 服务器部署教程

### Nginx + uWSGI + FastAPI 部署

1. 安装必要工具

```bash
sudo apt update
sudo apt install nginx python3-pip python3-dev
pip install uwsgi
```

2. 配置Nginx

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        root /path/to/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        include uwsgi_params;
        uwsgi_pass unix:/tmp/fengchao.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

3. 配置uWSGI

```ini
[uwsgi]
socket = /tmp/fengchao.sock
chmod-socket = 666
chdir = /path/to/backend
module = app:app
master = true
processes = 4
vacuum = true
die-on-term = true
```

4. 启动服务

```bash
uwsgi --ini uwsgi.ini &
sudo systemctl restart nginx
```

## 用途

- 个人用户: 快速查看和管理丰巢快递，无需手动输入验证码
- 快递员: 可以协助客户远程开箱，提高派件效率
- 社区服务: 可为老人、行动不便人士提供远程取件帮助
- 企业应用: 可集成至企业内部系统，管理公司收发的快递

## 注意事项

- 本应用需要配合丰巢账号使用
- 开箱功能需要距离箱体一定范围内才能操作
- 请遵守相关法律法规，不得用于非法用途
- 账号安全自行负责，建议不要共享账号信息

## 许可证

MIT License

---

*本项目为个人学习与使用目的开发，与丰巢官方无关。*  
*通过AI辅助开发，在短短两天内从零到一完成全栈应用。*  
*此文档也是AI生成的，如若侵权请联系微信:lpsssk。*
