from odoo import models, fields, api, http
from odoo.exceptions import UserError
from multisafepay.client import Client
from .payment_icon import DEFAULT_VALUES, E_INVOICING_PAYMENT_METHOD
from .payment_icon import MultiSafepayPaymentIcon
import logging

_logger = logging.getLogger(__name__)


class MultiSafepayPaymentAcquirer(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[("multisafepay", "MultiSafepay")],
        ondelete={"multisafepay": "set default"},
    )
    multisafepay_api_key_test = fields.Char('MultiSafepay test api key', size=40)
    multisafepay_api_key_live = fields.Char('MultiSafepay live api key', size=40)

    @api.onchange('multisafepay_api_key_test')
    def _onchange_multisafepay_api_key_test(self):
        if self.multisafepay_api_key_test and len(self.multisafepay_api_key_test) != 40:
            raise UserError('An API key must be 40 characters long')

    @api.onchange('multisafepay_api_key_live')
    def _onchange_multisafepay_api_key_live(self):
        if self.multisafepay_api_key_live and len(self.multisafepay_api_key_live) != 40:
            raise UserError('An API key must be 40 characters long')

    def get_appropriate_payment_methods(self, amount, currency, partner):
        payment_method_list = []
        for icon in self.payment_icon_ids:
            if not icon.enabled:
                continue
            if icon.customer_group == 'logged-in' and not http.request.session.uid:
                continue
            if icon.customer_group == 'non-logged-in' and http.request.session.uid:
                continue
            eur = self.env.ref('base.EUR')
            amount_in_eur = currency._convert(float(amount), eur, self.company_id, fields.Date.today())
            if amount_in_eur > icon.max_amount or amount_in_eur < icon.min_amount:
                continue
            if icon.currency_ids and currency not in icon.currency_ids:
                continue
            payment_method_list.append(icon)
        return payment_method_list

    def pull_merchant_payment_methods(self):
        if self.state == 'disabled' or self.code != 'multisafepay':
            pass

        multisafepay_client = self.get_multisafepay_client()
        payment_methods = multisafepay_client.gateways.allgateways()

        if not payment_methods.get('success', False):
            error_message = payment_methods.get('error_info', 'Request failed')
            raise UserError(error_message)

        multisafepay_icon = self.env['payment.icon'].search([('title', 'ilike', 'MultiSafepay')], limit=1)

        for payment_icon in self.payment_icon_ids:
            payment_methods_ids = list(map(lambda method: method.get('id'), payment_methods.get('data', [])))
            if payment_icon.title \
                    and payment_icon.title != multisafepay_icon.title \
                    and payment_icon.title not in payment_methods_ids:
                payment_icon.unlink()

        payment_icon_ids = [multisafepay_icon.id]
        for payment_method in payment_methods.get('data', []):
            existed_icon = self.env['payment.icon'].search(
                [('title', '=', payment_method.get('id', '').upper())],
                limit=1)

            if existed_icon:
                payment_icon_ids.append(existed_icon.id)
                continue

            payment_icon = MultiSafepayPaymentIcon.create_multisafepay_icon(
                payment_method.get('id', ''),
                self.env,
                self.code
            )
            payment_icon_ids.append(payment_icon.id)

        existing_generic_icon = self.env['payment.icon'].search(
            [('is_generic_gateway', '=', payment_method.get('id', '').upper())], limit=1)

        if existing_generic_icon:
            payment_icon_ids.append(existing_generic_icon.id)
        else:
            generic_payment_icon = MultiSafepayPaymentIcon.create_multisafepay_icon(
                'GENERIC',
                self.env,
                self.code
            )
            payment_icon_ids.append(generic_payment_icon.id)

        self.write({'payment_icon_ids': payment_icon_ids})

        return {
            'name': 'MultiSafepay payment methods',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'payment.icon',
            'views': [(self.env.ref('payment_multisafepay_official.payment_icon_tree_view').id, 'tree'),
                      (self.env.ref('payment_multisafepay_official.payment_icon_form_view_multisafepay').id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': {},
            'domain': [('provider', '=', 'multisafepay')],
        }

    def get_api_key_by_state(self):
        if self.state == 'test':
            return self.multisafepay_api_key_test
        return self.multisafepay_api_key_live

    def get_modus_by_state(self):
        if self.state == 'test':
            return 'TEST'
        return 'LIVE'

    def get_ideal_issuers(self):
        multisafepay_client = self.get_multisafepay_client()
        ideal_issuers = multisafepay_client.ideal_issuers.get()

        if not ideal_issuers.get('success', False):
            return []

        return ideal_issuers.get('data', [])

    def build_order_body(self, data):
        gateway = self.get_gateway(payment_method_id=data['payment_method'])
        website = self.env['website'].search([('id', '=', data['website'])], limit=1)
        sale_order = self.env['sale.order'].sudo().browse(data['sale_order_id'])
        currency = self.__check_currency(gateway=gateway, current_currency=data['currency'])
        shopping_cart = self.__get_shopping_cart_with_checkout_options(sale_order, gateway, data['currency'])
        amount = self.__check_amount(gateway=gateway, current_amount=data['amount'], shopping_cart=shopping_cart)

        order_body = {
            'type': self.__get_order_type(gateway=gateway),
            'order_id': data['order_reference'].split('-')[0],
            'custom_info': {
                'transaction_reference': data['order_reference']
            },
            'currency': currency,
            'amount': round(amount) if isinstance(amount, (int, float)) else amount,
            'gateway': gateway,
            'description': 'Odoo Order Payment',
            'google_analytics': {
                'account': 'UA-XXXXXXXXX',
            },
            'manual': False,
            'gateway_info': {
                'birthday': '1970-07-10',
                'gender': 'female',
                'phone': data['phone'],
                'email': data['email'],
            },
            'payment_options': {
                'notification_url': data['base_url'] + '/payment/multisafepay/notification?type=notification',
                'redirect_url': data['base_url'] + '/payment/multisafepay/notification?type=redirect',
                'cancel_url': data['base_url'] + '/payment/multisafepay/notification?type=cancel',
                'close_window': True
            },
            'customer': {
                'locale': data['lang'],
                'ip_address': data['ip_address'],
                'first_name': data['first_name'],
                'last_name': data['last_name'],
                'address1': data['address'],
                'zip_code': data['zip_code'],
                'city': data['city'],
                'country': data['country'],
                'phone': data['phone'],
                'email': data['email'],
                'referrer': data['base_url'],
                'user_agent': data['user_agent'] if gateway != E_INVOICING_PAYMENT_METHOD else '',
                'house_number': data['address2'] if data['address2'] else '1A',
            },
            'plugin_info': {
                'shop': website.name,
                'plugin_version': '1.0',
                'shop_version': 'odoo 13.0',
                'shop_root_url': website.domain if website.domain else data['base_url'],
            },
        }
        if data['issuer']:
            order_body['gateway_info'] = {
                'issuer_id': data['issuer'],
            }
        return {**order_body, **shopping_cart}

    def get_gateway(self, payment_method_id):
        payment_method = self.env['payment.icon'].search([('id', '=', payment_method_id)], limit=1)
        if payment_method.title != 'MultiSafepay':
            return payment_method.title
        return ''

    def __check_currency(self, gateway, current_currency):
        if not DEFAULT_VALUES.get(gateway, {}).get('convert_to_eur', False):
            return current_currency
        return self.env.ref('base.EUR').name

    def __check_amount(self, gateway, current_amount, shopping_cart):
        if not DEFAULT_VALUES.get(gateway, {}).get('convert_to_eur', False):
            return current_amount

        items = shopping_cart.get('shopping_cart', {}).get('items', [])

        amount = 0
        for item in items:
            amount += item.get('quantity', 1.0) * item.get('unit_price', 0.00)
        return amount * 100

    def __check_unit_price(self, gateway, current_currency, current_price):
        if not DEFAULT_VALUES.get(gateway, {}).get('convert_to_eur', False):
            return current_price

        eur = self.env.ref('base.EUR')
        initial_currency = self.env.ref('base.' + current_currency.upper())
        return initial_currency._convert(float(current_price), eur, self.company_id, fields.Date.today(), round=False)

    @staticmethod
    def __get_order_type(gateway):
        if not gateway:
            return 'redirect'
        if DEFAULT_VALUES.get(gateway, {}).get('direct_supported', False):
            return 'direct'
        return 'redirect'

    @staticmethod
    def __get_tax_percentage(order_line, price_unit):
        tax_percentage = 0
        if not order_line:
            return tax_percentage

        if order_line.price_tax != 0 and price_unit != 0:
            tax_percentage = order_line.price_tax / (price_unit * order_line.product_uom_qty)
        return round(tax_percentage, 2)

    def __get_shopping_cart_with_checkout_options(self, sale_order, gateway, current_currency):
        if not sale_order:
            return []

        items = []
        alternate = [
            {
                'name': 'none',
                'rules': [
                    {
                        'rate': 0.00,
                    },
                ],
            }
        ]
        for order_line in sale_order.order_line:
            price_unit = order_line.price_total / order_line.product_uom_qty
            # tax_percentage = MultiSafepayPaymentAcquirer.__get_tax_percentage(order_line, price_unit)
            # tax_table_selector_name = 'TAX' + str(int(tax_percentage * 100)) if tax_percentage != 0 else 'none'
            price_unit = self.__check_unit_price(
                gateway=gateway,
                current_currency=current_currency,
                current_price=price_unit
            )

            items.append({
                'name': order_line.product_id.name,
                'description': order_line.name,
                'unit_price': price_unit,
                'quantity': order_line.product_uom_qty,
                'merchant_item_id': order_line.product_id.id,
                # 'tax_table_selector': tax_table_selector_name,
                'weight': {
                    'unit': order_line.product_id.weight_uom_name.upper(),
                    'value': order_line.product_id.weight,
                }
            })

            # tax_found = any(alternate_item.get('name') == tax_table_selector_name for alternate_item in alternate)
            # if not tax_found:
            #     alternate.append({
            #         'name': tax_table_selector_name,
            #         'rules': [
            #             {
            #                 'rate': tax_percentage,
            #             },
            #         ],
            #     })

        return {
            'shopping_cart': {
                'items': items,
            },
            'checkout_options': {
                'tax_tables': {
                    'alternate': alternate,
                },
            },
        }

    def get_multisafepay_client(self):
        multisafepay_client = Client()
        multisafepay_client.set_modus(self.get_modus_by_state())
        multisafepay_client.set_api_key(self.get_api_key_by_state())

        return multisafepay_client
