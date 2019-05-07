# EB Draw Script by Alex Gompper
# May 6 2019
# Contact: https://twitter.com/edzart

import requests
import re
import urllib3
import json
import threading

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


HEADERS = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/73.0.3683.103 Safari/537.36',
    'content-type': 'application/x-www-form-urlencoded'
}

STRIPE_PUB_KEY = 'pk_live_u42h9k3kHDcKpj3DjgyIXjc7'


class EBDraw(threading.Thread):
    def __init__(self):
        super().__init__()
        self.s = requests.Session()
        self.s.verify = False
        self.s.headers = HEADERS
        self.size = None
        self.product_id = None
        self.customer_id = None
        self.email = None
        self.password = None
        self.first_name = None
        self.last_name = None
        self.address = None
        self.city = None
        self.state = None
        self.zip = None
        self.phone = None
        self.variant_id = None
        self.entry_id = None
        self.card_number = None
        self.card_exp_m = None
        self.card_exp_y = None
        self.card_cvc = None
        self.card_token = None

        print('*'*80)
        print('EB DRAW SCRIPT BY ALEX GOMPPER @EDZART'.center(80))
        print('*'*80)

    def load_config(self):
        try:
            with open('config.json') as config_file:
                config = json.load(config_file)
        except IOError:
            print('[err] unable to open config.json file')
            exit(-1)

        self.email = config['email']
        self.password = config['password']
        self.size = config['size']
        self.phone = config['phone']
        self.card_number = config['card_number']
        self.card_exp_m = config['card_exp_m']
        self.card_exp_y = config['card_exp_y']
        self.card_cvc = config['card_cvc']
        self.product_id = config['product_id']

    def get_customer_id(self):
        # takes the user/pass of a user and gathers their customer id
        print('logging into account {}'.format(self.email))
        # login to the account
        r = self.s.post(
            url='https://shop.extrabutterny.com/account/login',
            data={
                'form_type': 'customer_login',
                'utf8': '✓',
                'customer[email]': self.email,
                'customer[password]': self.password
            }
        )
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            print('[err] bad status logging into shopify account {}'.format(r.status_code))
            exit(-1)
        print('getting account id and address details')
        r = self.s.get(
            url='https://shop.extrabutterny.com/account'
        )
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            print('[err] bad status while finding customer id {}'.format(r.status_code))
            exit(-1)
        try:
            self.customer_id = re.findall('"customerId":(.*?)}}', r.text)[0]
            self.first_name = re.findall('"first_name":"(.*?)"', r.text)[0]
            self.last_name = re.findall('"last_name":"(.*?)"', r.text)[0]
            self.address = re.findall('"address1":"(.*?)"', r.text)[0]
            self.city = re.findall('"city":"(.*?)"', r.text)[0]
            self.state = re.findall('"province_code":"(.*?)"', r.text)[0]
            self.zip = re.findall('"zip":"(.*?)"', r.text)[0]
            # extra butter doesnt save phone numbers with addresses i guess so we gotta input that manually
        except IndexError:
            print('[err] couldnt find customer id and/or address details')
            exit(-1)
        print('found customer id {}'.format(self.customer_id))
        print('found customer name {} {}'.format(self.first_name, self.last_name))
        print('found address {} {} {} {}'.format(self.address, self.city, self.state, self.zip))
        return True

    def get_size(self):
        # get the draw id associated with the product id
        print('getting size {} variant for draw'.format(self.size))
        r = self.s.get(
            url='https://eb-draw.herokuapp.com/draws/{}'.format(self.product_id),
        )
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            print('[err] bad status while fetching draw variants')
            exit(-1)
        j = r.json()
        for variant in j[0]['variants']:
            if str(self.size) == variant['variant_label']:
                self.variant_id = variant['id']
        if not self.variant_id:
            print('[err] couldnt find an available size {} in variants'.format(self.size))
            exit(-1)
        print('found variant {} for size {}'.format(self.variant_id, self.size))
        return True

    def make_entry(self):
        # submit an entry
        print('making a new entry')
        r = self.s.post(
            url='https://eb-draw.herokuapp.com/draws/entries/new',
            data={
                'shipping_first_name': self.first_name,
                'shipping_last_name': self.last_name,
                'customer_id': self.customer_id,
                'variant_id': self.variant_id,
                'street_address': self.address,
                'zip': self.zip,
                'state': self.state,
                'phone': self.phone,
                'country': 'United States',
                'delivery_method': 'online'
            }
        )
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            if r.status_code == 422:
                print('[err] entry already exists')
            else:
                print('[err] bad status code while making new entry {}'.format(r.status_code))
            exit(-1)
        j = r.json()
        self.entry_id = j['id']
        print('got new entry id {}'.format(self.entry_id))
        return True

    def tokenize_card(self):
        # submit card to stripe
        print('tokenizing card with stripe')
        r = self.s.post(
            url='https://api.stripe.com/v1/tokens',
            data={
                'card[number]': self.card_number,
                'card[cvc]': self.card_cvc,
                'card[exp_month]': self.card_exp_m,
                'card[exp_year]': self.card_exp_y,
                'payment_user_agent': 'stripe.js/7c311245; stripe-js-v3/7c311245',
                'referrer': 'https://shop.extrabutterny.com/products/eb-ts',
                'key': STRIPE_PUB_KEY
            }
        )
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            print('[err] bad status while tokenizing card {}'.format(r.status_code))
            exit(-1)
        j = r.json()
        self.card_token = j['id']
        print('got card token {}'.format(self.card_token))
        return True

    def finalize_entry(self):
        # finish up
        print('finalizing entry')
        r = self.s.post(
            url='https://eb-draw.herokuapp.com/draws/entries/checkout',
            data={
                'checkout_token': self.card_token,
                'entry_id': self.entry_id
            }
        )
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            print('[err] bad status while finalizing entry {}'.format(r.status_code))
            print(r.text)
            exit(-1)
        print('successfully entered')

    def run(self):
        self.load_config()
        self.get_customer_id()
        self.get_size()
        self.make_entry()
        self.tokenize_card()
        self.finalize_entry()


E = EBDraw()
E.start()
