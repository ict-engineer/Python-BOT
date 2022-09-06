import pocketOptionSelenium
import logging
import time

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)

from telethon import TelegramClient, events

# Premium has ID -1001308366242
# TestMsg has ID 1392897160
# TestingScript has ID -428345469
# Indicator Signals Forextrade1 has ID -1001406919616

api_id = 2259167
api_hash = '14143b25ac938c15bc088dba777d4b6b'
userName = "nomana123"
client = TelegramClient(userName, api_id, api_hash)


# Testing for Selenium
@client.on(events.NewMessage(chats="MyTelegramCopier"))
async def handler(event):
    print(event.raw_text)
    pocketOptionSelenium.openChrome("Test123")


# Listen to Indicator Signals Forextrade1
@client.on(events.NewMessage(chats=-1001406919616))
async def handler(event):
    token = event.raw_text.split("\n")
    if len(token) == 8 and "TP" in token[2]:
        tp = "TP " + token[2].split("TP ")[1]
        signal = token[0] + "\n" + tp
        print(signal)
        await sendToTrade(signal)


# Listen to TestMsg
@client.on(events.NewMessage(chats=1392897160))
async def handler(event):
    async for dialog in client.iter_dialogs():
        print(dialog.name, 'has ID', dialog.id)
    token = event.raw_text.split("\n")
    print(token)
    if "TP" in token[2]:
        print(token[2].split("TP ")[1])
    # if len(event.raw_text) > 20:
    #     await formatPremium(event.raw_text)


# Premium connected
@client.on(events.NewMessage(chats=-1001308366242))
async def handler(event):
    unFormatted = event.raw_text
    await formatPremium(unFormatted)


async def formatPremium(unFormatted):
    split = unFormatted.split("\n")
    if len(split) > 4:
        signal1 = ""
        signal2 = ""
        level1Signal = ""
        level2Signal = ""
        assetName = ""
        takeProfit = ""
        if "SELL GBPUSD" in unFormatted:
            assetName = "SELL GBPUSD "
        if "SELL EURUSD" in unFormatted:
            assetName = "SELL EURUSD "
        if "BUY AUDUSD" in unFormatted:
            assetName = "BUY AUDUSD "
        if "BUY USDCAD" in unFormatted:
            assetName = "BUY USDCAD "
        if "BUY USOIL" in unFormatted:
            assetName = "BUY USOUSD "
        if "BUY XAUUSD" in unFormatted:
            assetName = " BUY XAUUSD "

        if "TP" in split[9]:
            takeProfit = str(split[9])

        if ("SELL GBPUSD" in unFormatted or "SELL EURUSD" in unFormatted or "BUY AUDUSD" in unFormatted
                or "BUY USDCAD" in unFormatted or "BUY USOIL" in unFormatted or "BUY XAUUSD") and len(split) == 10:
            print("split: ")
            print(split)
            # S1:
            if "S1:" in split[4]:
                sigInfo = formatPremiumLines(split[4])
                signal1 = assetName + sigInfo + " " + str(takeProfit)
                print("S1: ")
                print(signal1)
            # S2
            if "S2:" in split[5]:
                sigInfo = formatPremiumLines(split[5])
                takeProfit = split[9]
                signal2 = assetName + sigInfo + " " + takeProfit
                print("S2: ")
                print(signal2)
            # L1
            if "L1:" in split[7] or "E1:" in split[7]:
                levelSig = formatPremiumLevels(split[7])
                level1Signal = assetName + levelSig + " " + takeProfit
                print("level1Sig: ")
                print(level1Signal)

            if "L1:" in split[8]:
                levelSig = formatPremiumLevels(split[8])
                level1Signal = assetName + levelSig + " " + takeProfit
                print("level1Sig: ")
                print(level1Signal)

            if "L2:" in split[8] or "E1:" in split[8] or "E2:" in split[8]:
                levelSig = formatPremiumLevels(split[8])
                level2Signal = assetName + levelSig + " " + takeProfit
                print("level2Signal: ")
                print(level2Signal)

        if signal1 != "":
            print("sending sig1")
            await sendToTrade(signal1)
        if signal2 != "":
            await sendToTrade(signal2)
        if level1Signal != "":
            print("sending level1Signal")
            await sendToTrade(level1Signal)
        if level2Signal != "":
            print("sending level2Signal")
            await sendToTrade(level2Signal)


def formatPremiumLines(line):
    signalLine = line.split(" ")
    myRangeValueFirst = signalLine[1].split("-")[0]
    # myRangeValueSecond = float(signalLine1[1].split("-")[1])
    atValue = myRangeValueFirst
    stopLoss = signalLine[2]
    line = atValue + " " + stopLoss
    return line


def formatPremiumLevels(line):
    line = line.replace(" ", "")
    level = line[3:len(line)]
    firstVal = level.split("-")[0]
    if "|" in level:
        levelSL = level.split("|")[1]
        levelSL = levelSL.split("(")[0]
    else:
        levelSL = "S" + line.split("S")[1]
    return firstVal + " " + levelSL


async def sendToTrade(formattedSignal):
    # async for dialog in client.iter_dialogs():
    #     print(dialog.name, 'has ID', dialog.id)

    # print("formattedSignal: ")
    # print(formattedSignal)
    if formattedSignal:
        print("Still sending")
        # sent = await client.send_message(-1001212341441, formattedSignal)
        sent = await client.send_message("MySignals", formattedSignal)
        time.sleep(2)


async def main():
    # Getting information about yourself
    me = await client.get_me()


def remove_last_line_from_string(s):
    return s[:s.rfind('\n')]


def strip_end(text, suffix):
    if not text.endswith(suffix):
        return text
    return text[:len(text) - len(suffix)]


with client:
    client.run_until_disconnected()
