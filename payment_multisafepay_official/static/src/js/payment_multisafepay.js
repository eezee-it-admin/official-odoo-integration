/* global Accept */
odoo.define('payment_multisafepay_official.multisafepay', require => {
    'use strict';

    const core = require('web.core');
    const ajax = require('web.ajax');
    const { loadJS } = require('@web/core/assets');

    const checkoutForm = require('payment.checkout_form');
    const manageForm = require('payment.manage_form');
    const Qweb = core.qweb;
    const Dialog = require('web.Dialog');

    var ctx;


    const _t = core._t;
    // ajax.loadXML('/payment_multisafepay_scs/static/src/xml/payment_multisafepay_templates.xml', Qweb);

    const multisafeMixin = {

        events: Object.assign({}, checkoutForm.prototype.events, {
            'click .o_payment_option_card': 'updateNewPaymentDisplayStatus',
            'change input[name="multisafepay_pm_id"]': 'changeMultiSafepayAcquirerStatus',
            'change select[name="cc_multisafepay_pm_id"]': 'changeCreditCardMethod',
            'change select[name="ideal_issuer_id"]': 'changeIdealIssuer',
        }),

        changeIdealIssuer: function () {
            var select = this.$('select[name="ideal_issuer_id"]');
            var input = this.$('input[data-ideal-issuer="true"]')[0];
            input.setAttribute('data-issuer-id', select.val());
        },

        changeCreditCardMethod: function () {
            var select = this.$('select[name="cc_multisafepay_pm_id"]');
            var input = this.$('input[data-credit-card="true"]')[0];
            input.setAttribute('data-payment-method-id', select.val());
            input.setAttribute('data-multisafepay-aq', select.val());
            input.setAttribute('value', 'form_' + select.val());
        },

        changeMultiSafepayAcquirerStatus: function () {
            var checked_radio = this.$('input[name="multisafepay_pm_id"]:checked');
            if (checked_radio.length !== 1) {
                return;
            }
            var ideal_select = this.$('select[name="ideal_issuer_id"]')[0];
            var cc_select = this.$('select[name="cc_multisafepay_pm_id"]')[0];

            if (checked_radio[0].getAttribute('data-ideal-issuer') == 'true') {
                cc_select.setAttribute('hidden', '');
                 if (ideal_select !== undefined) {
                    ideal_select.removeAttribute('hidden', '');
                }
            } else if (checked_radio[0].getAttribute('data-credit-card') == 'true') {
                cc_select.removeAttribute('hidden', '');
                if (ideal_select !== undefined) {
                    ideal_select.setAttribute('hidden', '');
                }
            } else {
                if (cc_select !== undefined) {
                    cc_select.setAttribute('hidden', '');
                }
                if (ideal_select !== undefined) {
                    ideal_select.setAttribute('hidden', '');
                }
            }

            $('input[data-provider="multisafepay"]').prop("checked", true);
            this._enableButton();
        },

        updateNewPaymentDisplayStatus: function () {
            var checked_radio = this.$('input[name="pm_id"]:checked');
            if (checked_radio.data('provider') !== 'multisafepay') {
               $('input[name="multisafepay_pm_id"]').prop( "checked", false);
               $('input[name="multisafepay_pm_id"]').trigger("change");
            }
        },


        _prepareTransactionRouteParams: function (code, paymentOptionId, flow) {
            const transactionRouteParams = this._super(...arguments);

            return {
                ...transactionRouteParams,
                context: ctx,
            };
        },

        /**
         * Display an error in dialog. If MSP payment method is selected
         *
         * @private
         * @param {string} title - The title of the error
         * @param {string} description - The description of the error
         * @param {string} error - The raw error message
         * @return {Dialog} A dialog showing the error.
         */
        _displayErrorInMsp: function (title, description = '', error = '') {
            const $checkedRadios = this.$('input[name="multisafepay_pm_id"]:checked');
            this._enableButton(); // Enable button back after it was disabled before processing
            $('body').unblock(); // The page is blocked at this point, unblock it
            return new Dialog(null, {
                title: _.str.sprintf(_t("Error: %s"), title),
                size: 'medium',
                $content: `<p>${_.str.escapeHTML(description) || ''}</p>`,
                buttons: [{text: _t("Ok"), close: true}]
            }).open();
        },

        /**
         * Dispatch the secure data to MultiSafePay.
         *
         * @override method from payment.payment_form_mixin
         * @private
         * @param {string} provider - The provider of the payment option's provider
         * @param {number} paymentOptionId - The id of the payment option handling the transaction
         * @param {string} flow - The online payment flow of the transaction
         * @return {Promise}
         */
        _processPayment: function (provider, paymentOptionId, flow) {
            var checked_radio = this.$('input[name="multisafepay_pm_id"]:checked');

            if (checked_radio.length === 1 && checked_radio.data('form-payment') === 'True') {
                // checked_radio = checked_radio[0];
                var self = this;
                var provider_id = checked_radio.data('payment-option-id');
                // var acquirer_form = this.$('#o_payment_form_acq_' + acquirer_id);
                // var inputs_form = $('input', acquirer_form);
                // var ds = $('input[name="data_set"]', acquirer_form)[0];

                var method_id = this.$('input[name="multisafepay_pm_id"]:checked');
                var $tx_url = this.txContext.transactionRoute;
                var invoice_id = $('input[name="invoice_id"]')
                // if there's a prepare tx url set
                if ($tx_url !== null) {
                    // if the user wants to save his credit card info
                    // var form_save_token = acquirer_form.find('input[name="o_payment_form_save_token"]').prop('checked');
                    // then we call the route to prepare the transaction
                    ctx = this._getContext();
                    ctx = _.extend({}, ctx, {
                        "payment_method": method_id.data('payment-method-id'),
                        "issuer_id": method_id.data('issuer-id'),
                        "provider_id": parseInt(provider_id),
                    });
                    this._rpc({
                        route: $tx_url,
                        params: this._prepareTransactionRouteParams(provider, paymentOptionId, flow),
                    }).then(function (result) {
                        if (result) {
                            // if the server sent us the html form, we create a form element
                            var newForm = document.createElement('form');
                            newForm.setAttribute("method", "post"); // set it to post
                            newForm.setAttribute("target", "_top"); // Set the target attribute of the form to "_top"
                            newForm.setAttribute("provider", checked_radio[0].dataset.provider);
                            newForm.hidden = true; // hide it
                            newForm.innerHTML = result.redirect_form_html; // put the html sent by the server inside the form
                            var action_url = $(newForm).find('input[name="data_set"]').data('actionUrl');
                            newForm.setAttribute("action", action_url); // set the action url
                            $(document.getElementsByTagName('body')[0]).append(newForm); // append the form to the body
                            $(newForm).find('input[data-remove-me]').remove(); // remove all the input that should be removed
                            if(action_url) {
                                newForm.submit(); // and finally submit the form
                            }
                        }
                        else {
                            this._displayErrorInMsp(
                                _t('Server Error'),
                                _t("We are not able to redirect you to the payment form.")
                            );
                        }
                    }).guardedCatch(function (error) {
                        error.event.preventDefault();
                        self._displayErrorInMsp(
                            _t('Server Error'),
                            _t("We are not able to redirect you to the payment form.") +
                                error.message.data.message
                        );
                    });
                }
                else {
                    this._displayErrorInMsp(
                        _t("Cannot setup the payment"),
                        _t("We're unable to process your payment.")
                    );
                }
            } else {
                this._super.apply(this, arguments);
            }

        },


    };

    checkoutForm.include(multisafeMixin);
    manageForm.include(multisafeMixin);
});
