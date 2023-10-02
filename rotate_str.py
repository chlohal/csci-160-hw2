def rotate(s):
    l = len(s)
    for i in range(l):
        print(s, end=" ")
        s = s[1:] + s[0]
