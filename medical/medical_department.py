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


class medical_project(osv.osv):
    _name = "project.project"
    _inherit = "project.project"

    _description = "project.project"
    _columns = {
        'department_id':
                fields.many2one('hr.department', 'Department'),
                }
medical_project()


class hr_department(osv.osv):
    _name = "hr.department"
    _inherit = "hr.department"

    def create(self, cr, uid, vals, context=None):
        vals.update({
                     'project_ids': [(0, 0, {'name': vals['name'], })],
            })
        res = super(hr_department, self).create(cr, uid, vals, context=context)
        return res

    def write(self, cr, uid, ids, vals, *args, **kwargs):
        if "name" in vals.keys():
            for dpto in self.browse(cr, uid, ids):
                if dpto.project_ids:
                    project_id = [idx for idx in dpto.project_ids if\
                                  idx.name == dpto.name][0].id
                    vals.update({
                     'project_ids': [(1, project_id, {'name': vals['name'], \
                                                       })], })
        return super(hr_department, self).write(cr, uid, ids, vals,
                                                *args, **kwargs)

    _columns = {
        'project_ids':
                fields.one2many('project.project', 'department_id', 'Project'),
        }
hr_department()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
