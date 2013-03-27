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
from tools.translate import _
from datetime import datetime, date

class medical_person(osv.osv):
    _name = "medical.person"
    _description = "Person"
    _rec_name = 'complete_name'

    def get_age(self, cr, uid, ids, birthdate=None):
        res = {}
        if birthdate:
            try:
                delta = date.today() - datetime.strptime(birthdate, '%Y-%m-%d').date()
                age = date.fromordinal(delta.days).year - 1
                res.update({'age': age })
                return {'value' : res}
            except:
                pass
        return {'value':{'age':0}}

    def _get_age(self, cr, uid, ids, name, arg, context=None):
        res = {}
        if not ids:
            return res
        for obj in self.browse(cr, uid, ids, context):
            if obj.birthdate:
                delta = date.today() - datetime.strptime(obj.birthdate, '%Y-%m-%d').date()
                age = date.fromordinal(delta.days).year - 1
                res[obj.id] = age
            else:
                res[obj.id] = 0
        return res


    _columns = {
        'complete_name':fields.char('Name', size=64, required=True),
        'alias':fields.char('Alias', size=64),
        'gender':fields.selection([('Female', 'female'), ('Male', 'male')], 'Gender'),
        'age':fields.function(_get_age, type="integer", string='Age'),
        'birthdate':fields.date('Birthdate'),
        'passport':fields.char('No. passport', size=64),
        'expiration_date':fields.date('Expiration Date'),
        'license':fields.char('License', size=64),
        'observation':fields.text('Description'),
    }
    _defaults = {
        'age':  lambda *a: 0,
                }

    def _check_birthdate(self, cr, uid, ids):
        for person in self.browse(cr, uid, ids):
            if person.birthdate:
                if datetime.strptime(person.birthdate, '%Y-%m-%d').date() >= date.today():
                    raise osv.except_osv(_('Invalid Birthdate!'), _('The birthdate must be less than current date.'))
        return True

    _constraints = [(_check_birthdate, 'Invalid Birthdate!.The birthdate must be less than current date ', ['birthdate'])]

medical_person()
