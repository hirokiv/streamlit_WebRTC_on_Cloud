# streamlit WebRTC on Cloud

## 実施事項
- NAT Traversal1
  - STUN serverはgoogleの無料サーバーを利用
  - TURN サーバーは、coturnライブラリにより設定
- HTTPS化のためにNginxによるリバースプロキシサーバーを設定

## Nginx
Streamlitサーバーのhttp port(80)へのルーティングを設定
```
vim /etc/nginx/sites-available/streamlit-webservice
ln -s /etc/nginx/sites-available/streamlit-webservice  /etc/nginx/sites-enabled/streamlit-webservice
```

## Streamlit setup
`.streamlit/config.toml`を設定

## References 
- [PythonでWebRTCを使ったリアルタイム通信の実装方法](https://brian0111.com/python-webrtc-real-time-communication/)
- [StreamlitのWebサービスをLet's EncryptでHTTPS化する手順の解説]( https://www.softbank.jp/biz/blog/cloud-technology/articles/202305/https-streamlit/)
- [whitphx / streamlit-webrtc](https://github.com/whitphx/streamlit-webrtc)
