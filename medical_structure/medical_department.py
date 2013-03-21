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


class hr_department(osv.osv):
    _name = "hr.department"
    _inherit = "hr.department"

    _columns = {
        'category':
            fields.selection([('service', 'Service'),
                              ('administrative', 'Administrative'),
                              ('infrastructure', 'Infrastructure'),
                              ('others', 'Others')],
                             'Category', required=True),
        'employee_ids':
            fields.one2many('hr.employee', 'department_id', 'Employees'),
        'local_ids':
            fields.one2many('medical.resource.local', 'department_id',
                            'Locals'),
        'tool_ids':
            fields.one2many('medical.resource.tool', 'department_id',
                            'Resources'),
         }
    _defaults = {
        'category': 'service',
        }

    def _check_department_unique_name(self, cr, uid, ids, context=None):
        asset = self.browse(cr, uid, ids[0], context=context)
        count = self.search(cr, uid, [('name', '=', asset.name), ('id', '!=',
                    asset.id)], context=None, count=True)
        return count == 0
    _constraints = [
        (_check_department_unique_name, 'The name must be unique per\
                                         department!',
            ['name'])
        ]
    _sql_constraints = [
        ('name_departmentname_uniq', 'unique(name)',
         'The name must be unique per department!'), ]

hr_department()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
