import re
import neo4j_service
import json

FEMALE = [r"(n|N)ữ"]
MALE = [r"(n|N)am", "nam giới"]
AGE = [r"[0-9]{1,4}\s{1,6}tuổi"]
BN_RANGE = [
    r"CA BỆNH\s{1,6}[0-9]{1,4} - [0-9]{1,4}",
    r"Bệnh nhân\s[0-9]{1,4} - [0-9]{1,4}",
    r"Bệnh nhân số\s{1,6}[0-9]{1,4} - [0-9]{1,4}"
]
BNre = [
    r"CA BỆNH\s{1,6}[0-9]{1,4}",
    r"(b|B)ệnh nhân\s[0-9]{1,4}",
    r"(b|B)ệnh nhân số\s{1,6}[0-9]{1,4}",
    r"BN\s{0,2}[0-9]{1,4}"
]
FLIGHT_RE = [r"(c|C)huyến bay\s{0,6}[A-Z]{1,4}\s?[0-9]{2,8}"]
NATIONLATY_RE = [
    "quốc tịch(.{0,1}[A-Z]\w{1,7}){1,4}",
    "quốc tịch(.{0,1}\w{1,7}){1,4}"
]
ORIGIN = [
    r"(địa\s{1,2}chỉ|trú)\s{1,2}(tại|ở)\s{1,2}(\s|\w|,|TP.)*([A-Z]\w{1,})",
    r"(địa chỉ|trú|quê) (tại|ở)?(\s(phường|quận|thị xã|thị trấn|tỉnh|thành phố)?(\s?\w{1,4}){1,4})"
]
NUMBERSIT = ["số ghế [0-9]{1,8}[A-Z]{1,4}\s?"]
flags = re.I | re.U
DEATH = [
    r"(đã)?\s{1,4}(chết|khuất|ngoẻo|tử vong|mất)",
    r"(đã)\s{1,4}(khuất|mất)"
]
NEGATIVE_COVID = [r"(đã)?\s{1,4}(khỏi bệnh)"]


def getStatus(text):
    for i in NEGATIVE_COVID:
        result = re.search(i, text, flags)
    if result:
        return "negative"
    for i in DEATH:
        result = re.search(i, text, flags)
    if result:
        return "death"
    return None


def getSex(text):
    for i in FEMALE:
        result = re.search(i, text)
        if result:
            return "female"
    for i in MALE:
        result = re.search(i, text)
        if result:
            return "male"
    return None


def getAge(text):
    for i in AGE:
        result = re.search(i, text)
        if result:
            return re.findall(i, text)[0]
    return None


def BNrange(text):
    BNids = None
    for i in BN_RANGE:
        result = re.search(i, text)
        if result:
            BNids = re.findall(i, text)[0]
            ids = re.findall(r"[0-9]{1,4}", BNids)
            return (ids)
            break
        return None


def getBNid(text):
    BNs = []
    for i in BNre:
        result = re.search(i, text)
        if result:
            text_include = re.findall(i, text)
            for bn in text_include:
                BNs.append(re.findall(r"[0-9]{1,4}", bn)[0])
    return ["BN" + BNid for BNid in BNs]


def preprocessIDBN(text):
    BNs = []
    for i in BNre:
        result = re.search(i, text)
        if result:
            text_include = re.findall(i, text)
            for bn in text_include:
                text = text.replace(bn, "BN" + str(re.findall(r"[0-9]{1,4}", bn)[0]))

    text = text.replace("TP. ", "thành phố ")
    return text


def seperateSentences(text):
    sentences = []
    for sentence in text.split('.'):
        sentences += sentence.split(";")
    return sentences


def getRelation(text):
    BNids = getBNid(text)
    for BNid in BNids:
        neo4j_service.createBN(BNid, None, None, None, None, None, None, None, None)
    if len(BNids) < 2:
        return
    BNid_main = BNids[0]

    for sentence in seperateSentences(text):
        if len(sentence) < 4:
            continue
        BNids = getBNid(sentence)
        if len(BNids) < 2:
            continue
        else:
            for i in range(len(BNids) - 1):
                BNid1 = BNids[i]
                BNid2 = BNids[i + 1]
                if BNid1 == BNid2:
                    continue
                else:
                    sub = text[text.rfind(BNid1) + len(BNid1):text.find(BNid2)]
                    print(sub)
                    if "," in sub:
                        BNid1 = BNid_main
                    else:
                        BNid_main = BNid1
                    relation = sub[sub.rfind(",") + 1:]
                    if relation == None:
                        relation = sub[sub.rfind("(") + 1:]
                    if relation == None:
                        relation = sub
                    print("Relation:", BNid1, relation, BNid2)
                    neo4j_service.createConnect(BNid1, relation, BNid2)


def getNationlaty(text):
    for i in NATIONLATY_RE:
        result = re.search(i, text, flags)
        if result:
            match_obj_country = re.search("([A-Z]\w{1,7}.{0,1}){1,4}", result.group(0))
            if match_obj_country:
                return match_obj_country.group(0)
            else:
                return result.group(0)


def getOrigin(text):
    for i in ORIGIN:
        result = re.search(i, text, flags)
        if result:
            return result.group(0)


def getFlight(text):
    for i in FLIGHT_RE:
        result = re.search(i, text)
        if result:
            return result.group(0)
    return None


def getNumberSit(text):
    for i in NUMBERSIT:
        result = re.search(i, text)
        if result:
            return result.group(0)
    return None


def process(text, date=None):
    BNid_main = None
    for sentence in seperateSentences(text):
        print("#" * 32)
        print("Sentences:", sentence)
        BNids = getBNid(sentence)
        if len(BNids) != 0:
            BNid_main = BNids[0]
        print(BNid_main)
        if date:
            neo4j_service.updateBN(BNid_main, "date", date)
        sex = getSex(sentence)
        if sex != None:
            neo4j_service.updateBN(BNid_main, "sex", sex)
            print("Sex:", sex)
        age = getAge(sentence)
        if age != None:
            neo4j_service.updateBN(BNid_main, "age", age)
            print("Age:", age)
        flight = getFlight(sentence)
        if flight != None:
            neo4j_service.createTranspotation(BNid_main, flight)
            print("Flight:", flight)
            numbersit = getNumberSit(sentence)
            if numbersit != None:
                neo4j_service.updateBN(BNid_main, "number_sit", numbersit)
                print("Numbersit:", numbersit)
                neo4j_service.createConnectPTVT(BNid_main, numbersit, flight)
        nationlaty = getNationlaty(sentence)
        if nationlaty != None:
            neo4j_service.updateBN(BNid_main, "nationlaty", nationlaty)
            print("Nation:", nationlaty)
        origin = getOrigin(sentence)
        if origin != None:
            neo4j_service.updateBN(BNid_main, "origin", origin)
            print("Origin:", origin)
        status = getStatus(sentence)
        if status != None:
            neo4j_service.updateBN(BNid_main, "status", status)
            print("Status:", status)


def getObject(text, date=None):
    try:
        text = preprocessIDBN(text)
        getRelation(text)
        process(text, date)
    except Exception as e:
        print("Error: ", e)


if __name__ == '__main__':
    f = open('../scraper/scraper/crawled_data/legit_timeline_news.json')
    timeline_articles = json.load(f)
    for article in timeline_articles:
        getObject(article['content'], article['time_tag'].split(" ")[1])




        # print(article['time_tag'].split(" ")[1])
    # text = """THÔNG BÁO VỀ 2 CA MẮC MỚI (BN2558-2559): Ghi nhận trong nước tại Hải Dương. Cụ thể: Ca bệnh BN2558 (BN2558): ghi nhận tại xã Kim Đính, huyện Kim Thành, tỉnh Hải Dương, là F1 của BN2484 và BN2471, đã được cách ly trước đó.
    # Ca bệnh BN2559 (BN2559): ghi nhận tại xã Kim Đính, huyện Kim Thành, tỉnh Hải Dương, là F1 của BN2467, đã được cách ly trước đó.
    # Ngày 14/3/2021, cả 2 bệnh nhân trên được lấy mẫu xét nghiệm. Kết quả xét nghiệm ngày 15/3/2021 cả 2 bệnh nhân dương tính với SARS-CoV-2. Hiện 2 bệnh nhân đang được cách ly điều trị tại Bệnh viện Dã chiến số 3 - Bệnh viện Đa khoa tỉnh Hải Dương cơ sở 2.
    # """
    # getObject(text, "16/03/2021")
