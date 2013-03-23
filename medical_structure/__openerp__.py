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
    'name': 'medical_structure',
    'version': '1.0',
    'author': 'medical S.A.',
    'category': '?',
    "website": "http://www.medical.com",
    "depends": ['medical'],
    "description": """ Modules for structure administration """,
    "init_xml": [],
    "update_xml": [
         'view/medical_structure_view.xml',
         'view/medical_department_view.xml',
         'view/medical_employee_view.xml',
         'view/medical_tool_view.xml',
         'view/medical_local_view.xml',
         'view/medical_locations_view.xml',
         'view/medical_structure_menu.xml'
        ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
    'application': False,
}
