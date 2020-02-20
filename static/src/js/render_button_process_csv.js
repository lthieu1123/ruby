odoo.define('ruby.custom_list_view', function (require) {
    'use strict';
    
    var Dialog = require("web.Dialog");
    var core = require("web.core");
    var _t = core._t;
    let ListController = require('web.ListController');
    ListController.include({
        renderButtons: function($node) {
            this._super.apply(this, arguments);
            if (this.$buttons && this.modelName == 'sale.order.management') {
                this.$buttons.find('.o_button_process_csv').on('click', this.proxy('redirect_to_process_csv'));
                this.$buttons.find('.o_button_process_sale_done').on('click', this.proxy('redirect_to_process_sale_done'));
                this.$buttons.find('.o_button_reconcile').on('click', this.proxy('redirect_to_reconcile'));
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
                var msg_type = data.messages[0].type
                var msg = data.messages[0].message
                var message = "";
                msg.forEach(function(item,idx,array){
                    if(idx === array.length-1){
                        message+= item;
                    }else{
                        message+= item+" | ";
                    }
                })
                Dialog.alert(this, msg,{
                $content: $("<main/>", {
                    role: "alert",
                    text: message
                }),
                title: msg_type
                });
            })
        },

        redirect_to_process_sale_done: function(event){
            event.stopPropagation();
            event.preventDefault();
            return this._rpc({
                model: 'sale.order.management',
                method: 'btn_process_sale_done',
                args: [{}]
            }).then(function(data){
                var msg_type = data.messages[0].type
                var msg = data.messages[0].message
                var message = "";
                msg.forEach(function(item,idx,array){
                    if(idx === array.length-1){
                        message+= item;
                    }else{
                        message+= item+" | ";
                    }
                })
                Dialog.alert(this, msg,{
                $content: $("<main/>", {
                    role: "alert",
                    text: message
                }),
                title: msg_type
                });
            })
        },

        redirect_to_reconcile: function(event){
            event.stopPropagation();
            event.preventDefault();
            return this.do_action({
                name: 'Reconcile Date',
                type: 'ir.actions.act_window',
                view_type: 'form',
                view_mode: 'form',
                res_model: 'set.reconcile.date',
                views: [[false, 'form']],
                target: 'new',
                context: {}
            })
        },

    });

    core.action_registry.add('sale.order.management', ListController);
    // return the object.
    return ListController;
});