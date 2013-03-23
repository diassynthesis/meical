# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from osv import fields, osv
import addons
from tools.translate import _


class res_partner(osv.osv):
    _description = 'Partner'
    _name = "res.partner"
    _inherit = "res.partner"

    _columns = {
        'website':
            fields.related('address', 'website', type='char',
                                  string='Website', store=True),
        'phone2':
            fields.related('address', 'phone2', type='char', string='Phone 2',
                            store=True),
        'mobile2':
            fields.related('address', 'mobile2', type='char',
                           string='Mobile 2', store=True),
        'municipality_id':
            fields.related('address', 'municipality_id', type='many2one',
                           relation='medical.municipality',
                           string='Municipality',
                           domain="[('state_id','=',state_id)]"),
        }


    _defaults = {
      'customer': True,
    }

    def create(self, cr, uid, data, context={}):
        if not data.get('customer', False) and not data.get('supplier',
                                                              False):
            data['customer'] = True
        result = super(res_partner, self).create(cr, uid, data,
                                                   context=context)
        return result
res_partner()




class medical_partner_address_function(osv.osv):

    _name = "medical.partner.address.function"
    _columns = {
        'name': fields.char(_('Name'), size=64, required=True, select=True),
        'description': fields.char(_('Description'), size=250),
    }

medical_partner_address_function()

class res_partner_contact(osv.osv):
    _inherit = 'res.partner.contact'

    def onchange_birthdate(self, cr, uid, ids, birthdate=False):
        if birthdate:
            if date.today() < datetime.strptime(birthdate, '%Y-%m-%d').date():
                raise osv.except_osv(_('Invalid action !'), _('The Birthdate must be less than current date!'))
        return False

    _columns = {
        'contact_id':
            fields.many2one('medical.location', 'Location'),
        'mobile2':
            fields.char('Mobile 2', size=64),
        'phone':
            fields.char('Phone', size=64),
        'phone2':
            fields.char('Phone 2', size=64),
        'fax':
            fields.char('Fax', size=64),
        'birthdate':
            fields.datetime('Birthdate'),

        'function': fields.many2one('medical.partner.address.function',
                                    'Function', select=True),

        'birthdate':fields.date('Birthdate'),

        }

    def search(self, cr, uid, args, offset=0, limit=None, order=None,
               context=None, count=False):
        cr.execute('delete from res_partner_contact where last_name=%s', ('not defined contact name',))

        return super(res_partner_contact, self).search(cr, uid, args, offset, limit,
            order, context, count)
res_partner_contact()


class medical_municipality(osv.osv):
    _description = "Municipality"
    _name = 'medical.municipality'
    _columns = {
        'state_id': fields.many2one('res.country.state', 'State',
            required=True),
        'country_id':
            fields.related('state_id', 'country_id', type='many2one',
                           relation='res.country', string='Country'),
        'name': fields.char('Municipality Name', size=64, required=True),
        'code': fields.char('Municipality Code', size=3,
            help='The municipality code in three chars.\n', required=True),
    }

    def name_search(self, cr, user, name='', args=None, operator='ilike',
            context=None, limit=100):
        if not args:
            args = []
        if not context:
            context = {}
        ids = self.search(cr, user, [('code', 'ilike', name)] + args,
                    limit=limit, context=context)
        if not ids:
            ids = self.search(cr, user, [('name', operator, name)] + args,
                    limit=limit, context=context)
        return self.name_get(cr, user, ids, context)

    _order = 'code'
    _sql_constraints = [
        ('code_municipality_uniq', 'unique(code)',
         'The code must be unique per municipality!'), ]
medical_municipality()


class res_partner_location(osv.osv):
    _inherit = 'res.partner.location'
    _columns = {
        'number': fields.char('Number', size=128),
        'municipality_id': fields.many2one("medical.municipality", 'Municipality',
                                    domain="[('state_id','=',state_id)]"),
    }
res_partner_location()


class res_partner_address(osv.osv):
    _name = "res.partner.address"
    _inherit = "res.partner.address"

    _description = 'Partner Addresses'

    def create(self, cr, uid, data, context={}):
        cad = False
        result = False
        if data.get('first_name', False):
            cad = data.get('first_name', False)
            if data.get('last_name', False):
                cad = data.get('last_name', False) + ' ' + cad
        else:
            cad = _('not defined contact name')
        if cad:
            if not data.get('location_id', False):
                loc_id = self.pool.get('res.partner.location').create(cr, uid,
                            {'street': data.get('street', ''),
                            'street2': data.get('street2', ''),
                            'zip': data.get('zip', ''),
                            'number': data.get('number', ''),
                            'city': data.get('city', ''),
                            'country_id': data.get('country_id', False),
                            'state_id': data.get('state_id', False),
                            'municipality_id': data.get('municipality_id',
                                                        False)
                            }, context=context)
                data['location_id'] = loc_id
            if not data.get('contact_id', False):
                cont_id = self.pool.get('res.partner.contact').create(cr, uid,
                            {'phone': data.get('phone', ''),
                            'phone2': data.get('phone2', ''),
                            'mobile': data.get('mobile', ''),
                            'mobile2': data.get('mobile2', ''),
                            'name': cad,
                            'function': data.get('function', False),
                            'title': data.get('title', False),
                            'fax': data.get('fax', ''),
                            'first_name': data.get('first_name', ''),
                            'last_name': data.get('last_name', '') if\
                                 data.get('last_name', False) else cad,
                            'website': data.get('website', False),
                            'email': data.get('email', False),
                        }, context=context)
                data['contact_id'] = cont_id
            result = super(res_partner_address, self).create(cr, uid, data,
                                                   context=context)
        return result

    _columns = {
        #info associate to a contact place informations
        'location_id':
            fields.many2one('res.partner.location', 'Location'),
        'contact_id':
            fields.many2one('res.partner.contact', 'Contact'),

        # fields from location
        'street':
            fields.related('location_id', 'street', string='Street',
                           type="char", store=True, size=128),
        'street2':
            fields.related('location_id', 'street2', string='Street2',
                               type="char", store=True, size=128),
        'number':
            fields.related('location_id', 'number', string='Number',
                               type="char", store=True, size=128),
        'zip':
            fields.related('location_id', 'zip', string='Zip', type="char",
                           store=True, change_default=True, size=24),
        'city':
            fields.related('location_id', 'city', string='City', type="char",
                           store=True, size=128),
        'country_id':
            fields.related('location_id', 'country_id', type='many2one',
                        string='Country', store=True, relation='res.country'),
        'municipality_id':
            fields.related('location_id', 'municipality_id',
                           relation="medical.municipality", string='Municipality',
                           type="many2one", store=True,
                           domain="[('state_id','=',state_id)]"),
        'state_id':
            fields.related('location_id', 'state_id',
                           relation="res.country.state", string='State',
                           type="many2one", store=True,
                           domain="[('country_id','=',country_id)]"),
        'email':
            fields.related('contact_id', 'email', type='char', size=64,
                           string='E-Mail', store=True),
        'phone':
            fields.related('contact_id', 'phone', type='char', size=64,
                           string='Phone', store=True),
        'fax':
            fields.related('contact_id', 'fax', type='char', size=64,
                           string='Fax', store=True),
        'function':
            fields.related('contact_id', 'function', type='many2one',
                           relation="medical.partner.address.function", size=64,
                           string='Functions', store=True),
        'phone2':
            fields.related('contact_id', 'phone2', type='char', size=64,
                           string='Phone 2', store=True),
        'mobile2':
            fields.related('contact_id', 'mobile2', type='char', size=64,
                           string='Mobile 2', store=True),
        'website':
            fields.related('contact_id', 'website', type='char', size=64,
                           string='Website', store=True),

        'last_name': fields.related('contact_id', 'last_name', type='char',
                                    size=64, string='Last Name', store=True),

        'first_name': fields.related('contact_id', 'first_name', type='char',
                                     size=64, string='First Name', store=True),

        }

    def onchange_contact_id(self, cr, uid, ids, contact_id=False,
                             context={}):
        if not contact_id:
            return {}
        location = self.pool.get('res.partner.contact').browse(cr, uid,
                                                contact_id, context=context)
        return {'value': {
            'email': location.email,
            'phone2': location.phone2,
            'phone': location.phone,
            'mobile': location.mobile,
            'mobile2': location.mobile2,
            'function': location.function.id,
            'first_name': location.first_name,
            'last_name': location.last_name,
            'website': location.website,
            'name': location.name,
            'title': location.title and location.title.id or False,
        }}

    def onchange_location_id(self, cr, uid, ids, location_id=False,
                             context={}):
        if not location_id:
            return {}
        location = self.pool.get('res.partner.location').browse(cr, uid,
                                                location_id, context=context)
        return {'value': {
            'street': location.street,
            'street2': location.street2,
            'number': location.number,
            'zip': location.zip,
            'city': location.city,
            'country_id': location.country_id and location.country_id.id or\
                         False,
            'state_id': location.state_id and location.state_id.id or False,
            'municipality_id': location.municipality_id and\
                         location.municipality_id.id or False,
        }}

    def _default_location_id(self, cr, uid, context=None):
        if context is None:
            context = {}
        if not context.get('default_partner_id', False):
            return False
        ids = self.pool.get('res.partner.location').search(cr, uid,
                    [('partner_id', '=', context['default_partner_id'])],
                    context=context)
        return ids and ids[0] or False

    def _default_contact_id(self, cr, uid, context=None):
        if context is None:
            context = {}
        if not context.get('default_partner_id', False):
            return False
        ids = self.pool.get('res.partner.contact').search(cr, uid,
                    [('partner_id', '=', context['default_partner_id'])],
                    context=context)
        return ids and ids[0] or False


    def _display_address(self, cr, uid, address, context=None):
        '''
        The purpose of this function is to build and return an address formatted accordingly to the
        standards of the country where it belongs.

        :param address: browse record of the res.partner.address to format
        :returns: the address formatted in a display that fit its country habits (or the default ones
            if not country is specified)
        :rtype: string
        '''
        # get the address format
        address_format = address.country_id and address.country_id.address_format or\
                         '%(street)s\n%(street2)s\n%(city)s,%(state_code)s %(zip)s'
        # get the information that will be injected into the display format
        args = {
            'state_code': address.  state_id and address.state_id.code or '',
            'state_name': address.state_id and address.state_id.name or '',
            'country_code': address.country_id and address.country_id.code or '',
            'country_name': address.country_id and address.country_id.name or '',
            }
        address_field = ['title', 'street', 'street2', 'zip', 'city']
        for field in address_field :
            args[field] = getattr(address, field) or ''

        return address_format % args

    _defaults = {
        'location_id': _default_location_id,
        'contact_id': _default_contact_id
    }
res_partner_address()


class medical_location(osv.osv):
    _name = "medical.location"

    def create(self, cr, uid, data, context={}):
        if not data.get('location_id', False):
            loc_id = self.pool.get('res.partner.location').create(cr, uid, {
                'street': data.get('street', ''),
                'street2': data.get('street2', ''),
                'zip': data.get('zip', ''),
                'number': data.get('number', ''),
                'city': data.get('city', ''),
                'country_id': data.get('country_id', False),
                'state_id': data.get('state_id', False),
                'municipality_id': data.get('municipality_id', False)
            }, context=context)
            data['location_id'] = loc_id
        result = super(medical_location, self).create(cr, uid, data,
                                                   context=context)
        return result

    _columns = {
        'name':
                fields.char('Location', size=50, required=True),
       #info associate to a contact place informations
        'location_id':
            fields.many2one('res.partner.location', 'Location'),
        'contact_ids':
            fields.one2many('res.partner.contact', 'contact_id', 'Contact'),
        # fields from location
        'street':
            fields.related('location_id', 'street', string='Street',
                           type="char", store=True, size=128),
        'street2':
            fields.related('location_id', 'street2', string='Street2',
                               type="char", store=True, size=128),
        'number':
            fields.related('location_id', 'number', string='Number',
                               type="char", store=True, size=128),
        'zip':
            fields.related('location_id', 'zip', string='Zip', type="char",
                           store=True, change_default=True, size=24),
        'city':
            fields.related('location_id', 'city', string='City', type="char",
                           store=True, size=128),
        'municipality_id':
            fields.related('location_id', 'municipality_id',
                           relation="medical.municipality", string='Municipality',
                           type="many2one", store=True,
                           domain="[('state_id','=',state_id)]"),
        'state_id':
            fields.related('location_id', 'state_id',
                           relation="res.country.state", string='Fed. State',
                           type="many2one", store=True,
                           domain="[('country_id','=',country_id)]"),
        'country_id':
            fields.related('location_id', 'country_id', type='many2one',
                        string='Country', store=True, relation='res.country'),
        }
    _sql_constraints = [
        ('name_locations_medical_uniq', 'unique(name)',
         'The name must be unique per Location!'), ]
medical_location()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
