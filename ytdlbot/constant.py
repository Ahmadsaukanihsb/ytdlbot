#!/usr/local/bin/python3
# coding: utf-8

# ytdlbot - constant.py
# 8/16/21 16:59
#

__author__ = "Benny <benny.think@gmail.com>"

import os

from config import (
    AFD_LINK,
    COFFEE_LINK,
    ENABLE_CELERY,
    FREE_DOWNLOAD,
    REQUIRED_MEMBERSHIP,
    TOKEN_PRICE,
)
from database import InfluxDB
from utils import get_func_queue


class BotText:
    start = """
Selamat datang di Downloader Bot. ketik /help cara menggunakan bot. 
Developed by : @Exodiazx"""

    help = f"""
Salin link dari Platform Youtube/Tiktok/Instagram/Facebook/Twitter Kirim ke bot ini.
    """

    about = "Downloader Bot by @Exodiazx."

    buy = f"""
**Terms:**
1. Anda dapat menggunakan bot ini untuk mendownload video sebanyak {FREE_DOWNLOAD} kali dalam jangka waktu 24 ja.

2. Anda dapat membeli token Download tambahan, berlaku secara permanen.

3. Pengembalian dana dimungkinkan, hubungi saya jika Anda membutuhkannya @Exodiazx

4. Download untuk pengguna Premium tidak memerlukan antrian.

5. Premium user bisa mendownload video lebih dari 2GB.

**Price:**
valid permanently
1. 1 USD == {TOKEN_PRICE} tokens
2. 7 CNY == {TOKEN_PRICE} tokens
3. 10 TRX == {TOKEN_PRICE} tokens

**Payment options:**
Pay any amount you want. For example you can send 20 TRX for {TOKEN_PRICE * 2} tokens.
1. AFDIAN(AliPay, WeChat Pay and PayPal): {AFD_LINK}
2. Buy me a coffee: {COFFEE_LINK}
3. Telegram Bot Payment(Stripe), please click Bot Payment button.
4. TRON(TRX), please click TRON(TRX) button.

**After payment:**
1. Afdian: attach order number with /redeem command (e.g., `/redeem 123456`).
2. Buy Me a Coffee: attach email with /redeem command (e.g., `/redeem 123@x.com`). **Use different email each time.**
3. Telegram Payment & Tron(TRX): automatically activated within 60s. Check /start to see your balance.

Want to buy more token with Telegram payment? Let's say 100? Here you go! `/buy 123`
    """

    private = "This bot is for private use"

    membership_require = f"You need to join this group or channel to use this bot\n\nhttps://t.me/{REQUIRED_MEMBERSHIP}"

    settings = """
Please choose the preferred format and video quality for your video. These settings only **apply to YouTube videos**.

High quality is recommended. Medium quality aims to 720P, while low quality is 480P.

If you choose to send the video as a document, it will not be possible to stream it.

Your current settings:
Video quality: **{0}**
Sending format: **{1}**
"""
    custom_text = os.getenv("CUSTOM_TEXT", "")

    premium_warning = """
File Anda terlalu besar, apakah Anda ingin saya mencoba mengirimkannya sebagai pengguna premium?
Ini adalah fitur eksperimental sehingga Anda hanya dapat menggunakannya sekali sehari.
Selain itu, pengguna premium akan mengetahui siapa Anda dan apa yang Anda unduh.
Anda mungkin diblokir jika Anda menyalahgunakan fitur ini.
    """

    @staticmethod
    def get_receive_link_text() -> str:
        reserved = get_func_queue("reserved")
        if ENABLE_CELERY and reserved:
            text = f"Tugas Anda telah ditambahkan ke antrean khusus {reserved}. Proses...\n\n"
        else:
            text = "Tugas Anda telah ditambahkan ke antrean aktif.\Mendownload...\n\n"

        return text

    @staticmethod
    def ping_worker() -> str:
        from tasks import app as celery_app

        workers = InfluxDB().extract_dashboard_data()
        # [{'celery@BennyのMBP': 'abc'}, {'celery@BennyのMBP': 'abc'}]
        response = celery_app.control.broadcast("ping_revision", reply=True)
        revision = {}
        for item in response:
            revision.update(item)

        text = ""
        for worker in workers:
            fields = worker["fields"]
            hostname = worker["tags"]["hostname"]
            status = {True: "✅"}.get(fields["status"], "❌")
            active = fields["active"]
            load = "{},{},{}".format(fields["load1"], fields["load5"], fields["load15"])
            rev = revision.get(hostname, "")
            text += f"{status}{hostname} **{active}** {load} {rev}\n"

        return text
