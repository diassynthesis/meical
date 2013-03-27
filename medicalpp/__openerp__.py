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
    'description' : """

About Medical
-------------
Medical is a multi-user, highly scalable, centralized Electronic Medical Record (EMR) and Hospital Information System for openERP.

Medical provides a free universal Health and Hospital Information System, so doctors and institutions all over the world, specially in developing countries will benefit from a centralized, high quality, secure and scalable system.


Medical at a glance:


    * Strong focus in family medicine and Primary Health Care

    * Major interest in Socio-economics (housing conditions, substance abuse, education...)

    * Diseases and Medical procedures standards (like ICD-10 / ICD-10-PCS ...)

    * Patient Genetic and Hereditary risks : Over 4200 genes related to diseases (NCBI / Genecards)

    * Epidemiological and other statistical reports

    * 100% paperless patient examination and history taking

    * Patient Administration (creation, evaluations / consultations, history ... )

    * Doctor Administration

    * Lab Administration

    * Medicine / Drugs information (vademécum)

    * Medical stock and supply chain management

    * Hospital Financial Administration

    * Designed with industry standards in mind

    * Open Source : Licensed under GPL 



Most of the action should occur at sourceforge, so check the main page http://sourceforge.net/projects/medical for the latest news and developer releases. 

""",
    "init_xml": [
#        'data/jaf.country.state.csv',
#        'data/jaf.municipality.csv',
                 ],
    "update_xml": [],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
    'application': True
}
