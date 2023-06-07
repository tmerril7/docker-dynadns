import argparse
import logging
from logging.handlers import RotatingFileHandler
import requests
import time
import json
import telegram

loggerFile = '/var/log/dynamic_dns.log'
logger = logging.getLogger("Rotating Log")
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(loggerFile, maxBytes=500000, backupCount=4)
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

parser = argparse.ArgumentParser(description='monitor external IP address')
parser.add_argument('cloudflare_token', type=str,
                    help='api token from cloudflare')
parser.add_argument('zone_id', type=str, metavar='zone_id', help='Zone ID')
parser.add_argument('dns_id', type=str, metavar='dns_id', help='DNS ID')
parser.add_argument('dns_name', type=str, metavar='dns_name', help='DNS Name')
parser.add_argument('primary_check_url', type=str,
                    help='Primary url to check IP address')
parser.add_argument('bot_token', type=str, help='Bot token')
parser.add_argument('chat_id', type=str, help='Chat ID')
# parser.add_argument('secondary_check_url', type=str,
#                     help='Secondary url to check IP address')


args = parser.parse_args()

bot = telegram.Bot(token=args.bot_token)
logger.info('bot token: %s' % args.bot_token)
bot.send_message(chat_id=args.chat_id,
                 text='dynamic DNS online for %s' % args.dns_name)
logger.info('dynamic DNS online for %s' % args.dns_name)


def check_external_ip():
    url = args.primary_check_url
    ret = requests.get(url)
    logger.info('external ip is: ' + ret.text)
    return ret.text


def check_dns_record():
    hd1 = {'Content-Type': 'application/json',
           'Authorization': 'Bearer ' + args.cloudflare_token}

    data1 = {'name': args.dns_name}
    url1 = 'https://api.cloudflare.com/client/v4/zones/' + args.zone_id + '/dns_records'
    ret1 = requests.get(url1, json=data1, headers=hd1, params=data1)
    print(ret1.text)

    logger.info('DNS record for ' + args.dns_name +
                ' is ' + json.loads(ret1.text)['result'][0]['content'])

    return json.loads(ret1.text)['result'][0]['content']


def update_record(record):
    hd = {'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + args.cloudflare_token}
    url = 'https://api.cloudflare.com/client/v4/zones/' + \
        args.zone_id + '/dns_records/' + args.dns_id
    data = {'content': record, 'name': args.dns_name,
            'proxied': False, 'type': 'A'}
    ret = requests.put(url, json=data, headers=hd)
    js = json.loads(ret.text)
    print(js)
    logger.info('Update Success = ' +
                str(js['success']) + ' : ' + js['result']['content'])
    bot.send_message(chat_id=args.chat_id, text='DNS record for ' +
                     args.dns_name + ' changed to ' + js['result']['content'])
    return js['success']


while True:
    if check_dns_record() != check_external_ip():
        time.sleep(3)
        update_record(check_external_ip())
    else:
        logger.info('IP match')
    time.sleep(5*60)
