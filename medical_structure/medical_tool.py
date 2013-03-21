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


class medical_tool_category(osv.osv):
    _name = "medical.tool.category"
    _description = "tool_category"

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

    def _dept_name_get_fnc(self, cr, uid, ids, prop, unknow_none,
                           context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)

    _columns = {
        'complete_name': fields.function(_dept_name_get_fnc,
                                         type="char", string='Name'),
        'name':
            fields.char('Name', size=100, required=True),
        'descriptions':
            fields.text('Descriptions',
                        help="Descriptions category."),
        'parent_id': fields.many2one('medical.tool.category',
                                     'Parent Category', select=True),
        'child_ids': fields.one2many('medical.tool.category', 'parent_id',
                                     'Child Categories'),
        }
medical_tool_category()


class medical_resource_tool(osv.osv):
    _name = "medical.resource.tool"
    _inherits = {"resource.resource": "resource_id"}
    _description = "tool"

    def unlink(self, cr, uid, ids, context=None):
        base_rec_list_id = [idd.resource_id.id for idd in self.browse(cr, uid,
                                                        ids, context=context)]
        result = super(medical_resource_tool, self).unlink(cr, uid, ids, context)
        self.pool.get('resource.resource').unlink(cr, uid, base_rec_list_id,
                                                  context)
        return result

    _columns = {
        'category_tool_id':
                fields.many2one('medical.tool.category', 'Resource category'),
        'resource_id':
                fields.many2one('resource.resource', 'Resource',
                                 ondelete='cascade', required=True),
        'technical_descriptions':
                fields.char('Technical description', 250),
        'trade_mark':
                fields.char('Trade mark', 50),
        }
    _defaults = {
        'resource_type': 'material',
        'time_efficiency': 1,
        'active': True,
        'company_id': lambda self, cr, uid,
            context: self.pool.get('res.company')._company_default_get(cr,
                                                 uid, 'resource.resource',
                                                 context=context)
    }
medical_resource_tool()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
