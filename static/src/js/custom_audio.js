odoo.define('ecc_approval_process.FormController', function (require) {
    "use strict";
    var core = require('web.core');
    var FormControler = require('web.FormController');
    var _t = core._t;
    var qweb = core.qweb;

    FormControler.include({
        /**
         * @override
         */

        init: function (parent, model, renderer, params) {
            this._super.apply(this, arguments);
            var _self = this;
            var d = _self.model.get(this.handle);
            if (d && (d.model=='set.order.to.delivered' || d.model=='set.order.to.returned') && d.viewType=='form') {
                var myAudio = $('#audioFound')
                if (!myAudio || myAudio.length==0) {
                    $('body').append('<audio id="audioFound" src="/ruby/static/src/sounds/co.mp3" type="audio/mpeg"></audio>');                    
                    $('body').append('<audio id="audioNotFound" src="/ruby/static/src/sounds/khong.mp3" type="audio/mpeg"></audio>');                    
                }
                var tracking_code_count_id = document.getElementsByName('tracking_code_ids');
                var loopCount = 0;
                var handler = {};
                handler.old_value = 0;

                var iid = setInterval(function() {
                    if (tracking_code_count_id && tracking_code_count_id.length){
                        // tracking_code_count_id[0].addEventListener('focusin', function(){
                        //     console.log("Saving value " + $(this).val());
                        //     $(this).data('val', $(this).val());
                        // });
                        tracking_code_count_id[0].addEventListener("change",function(){
                            var current = $(this).val();
                            var _model = d.model;
                            _self._rpc({
                                model: _model,
                                method: "find_order",
                                args: [
                                    {
                                    order_number: current
                                    }
                                ]
                            }).then(function(isFound){
                                console.log('isFound: ',isFound);
                                if (isFound){
                                    var e = document.getElementById("audioFound");
                                    e.play();
                                }else{
                                    var e = document.getElementById("audioNotFound");
                                    e.play();
                                }
                            })
                            // console.log('this: ',handler.old_value);
                            // var data = document.getElementsByName('tracking_code_count')[0];
                            // console.log('data: ',data.innerText);
                            // var myAudio = document.getElementById('myAudio');
                            // myAudio.play();
                        });
                        if (iid) clearInterval(iid);
                    }else{
                        tracking_code_count_id = document.getElementsByName('tracking_code_ids')
                        if (loopCount++ > 30 && iid) clearInterval(iid);
                    }
                },100);
            }
        },
        
        
        

        // /**
        //  * @override
        //  */
        // start: function () {
        //     var _self = this;
        //     var _super = _self._super.bind(this);
        //     var _args = arguments;
        //     return $.when(
        //         _self._rpc({ model: "ecc.approval.status", method: "get_action_id", args: [{}] }).then(function (_id) {
        //             WebFormRenderer.approvalButtonId = _id;
        //         }).fail(function (err) { console.log("ERROR: ", err); })
        //     ).then(function () {
        //         return _super.apply(_self, _args)
        //     })
        // },

        _updateEnv: function () {
            this._super.apply(this, arguments);
            var _super = this._super.bind(this);
            var _self = this;
            var d = _self.model.get(this.handle);
            if (d && (d.model=='set.order.to.delivered' || d.model=='set.order.to.returned') && d.viewType=='form') {
                var myAudio = $('#audioFound')
                if (!myAudio || myAudio.length==0) {
                    $('body').append('<audio id="audioFound" src="/ruby/static/src/sounds/co.mp3" type="audio/mpeg"></audio>');                    
                    $('body').append('<audio id="audioNotFound" src="/ruby/static/src/sounds/khong.mp3" type="audio/mpeg"></audio>');
                    $('body').append('<audio id="audioDuplicate" src="/ruby/static/src/sounds/trung.mp3" type="audio/mpeg"></audio>');
                    $('body').append('<audio id="audioUsed" src="/ruby/static/src/sounds/da_nhap.mp3" type="audio/mpeg"></audio>');                    
                }
                var tracking_code_count_id = document.getElementsByName('tracking_code_ids');
                var loopCount = 0;
                var handler = {};
                handler.old_value = 0;

                var iid = setInterval(function() {
                    if (tracking_code_count_id && tracking_code_count_id.length){
                        // tracking_code_count_id[0].addEventListener('focusin', function(){
                        //     console.log("Saving value " + $(this).val());
                        //     $(this).data('val', $(this).val());
                        // });
                        tracking_code_count_id[0].addEventListener("change",function(){
                            var current = $(this).val();
                            var changes = _self.model.localData[d.id];
                            var _model = d.model;
                            console.log("d: ",d);
                            _self._rpc({
                                model: _model,
                                method: "find_order",
                                args: [
                                    {
                                    order_number: current
                                    }
                                ]
                            }).then(function(result){
                                var _res = result.result
                                if (isFound){
                                    var e = document.getElementById("audioFound");
                                    e.play();
                                }else{
                                    var e = document.getElementById("audioNotFound");
                                    e.play();
                                }
                            })
                            // console.log('this: ',handler.old_value);
                            // var data = document.getElementsByName('tracking_code_count')[0];
                            // console.log('data: ',data.innerText);
                            // var myAudio = document.getElementById('myAudio');
                            // myAudio.play();
                        });
                        if (iid) clearInterval(iid);
                    }else{
                        tracking_code_count_id = document.getElementsByName('tracking_code_ids')
                        if (loopCount++ > 30 && iid) clearInterval(iid);
                    }
                },100);
            }
        },
    });

});