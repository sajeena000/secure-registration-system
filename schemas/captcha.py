from pydantic import BaseModel

class CaptchaResponse(BaseModel):
    captcha_id: str
    image_base64: str