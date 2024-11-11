def calc_man(weight, height, age):
    if age >= 30:
        ret = 3.4 * weight + 15.3 * height - 6.8 * age - 961
    else:
        ret = 66.5 + 13.7 * weight + 5 * height - 6.8 * age

    print(ret)
    return ret


def calc_woman(weight, height, age):
    if age >= 30:
        ret = 2.4 * weight + 9 * height - 4.7 * age - 65
    else:
        ret = 655 + 9.6 * weight + 1.8 * height - 4.7 * age

    print(ret)
    return ret


calc_man(95, 167, 37)


def morning():
    return ""


def mid_morning_lunch():
    return ""


def lunch():
    fibers = []
    protein = [{"weight_cooked": 200,
                "name": "chicken_breast"
                }]
    carbohydrate = [{"weight_raw": 200,
                     "name": "tomato"
                     },
                    {"weight_raw": 200,
                     "name": "cucumber"
                     },
                    {"weight_raw": 100,
                     "name": "lettuce"
                     },
                    {"weight_raw": 120,
                     "name": "bell pepper"
                     }
                    ]
    lipids = [{"weight_raw": 200,
                     "name": "oil"
                     },]


def dinner():
    protein = ["egg", "tuna", "chicken breast"]
    ret = ["salad", "egg"]
