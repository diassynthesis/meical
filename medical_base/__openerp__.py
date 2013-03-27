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
    'name': 'medical',
    'version': '1.0',
    'author': 'medical S.A.',
    'category': '?',
    "website": "http://www.medical.com",
    "depends": ['base', 'account', 'resource', 'hr', 'base_contact',
                'project'],
    "description": """ Modules for medical administration. Base component""",
    "init_xml": [
#        'data/medical.country.state.csv',
#        'data/medical.municipality.csv',
                 ],
    "update_xml": [
        'view/medical_menu.xml',
        'view/medical_locations_view.xml',
        'view/medical_structure_base_menu.xml',
        'view/medical_person_view.xml',
        ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
    'application': False
}
