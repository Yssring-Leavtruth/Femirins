def canvert_str(_string: str) -> str:

    num_dic = {
        "零": "0",
        "一": "1",
        "二": "2",
        "三": "3",
        "四": "4",
        "五": "5",
        "六": "6",
        "七": "7",
        "八": "8",
        "九": "9",
        "十": "10"
    }

    result = ""

    for i in _string:

        if i in num_dic.keys():
            result += num_dic[i]
        else:
            result += i

    return result