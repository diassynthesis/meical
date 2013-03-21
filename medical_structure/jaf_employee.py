# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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
from tools.translate import _
from datetime import datetime


class user(osv.osv):
    _name = "res.users"
    _inherit = "res.users"
    _description = "users"

    def create(self, cr, uid, vals, context=None):
        if context == None:
            context = {}
        context.update({"noshortcut": True})
        res = super(user, self).create(cr, uid, vals, context=context)
        if 'not_employe' not in context.keys():
            employee_poll = self.pool.get('hr.employee')
            context.update({"not_user": True})
            employee_poll.create(cr, uid, {'name': vals['name'],
                                    'user_id': res}, context=context)
        return res
user()


class hr_employee(osv.osv):
    _name = "hr.employee"
    _inherit = "hr.employee"
    _description = "employee"

    def create(self, cr, uid, vals, context=None):
        if context == None:
            context = {}
        if 'not_user' not in context.keys():
            user_poll = self.pool.get('res.users')
            if user_poll.search(cr, uid, [("login", "=", vals['name'])],
                            context=context, count=True) == 0:
                company_id = self.pool.get('res.users').browse(cr,
                                            uid, uid).company_id.id
                context.update({"not_employe": True})
                context.update({"noshortcut": True})
                user_id = user_poll.create(cr, uid, {'name': vals['name'],
                            'login': vals['name'],
                            'new_password': vals['name'],
                            'context_lang': context['lang'],
                            'company_id': company_id, },
                                       context=context)
                vals.update({
                        'user_id': user_id,
                    })
        if not vals.get('address_home_id', False):
            add_id = self.pool.get('res.partner.address').create(cr, uid, {
                'street': vals.get('street', ''),
                'street2': vals.get('street2', ''),
                'zip': vals.get('zip', ''),
                'number': vals.get('number', ''),
                'city': vals.get('city', ''),
                'country_id': vals.get('country_address_id', False),
                'state_id': vals.get('state_id', False),
                'municipality_id': vals.get('municipality_id', False),
                'phone': vals.get('work_phone', ''),
                'phone2': vals.get('other_phone', ''),
                'mobile': vals.get('mobile_phone', ''),
                'mobile2': vals.get('mobile2', ''),
                'title': vals.get('title', False),
                'fax': vals.get('fax', ''),
                'first_name': vals.get('name', False) if\
                         vals.get('name', False) else 'not defined',
                'last_name': vals.get('last_name', False) if\
                         vals.get('last_name', False) else 'not defined',
                'website': vals.get('website', False),
                'email': vals.get('work_email', False),
            }, context=context)
            vals['address_home_id'] = add_id
        res = super(hr_employee, self).create(cr, uid, vals, context=context)
        return res

    _columns = {
        'address_id': fields.many2one('res.partner.address',
                                        'Working Address'),
        'address_home_id': fields.many2one('res.partner.address',
                                           'Home Address'),
        'last_name':
            fields.char('Last Name', size=64),
        'partner_id': fields.related('address_id', 'partner_id',
                                     type='many2one', relation='res.partner'),
        'city': fields.related('address_home_id', 'city', type='char',
                               string='City', store=True),
        'website':
            fields.related('address_home_id', 'website', type='char',
                                  string='Website', store=True),
        'work_phone':
            fields.related('address_home_id', 'phone', type='char',
                           string='Work Phone', store=True),
        'other_phone':
            fields.related('address_home_id', 'phone2', type='char',
                           string='Other Phone', store=True),
        'mobile_phone':
            fields.related('address_home_id', 'mobile', type='char',
                           string='Mobile', store=True),
        'mobile2':
            fields.related('address_home_id', 'mobile2', type='char',
                           string='Mobile 2', store=True),
        'work_email':
            fields.related('address_home_id', 'email', type='char',
                           string='email', store=True),
        'fax':
            fields.related('address_home_id', 'fax', type='char',
                           string='Fax', store=True),
        'state_id':
            fields.related('address_home_id', 'state_id', type='many2one',
                           relation='res.country.state', string='State',
                           store=True),
        'municipality_id':
            fields.related('address_home_id', 'municipality_id',
                           type='many2one', relation='jaf.municipality',
                           string='Municipality', store=True),
        'title':
            fields.related('address_home_id', 'title', type='many2one',
                           relation='res.partner.title', string="Title",
                           store=True),
        'country_address_id':
            fields.related('address_home_id', 'country_id', type='many2one',
                           relation='res.country', string='Country',
                           store=True),
        'work_location':
            fields.many2one('jaf.location', 'Office Location'),
        'street':
            fields.related('address_home_id', 'street', string='Street',
                           type="char", store=True, size=128),
        'street2':
            fields.related('address_home_id', 'street2', string='Street2',
                               type="char", store=True, size=128),
        'number':
            fields.related('address_home_id', 'number', string='Number',
                               type="char", store=True, size=128),
        'zip':
            fields.related('address_home_id', 'zip', string='Zip', type="char",
                           store=True, change_default=True, size=24),
        }

    def write(self, cr, uid, ids, vals, context=None):
        if "name" in vals.keys():
            for user in self.browse(cr, uid, ids):
                if user.user_id:
                    company_id = self.pool.get('res.users').browse(cr,
                                            uid, uid).company_id.id
                    self.pool.get('res.users').write(cr, uid,
                                [user.user_id.id], {'name': vals['name'],
                            'login': vals['name'],
                            'new_password': vals['name'],
                            'context_lang': context['lang'],
                            'company_id': company_id, })
        obj = self.browse(cr, uid, ids[0], context)
        if obj.address_home_id:
            first_name = obj.address_home_id.first_name
            last_name = obj.address_home_id.last_name
            if 'name' in vals.keys():
                first_name = vals['name']
            if 'last_name' in vals.keys():
                last_name = vals['last_name']
            self.pool.get('res.partner.address').write(cr, uid,
                    obj.address_home_id.id, {'first_name': first_name,
                    'last_name': last_name}, context)
        return super(hr_employee, self).write(cr, uid, ids, vals,
                                                context=context)

    def onchange_address_home_id(self, cr, uid, ids, address, context=None):
        if address:
            address = self.pool.get('res.partner.address').browse(cr, uid,
                                                address, context=context)
            return {'value': {
                              'website': address.website,
                              'work_phone': address.phone,
                              'other_phone': address.phone2,
                              'mobile_phone': address.mobile,
                              'mobile2': address.mobile2,
                              'work_email': address.email,
                              'state_id': address.state_id.id,
                              'city': address.city,
                              'state_id': address.state_id.id,
                              'municipality_id': address.municipality_id.id,
                              'country_address_id': address.country_id.id,
                              'street': address.street,
                              'street2': address.street2,
                              'number': address.number,
                              'zip': address.zip, }}
        return {'value': {}}

    def _lang_get(self, cr, uid, context=None):
        obj = self.pool.get('res.lang')
        ids = obj.search(cr, uid, [], context=context)
        res = obj.read(cr, uid, ids, ['code', 'name'], context)
        return [(r['code'], r['name']) for r in res] + [('', '')]

    def _contrains_old(self, cr, uid, ids):
        obj = self.browse(cr, uid, ids[0])
        return obj.birthday < datetime.strftime(datetime.today(), '%Y-%m-%d')

    _constraints = [
        (_contrains_old, "The employee's old year must be less than today",
         ['birthday']),
    ]
hr_employee()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
