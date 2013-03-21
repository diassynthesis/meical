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


class resource_resource(osv.osv):
    _name = "resource.resource"
    _inherit = "resource.resource"

    _description = "resource"

    _columns = {
        'name':
                fields.char("Name", size=64, required=True),
        'user_id':
                fields.many2one('res.users', 'User', help='Related user name\
                                 for the resource to manage its access.'),
        'code':
                fields.char('Code', size=16, required=True),
        'resource_type':
                fields.selection([('user', 'Human'), ('material', 'Material'),
                                  ('local', 'Local'), ('external',
                                   'External')], 'Resource Type',
                                  required=True),
        'location_id':
                fields.many2one('jaf.location', 'Location', help="Locations\
                        and contacts of the local's owner"),
        'local_id':
                fields.many2one('jaf.resource.local', 'Local'),
        'partner_id':
                fields.many2one('res.partner', 'Supplier',
                                domain="[('supplier', '=', 'True')]"),
        'general_descriptions':
            fields.text('General descriptions',
                        help="General descriptions of resources code."),
        'department_id':
                fields.many2one('hr.department', 'Department',
                                 ondelete='cascade'),
        'photo':
                fields.binary('Photo'),
        'company_id':
                fields.many2one('res.company', 'Company'),
        'technical_state':
            fields.selection([('neither', 'Neither'), ('in_using', 'In using'),
                ('broke', 'Broke'), ('on_reparation', 'On reparation'),
                ('others', 'Others')], 'Technical state', required=True,
                help="The different technical state of an active"),
        'fabrication_year':
                fields.integer('Fabrication year'),
        'responsible_id':
                fields.many2one('hr.employee', 'Responsible',
                                domain="[('department_id', '=',\
                                        department_id)]"),
        }

    _defaults = {
        'resource_type': 'user',
        'technical_state': 'in_using',
        'time_efficiency': 1,
        'active': True,
        'company_id': lambda self, cr, uid,
            context: self.pool.get('res.company')._company_default_get(cr, uid,
                                        'resource.resource', context=context)
    }
    _sql_constraints = [
        ('code_resource_uniq', 'unique(code)',
         'The code must be unique per resource!'), ]
resource_resource()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
