def filter_mother_daughter(comments):
    # 一级关键词（直接命中母女关系，扩充隐喻/方言/场景词）
    strong_keywords = [
        "母女", "母子" , "母女关系", "母女情", "母女线", "母女档",
        "母爱", "亲子关系", "母职", "妈妈们", "母亲角色",
        "单亲妈妈", "独生女", "母女俩", "娘亲", "囡囡", "小棉袄",
        "慈母", "贤女", "母性光辉", "抚养女儿", "养育女儿", "陪伴女儿"
    ]

    # 二级关键词（母亲相关，补充同义/方言/敬称）
    mother_words = [
        "妈妈", "母亲", "娘", "妈", "母" ,"老妈", "妈咪", "娘亲",
        "她妈", "他妈", "单亲妈妈", "慈母", "母上", "母親大人",
        "宝妈", "母性", "养母", "继母"  # 补充常见母亲相关称谓
    ]

    # 二级关键词（女儿相关，补充同义/方言/爱称）
    daughter_words = [
        "女儿", "闺女", "姑娘", "小姑娘", "丫头", "囡囡", "小棉袄",
        "她女儿", "他女儿", "独生女", "贤女", "乖女儿", "囡儿",
        "千金", "小丫头", "干女儿"  # 补充常见女儿相关称谓
    ]
    filtered = []

    for c in comments:
        content = c["content"]

        # 1. 强匹配：只要出现这些就直接选
        if any(k in content for k in strong_keywords):
            filtered.append(c)
            continue

        # 2. 母 / 女任意组合匹配
        if any(m in content for m in mother_words) and \
                any(d in content for d in daughter_words):
            filtered.append(c)
            continue

        # 3. “她和她妈”“她和女儿”的句型
        if ("她" in content) and ("妈" in content):
            filtered.append(c)
            continue
        if ("她" in content) and ("女儿" in content):
            filtered.append(c)
            continue

        # 4. 亲情戏 + 女性（常见于影评，但不一定是母女）
        if ("亲情戏" in content or "家庭线" in content) and \
                ("母" in content or "妈" in content):
            filtered.append(c)
            continue

    return filtered