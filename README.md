<p align="center">
  <img src="https://www.multisafepay.com/img/multisafepaylogo.svg" width="400px" position="center">
</p>

# MultiSafepay plugin Odoo 16 eCommerce 

Easily integrate MultiSafepay payment solutions into your Odoo 16 eCommerce webshop with the free and completely new MultiSafepay Odoo 16 eCommerce plugin.

## About MultiSafepay ##
MultiSafepay is a collecting payment service provider which means we take care of the agreements, technical details and payment collection required for each payment method. You can start selling online today and manage all your transactions from one place.


## What is Odoo 16 eCommerce?
Odoo is an open source software founded in 2004 by a student. Firstly known as OpenERP, the brand changed its focus from an ERP solution to a suite of business applications. More than 360 apps are available thanks to the multiple developments made by Odoo S.A. and its community. Some of these apps are officially validated by Odoo, whereas others developed by the community are dedicated to specific versions for specific needs.

Odoo is available in three editions: Community, Enterprise, and Online. The Community edition can be downloaded free of charge via the Odoo website. The Enterprise edition offers more features but comes with a yearly cost. The Online offer is the equivalent of the Enterprise version but hosted in the cloud and monthly billed. For this comparison, we choose to compare the Enterprise edition.


##  Requirements
1.  in order to use the plugin you need a MultiSafepay account. 
You can create a test account on [MultiSafepay Control](https://testmerchant.multisafepay.com/signup)
2.  Odoo 16.0
3.  Tested on Python 3.6

##  Installation
1. Download ZIP archive with module
2. Unpack the content of the .ZIP file and add _payment_multisafepay_official_ folder under your custom apps in your Odoo server
   (`/mnt/extra-addons/`)
3. Install the required Python dependencies.
    ```shell
    pip3 install -r requirements.txt
    ```
    Alternatively, you can install them manually by doing
    ```shell
    pip3 install multisafepay==0.3.0
    ```
    You can find all the information about the dependencies at this [link](https://pypi.org/project/multisafepay/)
4.  Restart Odoo server
5.  Activate developer mode at Odoo platform
6.  Navigate to Apps menu and click __Update Apps List__
7.  Search and open MultiSafepay payments module (payment_multisafepay_official)
8.  Click __Install__
  
##  Update
1.  Navigate to Apps menu
2.  Search and open MultiSafepay payments module
3.  Click __Upgrade__
  
##  Configuration
Configuration is possible within the _Invoicing_ menu or the _Website_ menu.
1.  Navigate to Invoicing/Website menu and go to Configuration -> Payment Acquirers
2.  Select _MultiSafepay_ payment acquirer. Go to __Edit__ mode. By default acquirer state is disabled.
3.  Change state, _Enabled_ or _Test_, and enter _Live_ and/or _Test_ _API Key_, set Journal at Configuration tab, and save changes.
4.  Click __Pull payment methods__ at Configuration tab to get payment methods from your MultiSafepay account.
    
    Be sure that you have the desired payment methods active in your [MultiSafepay Control](https://testmerchant.multisafepay.com)
5.  Configure payment methods you wish to offer. Each payment method will have to be configured separately. 
    
You can configure name, state, supported currency, country, and customer group, which are appropriate for this payment method.

For some payment methods editing country and/or order amount is __disabled__. The reason is this payment method supported 
only in certain countries or it has amount limits.

Also, some payment methods process transactions only in __EUR__. 
For these payment methods, if the order was created not in euros, the amount will be __converted__ to the required currency. 
__Odoo platform currency rate__ is used for conversions and it is configured by a system administrator.
    
##  Using

####   Create order
1.  Select the desired payment method at _the checkout page_ and click __Pay now__.
2.  Enter additional params (for example, bank account), if required, and confirm payment.
3.  Message __Order { order ID } Confirmed__ means that the transaction was completed.

####     Complete order
1.  Navigate to Website menu. Go to Orders -> Orders and select needed order.
2.  Go to __Delivery__ and __Validate__ transfer to mark the order as _Shipped_.

    After that status of the transaction at _MultiSafepay_ changes to __Shipped__, 
    delivery info was set.
3.  Now, in order details, you can create an invoice. It will be __paid__, right away after being posted, as the order was prepaid.
4.  If you want to update invoice ID of the transaction at _MultiSafepay_, you should go to Configuration -> Payment transactions,
select the needed transaction and click __Update invoice ID__.

####    Refund order
At Odoo platform you can refund only fully completed order. 

1.  Go to Order invoices and click __Add Credit Note__ for creating refund invoice
2.  Enter __refund reason__ and check invoice lines, which you want to return. Click __Post__.
3.  Click __Refund with MultiSafepay__ to create a refund request.
4.  If the request was created successfully, invoice status will change.
5.  When refund transaction at MultiSafepay will be marked as _Completed_, refund invoice status will be changed to _Paid_.

#####   Refund with shopping cart
If the order was paid with _Klarna - Buy now, pay later_, _AfterPay_, _E-invoice_ or _Pay After Delivery_, refund will be made with refund with shopping cart.
In this case __item quantity__ can not be more than quantity in the original order and __item price__ must be equal to price in the original order.

__Note!__ Refund cannot be claimed for those payment methods, if any coupon or promo code was applied to the original order.

##  Supported Payment methods
-   [iDEAL](https://docs.multisafepay.com/payment-methods/banks/ideal/)
-   [SOFORT Banking](https://docs.multisafepay.com/payment-methods/banks/sofort-banking/)
-   [PayPal](https://docs.multisafepay.com/payment-methods/wallet/paypal/)
-   [Belfius](https://docs.multisafepay.com/payment-methods/banks/belfius/)
-   [ING HomePay](https://docs.multisafepay.com/payment-methods/banks/ing-home-pay/)
-   [KBC](https://docs.multisafepay.com/payment-methods/banks/kbc/)
-   [Alipay](https://docs.multisafepay.com/payment-methods/wallet/alipay/)
-   [Santander Consumer Finance | Pay per Month](https://docs.multisafepay.com/payment-methods/billing-suite/betaalpermaand/)
-   [Request to Pay powered by Deutsche Bank](https://docs.multisafepay.com/payment-methods/banks/request-to-pay/)
-   [AfterPay](https://docs.multisafepay.com/payment-methods/billing-suite/afterpay/)
-   [Pay After Delivery](https://docs.multisafepay.com/payment-methods/billing-suite/pay-after-delivery/)
-   [E-Invoicing](https://docs.multisafepay.com/payment-methods/billing-suite/e-invoicing/)
-   [Maestro](https://docs.multisafepay.com/payment-methods/credit-and-debit-cards/maestro/)
-   [EPS](https://docs.multisafepay.com/payment-methods/banks/eps/)
-   [Giropay](https://docs.multisafepay.com/payment-methods/banks/)
-   JCB
-   [BankTransfer](https://docs.multisafepay.com/payment-methods/banks/bank-transfer/)
-   [ApplePay](https://docs.multisafepay.com/payment-methods/wallet/applepay/)
-   [Bancontact](https://docs.multisafepay.com/payment-methods/banks/bancontact/)
-   [Trustly](https://docs.multisafepay.com/payment-methods/banks/trustly/)
-   PayInAdvance
-   [Klarna - Buy now, pay later](https://docs.multisafepay.com/payment-methods/billing-suite/klarna/)
-   [SEPA Direct Debit](https://docs.multisafepay.com/payment-methods/banks/sepa-direct-debit/)
-   [MasterCard](https://docs.multisafepay.com/payment-methods/credit-and-debit-cards/mastercard/)
-   [Visa](https://docs.multisafepay.com/payment-methods/credit-and-debit-cards/visa/)
-   [American Express](https://docs.multisafepay.com/payment-methods/credit-and-debit-cards/american-express/)
-   [DotPay](https://docs.multisafepay.com/payment-methods/banks/dotpay/)


## Feedback
We look forward to receiving your input.
Have you seen an opportunity to change things for better? We invite you to create a pull request on GitHub.
Are you missing something and would like us to fix it? Suggest an improvement by sending us an [email](mailto:integration@multisafepay.com) or by creating an issue.

## Testing
Would you like to try out a working version of a Odoo 16 webshop? Reach out to our Integration team at <integration@multisafepay.com> and one of our colleagues will assist you in opening a test account, where you can install the MultiSafepay's latest Odoo 16 plugin and its current functionality.

## License
[MIT License](https://github.com/MultiSafepay/odoo/blob/develop/LICENSE)

## Want to be part of the team?
Are you a developer interested in working at MultiSafepay? [View](https://www.multisafepay.com/careers/#jobopenings) our job openings and feel free to get in touch with us.