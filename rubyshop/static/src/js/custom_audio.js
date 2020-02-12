odoo.define('ecc_approval_process.FormController', function (require) {
    "use strict";
    var config = require('web.config');
    var core = require('web.core');
    var dom = require('web.dom');
    var FormControler = require('web.FormController');
    var WebFormRenderer = require('web.FormRenderer');
    var _t = core._t;
    var qweb = core.qweb;

    $(()=>{
        var tracking_code_count_id = document.getElementsByName('tracking_code_count');
        var loopCount = 0;
        var iid = setInterval(function() {
                    
            if (tracking_code_count_id && tracking_code_count_id.length){
                tracking_code_count_id[0].addEventListener("change",function(){
                    console.log('testdata');
                    var myAudio = document.getElementById('myAudio');
                    myAudio.play();
                });
                var tracking_code_count_not_found = document.getElementsByName('tracking_code_not_found')[0];
                tracking_code_count_not_found.addEventListener("change",function(){
                    console.log('testdata2');
                    var myAudio1 = document.getElementById('myAudio1');
                    myAudio1.play();
                });
                if (iid) clearInterval(iid);
            }else{
                tracking_code_count_id = document.getElementsByName('tracking_code_ids')
                if (loopCount++ > 30 && iid) clearInterval(iid);
            }
        },100);
    });

    FormControler.include({
        /**
         * @override
         */

        init: function (parent, model, renderer, params) {
            this._super.apply(this, arguments);
            var _self = this;
            var d = this.model.get(this.handle);
            if (d && (d.model=='set.order.to.delivered' || d.model=='set.order.to.returned') && d.viewType=='form') {
                var myAudio = $('#myAudio')
                if (!myAudio || myAudio.length==0) {
                    $('body').append('<audio id="myAudio" src="/rubyshop/static/src/sounds/bomb-has-been-defused-csgo-sound-effect.mp3" type="audio/mpeg"></audio>');                    
                    $('body').append('<audio id="myAudio1" src="/rubyshop/static/src/sounds/bomb-has-been-planted-sound-effect-cs-go.mp3" type="audio/mpeg"></audio>');                    
                }
                // var tracking_code_count_id = document.getElementsByName('tracking_code_ids')
                // console.log("delta:", tracking_code_count_id)
                // var loopCount = 0;
                // var iid = setInterval(function() {
                    
                //     if (tracking_code_count_id && tracking_code_count_id.length){
                //         console.log('data')
                //         var count = tracking_code_count_id[0];
                //         count.addEventListener("change",function(){
                //             var x = document.getElementsByName('tracking_code_count')[0]
                //             console.log('count: ',x.innerText);
                            
                //         });
                //         if (iid) clearInterval(iid);
                //     }else{
                //         tracking_code_count_id = document.getElementsByName('tracking_code_ids')
                //         if (loopCount++ > 30 && iid) clearInterval(iid);
                //     }
                // },100);
                
                
                // tracking_code_count_id.addEventListener("change", function(){
                //     return _onchange_function();
                // });
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

        // _updateEnv: function () {
        //     this._super.apply(this, arguments);
        //     var rec = (this.isDirty() && this.model && this.model.get(this.handle)) || null;
        //     var recData = this.model.localData[rec.id];
        //     console.log('change: ',recData._changes)
        // },
    });

});