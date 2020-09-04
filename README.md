# mini_twitter
make mini twitter studing backend

# start backend code

#### run app.py
```bash
FLASK_ENV=development FKAS_APP=app.py flask run
```

#### request to server (app.py)
```bash
http -v POST localhost:5000/sign-up name=huhji email=huhji.elha@gmail.com password=1234
```

### HTTP Status Code remind

#### 200 OK

HTTP 요청이 문제없이 성공적으로 잘 처리되었을 때 보내는 status code

#### 301 Moved Permanently

HTTP 요청을 보낸 엔드포인트의 URL 주소가 바뀌었다는 것을 나타내는 status code.
이때 Location 헤더에 해당 엔드포인트의 새로운 주소가 포함되어 나온다.
301 요청을 받은 클라이언트는 Location 헤더의 새로운 엔드포인트 주소에 해당 요청을 다시 보내게 된다. 이러한 과정을 "redirection"이라고 한다.

#### 400 Bad Request

HTTP 요청이 잘못된 요청일 때 보내는 응답 코드.
주로 요청에 포함된 input 값이 잘못 보내졌을 때 사용된다.
예를 들어, 사용자의 전화번호를 저장하는 HTTP 요청인데, 전화번호 input에 숫자가 아닌 텍스트가 포함된 요청을 보낼 경우 서버에서는 400 응답을 클라이언트에게 전송한다.

#### 401 Unauthorized

HTTP 요청을 처리하기 위해서는 해당 요청을 보내는 클라이언트의 신분(credential) 확인이 요구되나, 서버 측에서 이를 확인할 수 없었을 때 보내는 응답 코드.
주로 해당 HTTP 요청을 보내는 사용자가 로그인이 필요할 경우 401 응답을 전송한다.

#### 403 Forbidden

HTTP 요청을 보내는 클라이언트가 해당 요청에 대한 권한이 없음을 나타내는 statud code. 예를 들어, 비용을 지불한 사용자만 볼 수 있는 데이터에 대해 HTTP 요청을 보낸 사용자는 아직 비용을 지불하지 않은 상태일 경우 403 응답을 받게 된다.

#### 404 Not Found

HTTP 요청을 보내려는 URI가 존재하지 않을 때 보내는 status code. 어떤 웹사이트에 잘못된 주소로 접근하려고 했을 때 "해당 페이지를 찾을 수 없습니다."라는 메세지가 이에 해당한다.

#
