def commonTwo(a: list, b: list):
    count = 0
    if len(a) > len(b):
        longer_list = {'list':a,'length':len(a)}
    elif len(a) <= len(b):
        longer_list = {'list':b,'length':len(b)}
    
    for item in range(longer_list['length']):
        print(1)

        

    return count

commonTwo([1,2,3,4],[2,3,5])
