import random
def genotp():
    otp=''
    caps=[chr(i) for i in range(ord('A'),ord('Z')+1)]
    sms=[chr(i) for i in range(ord('a'),ord('z')+1)]
    for i in range(0,2):
        otp=otp+random.choice(caps)
        otp=otp+str(random.randint(0,9))
        otp=otp+random.choice(sms)
    return otp