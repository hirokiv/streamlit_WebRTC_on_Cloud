# streamlit WebRTC on Cloud

## 実施事項
- Linux(Ubuntu)のクラウドサーバーでの実行を想定
- Streamlitアプリを生成
  - `app.py`を記述。アクセス端末の動画をサーバーに保存する
  - Port 8505で立ち上げ
  - Python 3.10で実行
- NAT Traversal1
  - STUN serverはgoogleの無料サーバーを利用
  - TURN サーバーは、coturnライブラリにより設定
- HTTPS化のためにNginxによるリバースプロキシサーバーを設定
  - 80へのアクセスを8505 Portへリダイレクト
- (ドメインを有する場合は、Certbot (Let's encrypt)によるSSL証明書の利用を推奨)
- streamlit-webrtcは最新版が正しく実行できず、バージョンを落として実行

## Nginx によるリダイレクト
記載ファイルは`nginx_template`を参照

Streamlitサーバーのhttp port(80)へのルーティングを設定
nginxをインストール
```
sudo apt install nginx
```

Streamlitへのルーティング
IPへのhttp requestをStreamlitのサーバー(Port 8505へ)
```
vim /etc/nginx/sites-available/streamlit-webservice
ln -s /etc/nginx/sites-available/streamlit-webservice  /etc/nginx/sites-enabled/streamlit-webservice
```
以下についても編集 (ssl_protoclsを制限)
```
vim /etc/nginx/nginx.conf
```

下記ファイルを編集
```
/etc/nginx/nginx.conf
```
Streamlitを再度立ち上げ
```
sudo systemctl reload nginx
sudo systemctl restart nginx
```
起動状況を確認
```
sudo systemctl status nginx
```

## SSL 化のための証明書取得
opensslか、certbot(Let's encrypt)
### oepnsslコマンドで自己証明書を発行
```
sudo openssl req \
	-subj '/CN=example.com (self-signed)/O=ORGANIZATION/C=JP' \
	-x509 -nodes -days 365 -newkey rsa:2048 \
	-keyout /etc/ssl/private/selfsigned.key \
	-out /etc/ssl/private/selfsigned.crt
```

### Certbot (Let's encrypt)
sudo apt install certbot python3-certbot-nginx
ここでは省略


## STUN, TURN serverの設定
NAT超えのための媒介サーバー。Pythonでは以下に該当
```

```
### STUN
Googleが公開している公開STUNサーバーを利用。立ち上げ状況は以下を確認
```
traceroute -U stun.l.google.com 19302
```

### TURN
TURN serverはサーバー内に自前で構築

インストール
```
sudo apt install coturn
```
内容を編集 （`turn_template`参照）
```
vim /etc/trunserver.conf
```
サービスを起動
```
sudo sytemctl enable coturn
sudo sytemctl restart coturn
```

## python setup
Python 3.10をインストール
`pip install -r requirements.txt`
## Streamlit setup
`.streamlit/config.toml`を設定し、SSL証明書へのルートとPort(8505)を設定
app.pyを立ち上げて、サーバーに取得動画を保存
```
streamlit run app.py
```

## References 
- [PythonでWebRTCを使ったリアルタイム通信の実装方法](https://brian0111.com/python-webrtc-real-time-communication/)
- [StreamlitのWebサービスをLet's EncryptでHTTPS化する手順の解説]( https://www.softbank.jp/biz/blog/cloud-technology/articles/202305/https-streamlit/)
- [whitphx / streamlit-webrtc](https://github.com/whitphx/streamlit-webrtc)
- [OpenSSL コマンドで自己署名 SSL/TLS サーバ証明書を作成する (SAN 対応)](https://qiita.com/hoto17296/items/b93187da939ef6f1cbb9)
- [とりあえずcertbotでSSL証明書を発行する](https://qiita.com/watav/items/3d77e2c0b32aceff7909)
- [Nginxに自己署名証明書を設定してHTTPS接続してみる](https://qiita.com/ohakutsu/items/814825a76b5299a96661)
- [coTurnでEC2上にTURNサーバを作ってみた](https://qiita.com/okyk/items/2d7db6b148a43bc3b405)
