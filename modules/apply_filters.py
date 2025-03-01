import cv2
import numpy as np

# グローバルなどに用意: Haar カスケードの読み込み
face_cascade = cv2.CascadeClassifier("xml/haarcascade_frontalface_default.xml")

def apply_filters(img, brightness, saturation, arg3=None):
    """
    img: BGR形式のnumpy配列
    brightness: 明るさの倍率 (1.0 なら変化なし)
    saturation: 彩度の倍率 (1.0 なら変化なし)
    arg3
    """
    # 1) 顔検出
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.2, 5)

    # 3) 明るさ調整 (簡易的にアルファだけ変える)
    # alpha=brightness, beta=0
    img = cv2.convertScaleAbs(img, alpha=brightness, beta=0)

    # 4) 彩度調整: BGR -> HSV へ変換し、Sチャネルを調整
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
    # hsv[...,0] -> H, hsv[...,1] -> S, hsv[...,2] -> V
    hsv[...,1] = hsv[...,1] * saturation  # 彩度チャンネルを乗算
    hsv[...,1] = np.clip(hsv[...,1], 0, 255)  # ピクセル値は0~255にクリップ
    hsv = hsv.astype(np.uint8)
    img = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    return img

