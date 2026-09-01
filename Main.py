from cons import char_map, multiples, tick, maxBits
from concurrent.futures import ThreadPoolExecutor
import time

testString = "Hey"
recData = []

cable = 0

def ASCIIConv(info, work):
    if work == True:
        letters = list(info)
        finalBinary = []
        cleanBinary = []
        for letter in letters:
            decimal_num = char_map[letter]
            binaryResult = []
            
            for v in multiples:
                if decimal_num >= v:
                    binaryResult.append(1)
                    decimal_num -= v
                else:
                    binaryResult.append(0)
            finalBinary.append(binaryResult)
    
        for letter in finalBinary:
            for bit in letter:
                cleanBinary.append(bit)
                    
        return cleanBinary
    else:
        dataL = []
        finalbin = []
        data = ""
        for i in range(0, len(info), 8):
            bloco = info[i:i+8]
            finalbin.append(bloco)

        storedMultiple = []

        for letter in finalbin:
            firstMulti = []
            for i, val in enumerate(letter):
                if int(val) == 1:                    
                    firstMulti.append(multiples[i])
            storedMultiple.append(sum(firstMulti))
    
        for index, mul in enumerate(storedMultiple):
            for l, v in char_map.items():
                if v == storedMultiple[index]:
                    dataL.append(l)
        for letter in dataL:
            data += str(letter)

        return data

def startClock():
    global cable, recData
    data = []
    iteration = 0
    time.sleep(tick / 2)

    while iteration < maxBits:
        data.append(cable)
        iteration += 1
        time.sleep(tick)
    recData = data
    return recData

def sendData(data):
    global cable, recData
    
    for bit in data:
        cable = bit
        time.sleep(tick)

def transmit(data):
    with ThreadPoolExecutor() as executor:
        res = executor.submit(startClock)
        res2 = executor.submit(sendData, data)

    binary = res.result()

    cable = 0
    return ASCIIConv(binary, False)

def test():
    bin = ASCIIConv(testString, True)
    return transmit(bin)
    
print(test())