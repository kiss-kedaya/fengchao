from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import hashlib
import base64
from typing import Optional, Union
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import uvicorn
import time

app = FastAPI()

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class VerificationRequest(BaseModel):
    phoneNumber: str
    sliderTicket: Optional[str] = ""
    sliderRandstr: Optional[str] = ""


class LoginRequest(BaseModel):
    phoneNumber: str
    verificationCode: str
    rsaPublicKey: str
    clientIp: str
    requestCode: str
    timestamp: Union[str, int]  # 允许字符串或整数类型


class CabinetLocationRequest(BaseModel):
    expressId: str
    boxId: Optional[str] = None
    cabinetCode: Optional[str] = None


class OpenBoxRequest(BaseModel):
    cabinetCode: str
    boxId: str
    expressId: str
    clientMobile: str
    staffMobile: str
    companyLogoUrl: str
    companyName: str
    expressType: int
    postId: str
    code: str
    boxGlobalRow: str
    address: str


def format_rsa_key(key_data):
    """格式化RSA密钥为PEM格式"""
    # 去除可能的头尾部分
    key_data = key_data.strip()

    # 如果已经是PEM格式，直接返回
    if key_data.startswith("-----BEGIN"):
        return key_data

    # 否则添加PEM头尾
    return f"-----BEGIN PUBLIC KEY-----\n{key_data}\n-----END PUBLIC KEY-----"


def encrypt_with_rsa(data, key_string):
    """使用RSA公钥加密数据"""
    try:
        # 尝试标准PEM格式导入
        key = RSA.importKey(key_string)
    except ValueError:
        try:
            # 尝试格式化后再导入
            formatted_key = format_rsa_key(key_string)
            key = RSA.importKey(formatted_key)
        except Exception as e:
            # 如果还是失败，尝试直接使用base64解码的数据加密
            # 这是一个备选方案，因为原始代码可能使用了特殊方式处理公钥
            from cryptography.hazmat.primitives.asymmetric import padding
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.backends import default_backend

            try:
                # 尝试使用cryptography库
                key_bytes = base64.b64decode(key_string)
                public_key = serialization.load_der_public_key(
                    key_bytes, backend=default_backend()
                )
                encrypted = public_key.encrypt(data.encode(), padding.PKCS1v15())
                return encrypted
            except Exception:
                # 如果所有尝试都失败，记录详细错误并重新抛出原始异常
                print(f"无法解析RSA公钥: {key_string[:30]}...")
                raise e

    # 使用PKCS1_v1_5进行加密
    cipher = PKCS1_v1_5.new(key)
    return cipher.encrypt(data.encode())


@app.post("/send_verification_code")
async def send_verification_code(request: VerificationRequest):
    phone_number = request.phoneNumber

    # 第一步: 获取校验参数
    url = f"https://consumer.fcbox.com/v1/account/secureCheckMobile?mobile={phone_number}&type=11&opCode=30b2718363204beeae98b7d03a75c3a4&nationCode=86"
    headers = {
        "pinpoint-traceid": "ConsumerA^1742830234658^73",
        "User-Agent": "channel=xiaomi,ip=,os=15,deviceType=2211133C,platform=Android,resolution=1080*2296,versionCode=6007000,versionName=6.7.0,timestamp=1742830229382",
        "FC_USER_FLAG": "",
        "FC_USER_AUTH": "tZGbsbamQGx8PkFPQ1acmgWu3ZW88nQsfdlMl2ZhxWs=",
        "pinpoint-spanid": "1",
        "pinpoint-sampled": "true",
        "pinpoint-pspanid": "-1",
        "Host": "consumer.fcbox.com",
        "Connection": "Keep-Alive",
    }

    response = requests.get(url, headers=headers)
    result = response.json()

    # 打印关键信息用于调试
    print(f"获取到的响应: {result}")

    # 提取参数
    key_order = result["data"]["keyOrder"].split(",")
    rsa_public_key = ""
    for i in range(1, 6):
        rsa_public_key += result["data"][f"key{key_order[i - 1]}"]

    print(f"构建的RSA公钥: {rsa_public_key[:30]}...")

    client_ip = result["data"]["clientIp"]
    request_code = result["data"]["requestCode"]
    timestamp = result["data"]["timestamp"]
    need_slider_code = result["data"].get("needSliderCode") == "true"

    # 第二步: 准备签名
    slider_ticket = request.sliderTicket
    slider_randstr = request.sliderRandstr

    if need_slider_code:
        md5_text = f"86{phone_number}11{slider_ticket}{slider_randstr}{timestamp}{client_ip}{request_code}30b2718363204beeae98b7d03a75c3a4"
    else:
        md5_text = f"86{phone_number}11{timestamp}{client_ip}{request_code}30b2718363204beeae98b7d03a75c3a4"

    sign = f"86{phone_number}{hashlib.md5(md5_text.encode()).hexdigest()}"

    print(f"需要加密的签名: {sign}")

    # RSA加密和Base64编码 - 使用改进的加密函数
    try:
        encrypted = encrypt_with_rsa(sign, rsa_public_key)
        sign_encoded = base64.b64encode(encrypted).decode()
    except Exception as e:
        print(f"加密过程中出错: {str(e)}")
        # 失败时返回错误信息
        return {"success": False, "error": f"加密失败: {str(e)}", "data": result}

    # 第三步: 发送验证码
    verify_url = f"https://consumer.fcbox.com/v1/account/secureSendCode?mobile={phone_number}&type=11&opCode=30b2718363204beeae98b7d03a75c3a4&nationCode=86&sliderTicket={slider_ticket}&sliderRandstr={slider_randstr}&sign={sign_encoded}"

    verify_headers = {
        "pinpoint-traceid": "ConsumerA^1742830234824^83",
        "User-Agent": "channel=xiaomi,ip=,os=15,deviceType=2211133C,platform=Android,resolution=1080*2296,versionCode=6007000,versionName=6.7.0,timestamp=1742830229382",
        "FC_USER_FLAG": "",
        "FC_USER_AUTH": "tZGbsbamQGx8PkFPQ1acmgWu3ZW88nQsfdlMl2ZhxWs=",
        "pinpoint-spanid": "1",
        "pinpoint-sampled": "true",
        "pinpoint-pspanid": "-1",
        "Content-Length": "0",
        "Host": "consumer.fcbox.com",
        "Connection": "Keep-Alive",
    }

    verify_response = requests.post(verify_url, headers=verify_headers)

    return {
        "success": True,
        "data": verify_response.json(),
        "params": {
            "rsa_public_key": rsa_public_key,
            "client_ip": client_ip,
            "request_code": request_code,
            "timestamp": timestamp,
        },
    }


@app.post("/login")
async def login(request: LoginRequest):
    phone_number = request.phoneNumber
    verification_code = request.verificationCode
    rsa_public_key = request.rsaPublicKey
    client_ip = request.clientIp
    request_code = request.requestCode
    timestamp = str(request.timestamp)  # 确保timestamp是字符串类型

    print(
        f"登录参数 - 手机号: {phone_number}, 验证码: {verification_code}, 时间戳: {timestamp}"
    )

    # 准备签名
    md5_text = f"86{phone_number}{verification_code}01{timestamp}{client_ip}{request_code}30b2718363204beeae98b7d03a75c3a4"
    sign = f"86{phone_number}{hashlib.md5(md5_text.encode()).hexdigest()}"

    print(f"登录签名: {sign}")

    # RSA加密和Base64编码 - 使用改进的加密函数
    try:
        encrypted = encrypt_with_rsa(sign, rsa_public_key)
        sign_encoded = base64.b64encode(encrypted).decode()
    except Exception as e:
        print(f"登录加密过程中出错: {str(e)}")
        return {"success": False, "error": f"登录加密失败: {str(e)}"}

    # 登录请求
    url = f"https://consumer.fcbox.com/v1/account/secureLoginByPhone?mobile={phone_number}&verifyCode={verification_code}&channel=0&type=1&weiXinUser=&nationCode=86&opCode=30b2718363204beeae98b7d03a75c3a4&sign={sign_encoded}"

    headers = {
        "pinpoint-traceid": "ConsumerA^1742830241164^93",
        "User-Agent": "channel=xiaomi,ip=,os=15,deviceType=2211133C,platform=Android,resolution=1080*2296,versionCode=6007000,versionName=6.7.0,timestamp=1742830229383",
        "FC_USER_FLAG": "",
        "FC_USER_AUTH": "tZGbsbamQGx8PkFPQ1acmgWu3ZW88nQsfdlMl2ZhxWs=",
        "pinpoint-spanid": "1",
        "pinpoint-sampled": "true",
        "pinpoint-pspanid": "-1",
        "Content-Length": "0",
        "Host": "consumer.fcbox.com",
        "Connection": "Keep-Alive",
    }

    response = requests.post(url, headers=headers)
    authorization = response.headers.get("Authorization", "")

    # 打印响应信息
    print(f"登录响应状态码: {response.status_code}")
    print(f"登录响应头: {dict(response.headers)}")

    try:
        response_data = response.json()
        print(f"登录响应数据: {response_data}")
    except Exception as e:
        print(f"解析响应JSON失败: {str(e)}")
        print(f"原始响应内容: {response.text[:200]}")

    return {
        "success": True,
        "data": response_data if response.text else {},
        "authorization": authorization,
    }


@app.get("/completed_orders")
async def get_completed_orders(
    authorization: str = Header(None), page: int = 1, limit: int = 10
):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header is required")

    url = "https://consumer.fcbox.com/post/express/pageQuery4App"

    # 使用前端传递的page和limit参数
    data = {"expressStatus": "2", "pageNo": str(page), "pageSize": str(limit)}

    headers = {
        "User-Agent": "channel=xiaomi,ip=192.168.2.101,os=15,deviceType=2211133C,platform=Android,resolution=1080*2296,versionCode=6007000,versionName=6.7.0,timestamp=1742842891659",
        "Authorization": authorization,
        "pinpoint-spanid": "1",
        "pinpoint-sampled": "true",
        "pinpoint-pspanid": "-1",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "consumer.fcbox.com",
        "Connection": "Keep-Alive",
    }

    try:
        response = requests.post(url, data=data, headers=headers)

        # 检查响应状态码
        if response.status_code != 200:
            print(f"已取件API返回非200状态码: {response.status_code}")
            return {
                "success": False,
                "data": [],
                "message": f"API返回状态码: {response.status_code}",
                "page": page,
                "pageSize": limit,
            }

        # 检查响应内容是否为空
        if not response.text:
            print("已取件API返回空响应")
            return {
                "success": False,
                "data": [],
                "message": "API返回空响应",
                "page": page,
                "pageSize": limit,
            }

        # 尝试解析JSON
        try:
            response_data = response.json()
        except Exception as e:
            print(f"已取件API返回的JSON无法解析: {str(e)}")
            return {
                "success": False,
                "data": [],
                "message": f"返回数据解析失败: {str(e)}",
                "page": page,
                "pageSize": limit,
            }
    except Exception as e:
        print(f"已取件API请求异常: {str(e)}")
        return {
            "success": False,
            "data": [],
            "message": f"API请求异常: {str(e)}",
            "page": page,
            "pageSize": limit,
        }

    orders = []
    if response_data.get("success") and response_data.get("data"):
        # 尝试从不同可能的路径中获取订单数据
        raw_orders = []
        if "expressInfoDtos" in response_data["data"]:
            raw_orders = response_data["data"]["expressInfoDtos"]
        elif "data" in response_data["data"]:
            raw_orders = response_data["data"]["data"]

        # 规范化已取订单数据结构，与待取订单保持一致
        for order in raw_orders:
            normalized_order = {
                "expressId": order.get("expressId", ""),
                "companyName": order.get("companyName", "未知快递"),
                "courierName": order.get("companyName", "未知"),
                "pickupCode": order.get("code", ""),
                "boxNo": order.get("boxId", ""),
                "boxName": order.get("cabinetCode", ""),
                "boxLocation": order.get("boxLocation", ""),
                "address": order.get("address", ""),
                "sendTm": order.get("sendTm", ""),
                "pickTm": order.get("pickTm", ""),
                "clientMobile": order.get("clientMobile", order.get("pickerPhone", "")),
                "pickStatus": order.get("pickStatus", ""),
                "pickStatusDesc": order.get("pickStatusDesc", "已取件"),
                "expressStatus": "2",  # 2表示已取件
                "postId": order.get("postId", ""),
                "companyLogoUrl": order.get("companyLogoUrl", ""),
                "staffMobile": order.get("staffMobile", ""),
                "totalCustodyFee": order.get("totalCustodyFee", "0"),
                "custodyFeeTag": order.get("custodyFeeInfo", "").get(
                    "custodyFeeTag", ""
                ),
            }
            orders.append(normalized_order)

    # 规范化返回格式，直接返回数组
    return {
        "success": True,
        "data": orders,
        "page": page,
        "pageSize": limit,
        "total": response_data.get("data", {}).get("total", len(orders)),
    }


@app.get("/pending_orders")
async def get_pending_orders(
    authorization: str = Header(None), page: int = 1, limit: int = 10
):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header is required")

    # 待取件接口，暂无分页功能，但仍然接收参数以保持API一致性
    url = "https://consumer.fcbox.com/post/mobilePick/queryWaitPick?channelCode=ANDROID_FC_APP"

    headers = {
        "pinpoint-traceid": "ConsumerA0fc2d4fc6bfea8b^1742843515003^1713",
        "User-Agent": "channel=xiaomi,ip=192.168.2.101,os=15,deviceType=2211133C,platform=Android,resolution=1080*2296,versionCode=6007000,versionName=6.7.0,timestamp=1742842891659",
        "FC_USER_FLAG": "1061404658809110528",
        "FC_USER_AUTH": "akpP6vL3TSanbO2M2DHsFEbSj5kj3lPMdifTbcXUGbg5DW+9/bHk34dqg95Sz7wlG/b+Fj/IAlkGtwgYmyV4aQ==",
        "Authorization": authorization,
        "pinpoint-spanid": "1",
        "pinpoint-sampled": "true",
        "pinpoint-pspanid": "-1",
        "Host": "consumer.fcbox.com",
        "Connection": "Keep-Alive",
    }

    try:
        response = requests.get(url, headers=headers)

        # 打印响应状态和内容
        print(f"待取件API响应状态码: {response.status_code}")
        print(f"待取件API响应内容前200个字符: {response.text[:200]}")

        # 检查响应状态码
        if response.status_code != 200:
            print(f"待取件API返回非200状态码: {response.status_code}")
            return {
                "success": False,
                "data": [],
                "message": f"API返回状态码: {response.status_code}",
                "page": page,
                "pageSize": limit,
            }

        # 检查响应内容是否为空
        if not response.text:
            print("待取件API返回空响应")
            return {
                "success": False,
                "data": [],
                "message": "API返回空响应",
                "page": page,
                "pageSize": limit,
            }

        # 尝试解析JSON
        try:
            response_data = response.json()
        except Exception as e:
            return {
                "success": False,
                "data": [],
                "message": f"API请求异常: {str(e)}",
                "page": page,
                "pageSize": limit,
            }
    except Exception as e:
        return {
            "success": False,
            "data": [],
            "message": f"API请求异常: {str(e)}",
            "page": page,
            "pageSize": limit,
        }

    # 打印原始响应数据
    print(f"丰巢API返回的原始数据(待取件, 页码{page}):", response_data)

    # 处理pending_orders的复杂数据层级
    pending_data = []

    try:
        if (
            response_data.get("success")
            and response_data.get("data")
            and "cabinets" in response_data["data"]
        ):
            cabinets = response_data["data"]["cabinets"]

            # 遍历所有的柜机
            for cabinet in cabinets:
                cabinet_code = cabinet.get("cabinetCode", "")
                cabinet_address = cabinet.get("address", "")

                # 遍历柜机中的所有箱子
                if "boxes" in cabinet:
                    for box in cabinet["boxes"]:
                        box_id = box.get("boxId", "")
                        box_location = box.get("location", "")

                        # 遍历箱子中的所有包裹
                        if "packages" in box:
                            for package in box["packages"]:
                                # 标准化数据结构
                                normalized_package = {
                                    "expressId": package.get("expressId", ""),
                                    "companyName": package.get(
                                        "companyName", "未知快递"
                                    ),
                                    "courierName": package.get("companyName", "未知"),
                                    "pickupCode": package.get("code", ""),
                                    "boxNo": box_id,
                                    "boxName": cabinet_code,
                                    "boxLocation": box_location,
                                    "address": cabinet_address,
                                    "sendTm": package.get("sendTm", ""),
                                    "clientMobile": package.get("clientMobile", ""),
                                    "pickStatus": package.get("pickStatus", ""),
                                    "pickStatusDesc": package.get(
                                        "pickStatusDesc", "待取件"
                                    ),
                                    "postId": package.get("postId", ""),
                                    "expressStatus": "1",
                                    "companyLogoUrl": package.get("companyLogoUrl", ""),
                                    "staffMobile": package.get("staffMobile", ""),
                                    "totalCustodyFee": package.get(
                                        "totalCustodyFee", "0"
                                    ),
                                    "custodyFeeTag": package.get(
                                        "custodyFeeInfo", ""
                                    ).get("custodyFeeTag", ""),
                                    "boxGlobalRow": package.get("boxGlobalRow", ""),
                                }
                                pending_data.append(normalized_package)
    except Exception as e:
        return {
            "success": False,
            "data": [],
            "message": f"API请求异常: {str(e)}",
            "page": page,
            "pageSize": limit,
        }

    start_idx = (page - 1) * limit
    end_idx = start_idx + limit

    # 进行分页处理
    if start_idx < len(pending_data):
        paged_data = pending_data[start_idx:end_idx]
    else:
        paged_data = []

    # 规范化返回格式
    return {"success": True, "data": paged_data, "page": page, "pageSize": limit}


@app.post("/cabinet_location")
async def get_cabinet_location(
    request: CabinetLocationRequest, authorization: str = Header(None)
):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header is required")

    url = "https://consumer.fcbox.com/post/clientGet/cabinetVisualInfo"

    # 根据请求示例构建请求头
    headers = {
        "pinpoint-traceid": f"ConsumerA0fc2d4fc6bfea8b^{int(time.time() * 1000)}^993",
        "User-Agent": "channel=xiaomi,ip=40.65.45.56,os=15,deviceType=2211133C,platform=Android,resolution=1080*2296,versionCode=6007000,versionName=6.7.0,timestamp=1742894334183",
        "FC_USER_FLAG": "1061404658809110528",
        "FC_USER_AUTH": "akpP6vL3TSanbO2M2DHsFEbSj5kj3lPMdifTbcXUGbg5DW+9/bHk34dqg95Sz7wlG/b+Fj/IAlkGtwgYmyV4aQ==",
        "Authorization": authorization,
        "pinpoint-spanid": "1",
        "pinpoint-sampled": "true",
        "pinpoint-pspanid": "-1",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "consumer.fcbox.com",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
    }

    # 构建表单数据，使用cabinetCode
    form_data = f"cabinetCode={request.cabinetCode or ''}"
    try:
        response = requests.post(url, data=form_data, headers=headers)
        try:
            response_data = response.json()
        except Exception as e:
            return {
                "success": False,
                "data": {},
                "message": f"解析API响应失败: {str(e)}, 原始响应: {response.text[:100]}",
            }

        if response.status_code != 200 or not response_data.get("success", False):
            return {
                "success": False,
                "data": {},
                "message": f"API返回错误: {response_data.get('message', '未知错误')}",
            }

        # 处理返回的数据，返回标准格式
        return {"success": True, "data": response_data.get("data", {})}

    except Exception as e:
        return {
            "success": False,
            "data": {},
            "message": f"API请求异常: {str(e)}",
        }


@app.post("/openBox")
async def openBox(request: OpenBoxRequest, authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header is required")

    url = "https://consumer.fcbox.com/post/clientGet/openBox"

    # 根据请求示例构建请求头
    headers = {
        "pinpoint-traceid": f"ConsumerA0fc2d4fc6bfea8b^{int(time.time() * 1000)}^993",
        "User-Agent": "channel=xiaomi,ip=40.65.45.56,os=15,deviceType=2211133C,platform=Android,resolution=1080*2296,versionCode=6007000,versionName=6.7.0,timestamp=1742894334183",
        "FC_USER_FLAG": "1061404658809110528",
        "FC_USER_AUTH": "akpP6vL3TSanbO2M2DHsFEbSj5kj3lPMdifTbcXUGbg5DW+9/bHk34dqg95Sz7wlG/b+Fj/IAlkGtwgYmyV4aQ==",
        "Authorization": authorization,
        "pinpoint-spanid": "1",
        "pinpoint-sampled": "true",
        "pinpoint-pspanid": "-1",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "consumer.fcbox.com",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
    }

    # 构建表单数据，使用cabinetCode
    data = {
        "cabinetCode": request.cabinetCode,
        "channel": "APP-ANDRIOD",
        "clientMobile": request.clientMobile,
        "cmdkType": "1",
        "expressId": request.expressId,
        "localActivityId": "",
        "localAddress": request.address,
        "localAllBoxIdList": request.boxId,
        "localBoxGlobalRow": request.boxGlobalRow,
        "localCode": request.code,
        "localCurrBoxId": request.boxId,
        "localDigitizationStatus": 0,
        "localFromSource": "2",
        "localOneClickOpenCabinetValidTime": "",
        "localOrderId": "",
        "localPopupTimeout": 120,
        "localRefusePackages": [
            {
                "companyLogoUrl": request.companyLogoUrl,
                "companyName": request.companyName,
                "expressId": request.expressId,
                "expressType": request.expressType,
                "localSelected": True,
                "postId": request.postId,
                "staffMobile": request.staffMobile,
            }
        ],
        "localRefuseSessionTokenTime": 120,
        "localScanFirst": True,
        "localScanTotal": 0,
        "localSource": "0",
        "localSupportVisual": False,
        "mobilePickType": "APP-ANDRIOD",
        "pickType": "ANDROID_PICK_MOBILE_APP",
        "postId": request.postId,
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        try:
            response_data = response.json()
        except Exception as e:
            return {
                "success": False,
                "data": {},
                "message": f"解析API响应失败: {str(e)}, 原始响应: {response.text[:100]}",
            }

        if response.status_code != 200 or not response_data.get("success", False):
            return {
                "success": False,
                "data": {},
                "message": f"API返回错误: {response_data.get('message', '未知错误')}",
            }

        # 处理返回的数据，返回标准格式
        return {"success": True, "data": response_data.get("data", {})}

    except Exception as e:
        return {
            "success": False,
            "data": {},
            "message": f"API请求异常: {str(e)}",
        }


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=5000, reload=True)
