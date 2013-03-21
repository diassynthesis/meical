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


class medical_location(osv.osv):
    _name = "medical.location"
    _inherit = "medical.location"

    def create(self, cr, uid, vals, context=None):
        location_id = super(medical_location, self).create(cr, uid,
                      vals, context=context)
        if "local_id" in vals.keys() and vals["local_id"]:
            context.update({"flat": True})
            self.pool.get('medical.resource.local').write(cr, uid,
                [vals["local_id"], ], {'location_id': location_id},
                context=context)
        return location_id

    def write(self, cr, uid, ids, vals, context=None):
        for idd in ids:
            r = super(medical_location, self).write(cr, uid,
                           idd, vals, context=context)
#            if "flat" not in context.keys():
            if "local_id" in vals.keys() and vals["local_id"]:
                context.update({"flat": True})
                self.pool.get('medical.resource.local').write(cr, uid,
                        [vals["local_id"], ], {'location_id': idd},
                        context=context)
            return r

    def onchange_local(self, cr, uid, ids, local_id=None, context=None):
        res = {}
        if local_id:
            local_obj = self.pool.get('medical.resource.local')
            local_obj = local_obj.browse(cr, uid, local_id)
            res.update({"is_rented": local_obj.is_rented})
            res.update({"department_id": local_obj.department_id.id})
        return {'value': res}

    _columns = {

        #info associate to a local's place
        'local_id':
                fields.many2one('medical.resource.local',
                            'Local associate'),
        'is_rented':
                fields.related('local_id', 'is_rented', type='boolean',
                            string='Is rented', readonly=True),
        'department_id':
                fields.related('local_id', 'department_id', type='many2one',
                            relation='hr.department', string='Department',
                            readonly=True,),
        }
medical_location()


class medical_resource_local(osv.osv):
    _name = "medical.resource.local"
    _inherits = {"resource.resource": "resource_id"}
    _description = "local"

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        reads = self.read(cr, uid, ids, ['name', 'parent_id'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1] + ' / ' + name
            res.append((record['id'], name))
        return res

    def _resources_list(self, cr, uid, ids, field, arg, context=None):
        res = {}
        for idd in ids:
            cr.execute('select id from resource_resource where\
                 local_id=%s', (idd,))
            id_list = map(lambda x: x[0], cr.fetchall())
            res[idd] = id_list
        return res

    def onchange_place(self, cr, uid, ids, location_id=None, context=None):
        res = {}
        if location_id:
            place_obj = self.pool.get('medical.location')
            place_obj = place_obj.browse(cr, uid, location_id)
            res.update({"place_name": place_obj.name})
            res.update({"contact_ids": [idd.id for idd in \
                                        place_obj.contact_ids]})
            res.update({"street": place_obj.street})
            res.update({"street2": place_obj.street2})
            res.update({"number_build": place_obj.number})
            res.update({"zip": place_obj.zip})
            res.update({"city": place_obj.city})
            res.update({"state_id": place_obj.state_id.id})
            res.update({"municipality_id": place_obj.municipality_id.id})
            res.update({"country_id": place_obj.country_id.id})
        return {'value': res}

    def create(self, cr, uid, vals, context=None):
        local_id = super(medical_resource_local, self).create(cr, uid,
                      vals, context=context)
        if "flat" not in context.keys():
            if "location_id" in vals.keys() and vals["location_id"]:
                self.pool.get('medical.location').write(cr, uid,
                                                  [vals["location_id"], ],
                        {'local_id': local_id}, context=context)
        return local_id

    def write(self, cr, uid, ids, vals, context=None):
        for idd in ids:
            r = super(medical_resource_local, self).write(cr, uid,
                           idd, vals, context=context)
            if "flat" not in context.keys():
                if "location_id" in vals.keys() and vals["location_id"]:
                    self.pool.get('medical.location').write(cr, uid,
                [vals["location_id"], ], {'local_id': idd}, context=context)
            return r

    def unlink(self, cr, uid, ids, context=None):
        base_rec_list_id = [idd.resource_id.id for idd in self.browse(cr, uid,
                                                        ids, context=context)]
        result = super(medical_resource_local, self).unlink(cr, uid, ids, context)
        self.pool.get('resource.resource').unlink(cr, uid, base_rec_list_id,
                                                  context)
        return result

    def _dept_name_get_fnc(self, cr, uid, ids, prop, unknow_none,
                           context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)

    _columns = {
        'complete_name': fields.function(_dept_name_get_fnc,
                                         type="char", string='Name'),
        'resource_id':
                fields.many2one('resource.resource', 'Resource',
                                 ondelete='cascade', required=True),
        'is_rented':
            fields.boolean('Is rented',
                           help="If a local or place is rented "),
        'number':
                fields.integer('No.'),
        'parent_id':
                fields.many2one('medical.resource.local',
                                     'Parent local', select=True),
        'child_ids':
                fields.one2many('medical.resource.local', 'parent_id',
                                     'Child locals'),
        'resources_ids':
            fields.function(_resources_list, string='Resources',
                            type='many2many', relation='resource.resource'),
        #colums associate to the place of the local
        'place_name':
                fields.related('location_id', 'name', type='char',
                            string='Place', store=True),
        'contact_ids':
                fields.related('location_id', 'contact_ids', type='many2many',
                       relation='res.partner.contact',
                       string='Contacts'),
        'street':
                fields.related('location_id', 'street', type='char',
                            string='Street', store=True),
        'street2':
                fields.related('location_id', 'street2', type='char',
                            string='Street 2', store=True),
        'number_build':
                fields.related('location_id', 'number', type='char',
                            string='Number', store=True),
        'zip':
                fields.related('location_id', 'zip', type='char',
                            string='Zip', store=True),
        'city':
                fields.related('location_id', 'city', type='char',
                            string='City', store=True),
        'country_id':
                fields.related('location_id', 'country_id', type='many2one',
                       relation='res.country', string='Country', store=True),
        'state_id':
                fields.related('location_id', 'state_id', type='many2one',
                       relation='res.country.state',
                       domain="[('country_id','=',country_id)]",
                       string='State', store=True),
        'municipality_id':
                fields.related('location_id', 'municipality_id', type='many2one',
                       relation='medical.municipality',
                       domain="[('state_id','=',state_id)]",
                       string='Municipality', store=True),
        }
    _defaults = {
        'resource_type': 'local',
        'time_efficiency': 1,
        'active': True,
        'company_id': lambda self, cr, uid,
            context: self.pool.get('res.company')._company_default_get(cr,
                                                 uid, 'resource.resource',
                                                 context=context)
    }

    def _check_local_unique_name(self, cr, uid, ids, context=None):
        asset = self.browse(cr, uid, ids[0], context=context)
        count = self.search(cr, uid, [('name', '=', asset.name), ('id', '!=',
                    asset.id)], context=None, count=True)
        return count == 0

    def _check_recursion(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        level = 100
        while len(ids):
            cr.execute('select distinct parent_id from medical_resource_local \
            where id IN %s', (tuple(ids),))
            ids = filter(None, map(lambda x: x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True

    _constraints = [
        (_check_recursion, 'Error ! You can not create recursive locals.',
         ['parent_id']),
        (_check_local_unique_name, 'The name must be unique per asset!',
            ['name'])
        ]
    _sql_constraints = [
        ('name_localname_uniq', 'unique(complete_name)',
         'The name must be unique per local!'), ]
medical_resource_local()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
