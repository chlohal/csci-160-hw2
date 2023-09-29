def rotate(s):
    l = len(s)
    if l > 1:
        for i in range(l):
            print(s, end=" ")
            s = s[1:] + s[0]
    else:
        print(s, end=" ")
    print()
