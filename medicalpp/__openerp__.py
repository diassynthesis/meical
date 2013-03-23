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
    'name': 'Open-Medical',
    'version': '1.0',
    'author': 'Eloquentia Solutions S.A de CV',
    'category' : 'Medical verticalization',
    'images': ['images/medical.png'],
    "website": "http://www.eloquentia.simart.dtdns.net/",
    "depends": ['medical', 'medical_structure', 'medical_genetics', 'medical_lifestyle', 'medical_socioeconomics'],
    "description": """ Modules medical app""",
    "init_xml": [
#        'data/jaf.country.state.csv',
#        'data/jaf.municipality.csv',
                 ],
    "update_xml": [
        ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
    'application': True
}
