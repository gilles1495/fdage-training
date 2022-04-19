odoo.define('faal_tempo.faal_contact', function (require) {
    'use strict';

    var FieldMany2One = require('web.relational_fields').FieldMany2One;
    var core = require('web.core');
    var field_registry = require('web.field_registry');

    var _t = core._t;

    var FaalContact = FieldMany2One.extend({
        /**
         * @private
         */
        _renderReadonly: async function () {
            if(this.value && this.value.data.id !== undefined){
                var rpc = require('web.rpc');

                var res_partner_id = this.value.data.id;
                var self = this;
                await rpc.query({
                    route: '/get_res_partner_information/',
                    params: {'res_partner_id': res_partner_id}
                }).then(function (data) {
                    var data_name = data.name ;
                    if(data_name === undefined){
                        data_name = ''
                    }
                    if(data.title !== '') {
                        data_name = data.title + ' ' + data_name
                    }
                    var data_email = data.email
                    if(data_email === undefined){
                        data_email = ''
                    }
                    var data_phone = data.phone
                    if(data_phone === undefined){
                        data_phone = ''
                    }
                    self.data_line = '<span>'+ data_name +'</span>'
                    if(data_email){
                        self.data_line +='<br><span>'+ data_email +'</span>'
                    }
                    if(data_phone){
                        self.data_line += '<br><span>Téléphone : '+ data_phone +'</span>'
                    }
                })

                this.$el.html(self.data_line);
                if (!this.noOpen && this.value) {
                    this.$el.attr('href', _.str.sprintf('#id=%s&model=%s', this.value.res_id, this.field.relation));
                    this.$el.addClass('o_form_uri');
                }
            }
        },
    });

    var FaalClientContact = FieldMany2One.extend({
        /**
         * @private
         */
        _renderReadonly: async function () {
            if(this.value && this.value.data.id !== undefined){
                var rpc = require('web.rpc');

                var res_partner_id = this.value.data.id;
                var self = this;
                await rpc.query({
                    route: '/get_res_partner_information/',
                    params: {'res_partner_id': res_partner_id}
                }).then(function (data) {
                    if(data.ref){
                        self.data_line ='<span></span><span>'+ data.ref +'</span>'
                    }
                    if(data.name) {
                        if(self.data_line){
                            self.data_line += '<br/><span class="first-child-trigger">' + data.name + '</span>'
                        }else{
                            self.data_line = '<span>' + data.name + '</span>'
                        }
                    }
                    if(data.street){
                        self.data_line +='<br><span>'+ data.street +'</span>'
                    }
                    if(data.street2){
                        self.data_line +='<br><span>'+ data.street2 +'</span>'
                    }
                    var data_city_zip = ''
                    if(data.zip){
                        data_city_zip += data.zip + ' '
                    }
                    if(data.city){
                        data_city_zip += data.city
                    }
                    if(data_city_zip){
                        self.data_line += '<br><span>'+ data_city_zip +'</span>'
                    }
                })

                this.$el.html(self.data_line);
                if (!this.noOpen && this.value) {
                    this.$el.attr('href', _.str.sprintf('#id=%s&model=%s', this.value.res_id, this.field.relation));
                    this.$el.addClass('o_form_uri');
                }
            }
        },
    });

    var FaalClientAdressContact = FieldMany2One.extend({
        /**
         * @private
         */
        _renderReadonly: async function () {
            if(this.value && this.value.data.id !== undefined){
                var rpc = require('web.rpc');

                var res_partner_id = this.value.data.id;
                var self = this;
                await rpc.query({
                    route: '/get_res_partner_information/',
                    params: {'res_partner_id': res_partner_id}
                }).then(function (data) {
                    self.data_line = '<span>' + data.name + '</span>'

                    if(data.street){
                        self.data_line +='<br><span>'+ data.street +'</span>'
                    }
                    if(data.street2){
                        self.data_line +='<br><span>'+ data.street2 +'</span>'
                    }
                    var data_city_zip = ''
                    if(data.zip){
                        data_city_zip += data.zip + ' '
                    }
                    if(data.city){
                        data_city_zip += data.city
                    }
                    if(data_city_zip){
                        self.data_line += '<br><span>'+ data_city_zip +'</span>'
                    }
                })

                this.$el.html(self.data_line);
                if (!this.noOpen && this.value) {
                    this.$el.attr('href', _.str.sprintf('#id=%s&model=%s', this.value.res_id, this.field.relation));
                    this.$el.addClass('o_form_uri');
                }
            }
        },
    });

    field_registry.add('faal_client_render', FaalClientContact);
    field_registry.add('faal_client_address_render', FaalClientAdressContact);
    field_registry.add('faal_contact', FaalContact);

    return FaalContact;
});
