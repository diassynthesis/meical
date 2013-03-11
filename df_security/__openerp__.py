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


{
    'name': 'df_security',
    'version': '1.0',
    "author": "Desoft S.A.",
    "website": "http://www.df.com",
    'category': '?',
    'depends': ['base'],
    "description": """ df Security Tools """,
    'init_xml': [],
    'update_xml': [		         															
			'security/df_security_security.xml',
			'security/ir.model.access.csv',
            'view/df_security_view.xml',
            'data/df_data_type_generation.xml'
        ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
    'js' : ['static/src/js/resource.js'],
    #'certificate': '0071515601309',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
