odoo.define('ruby.custom_list_view', function (require) {
    'use strict';

    const core = require('web.core');
    let ListController = require('web.ListController');
    ListController.include({
        renderButtons: function($node) {
            this._super.apply(this, arguments);
            if (this.$buttons && this.modelName == 'sale.order.management') {
                this.$buttons.find('.o_button_process_csv').on('click', this.proxy('redirect_to_process_csv'));
            }
        },

        redirect_to_process_csv: function(event) {
            event.stopPropagation();
            event.preventDefault();
            return this._rpc({
                model: 'sale.order.management',
                method: 'btn_process_csv',
                args: [{}]
            }).then(function(data){
                return console.log(data)
            })
        },

    });

    core.action_registry.add('sale.order.management', ListController);
    // return the object.
    return ListController;
});