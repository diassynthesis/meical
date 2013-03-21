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

from osv import osv, fields
from tools.translate import _
import tools


class res_company(osv.osv):
    _name = "res.company"
    _inherit = "res.company"
    _description = "medical company structure representations "

    def _members_list(self, cr, uid, ids, field, arg, context=None):
        res = {}
        for idd in ids:
            cr.execute('select id from hr_department where company_id=%s',
            (idd,))
            id_list = map(lambda x: x[0], cr.fetchall())
            id_list = self.pool.get('hr.department').browse(cr, uid, id_list)
            ilist = []
            for dpto in id_list:
                ilist += [d.id for d in dpto.employee_ids if d.id not in ilist]
            res[idd] = ilist
        return res

    def _department_list(self, cr, uid, ids, field, arg, context=None):
        res = {}
        for idd in ids:
            cr.execute('select id from hr_department where company_id=%s',
                       (idd,))
            id_list = map(lambda x: x[0], cr.fetchall())
            res[idd] = id_list
        return res

    def _get_address_data(self, cr, uid, ids, field_names, arg, context=None):
        """ Read the 'address' functional fields. """
        result = {}
        part_obj = self.pool.get('res.partner')
        address_obj = self.pool.get('res.partner.address')
        for company in self.browse(cr, uid, ids, context=context):
            result[company.id] = {}.fromkeys(field_names, False)
            if company.partner_id:
                address_data = part_obj.address_get(cr, uid,
                [company.partner_id.id], adr_pref=['default'])
                if address_data['default']:
                    address = address_obj.read(cr, uid,
                    address_data['default'], field_names, context=context)
                    for field in field_names:
                        result[company.id][field] = address[field] or False
        return result

    def _set_address_data(self, cr, uid, company_id, name,
        value, arg, context=None):
        """ Write the 'address' functional fields. """
        company = self.browse(cr, uid, company_id, context=context)
        if company.partner_id:
            part_obj = self.pool.get('res.partner')
            address_obj = self.pool.get('res.partner.address')
            address_data = part_obj.address_get(cr, uid,
            [company.partner_id.id], adr_pref=['default'])
            address = address_data['default']
            if address:
                address_obj.write(cr, uid, [address], {name: value or False})
            else:
                address_obj.create(cr, uid, {name: value or False,
                'partner_id': company.partner_id.id}, context=context)
        return True

    _columns = {
        'code':
            fields.char('Code', size=5, help="Alphanumeric field, represent\
                         the identifier value of the structure on the\
                        application, it is an optional value"),
        'department_ids':
            fields.function(_department_list, string='Departments',
                            type='many2many', relation='hr.department'),
        'members_id':
            fields.function(_members_list, string='Employees',
                            type='many2many', relation='hr.employee'),
        'number':
            fields.function(_get_address_data, fnct_inv=_set_address_data,
                    size=8, type='char', string="Number", multi='address'),
        'municipality_id':
            fields.function(_get_address_data, fnct_inv=_set_address_data,
                    type='many2one', domain="[('state_id','=',state_id)]",
                    relation='medical.municipality', string="Municipality",
                    multi='address'),
        'vat':
            fields.related('partner_id', 'vat', string="Tax ID", type="char",
                help="Value Added Tax number. Check the box if the partner \
                is subjected to the VAT. Used by the VAT legal statement.",
                 size=32),
        'phone':
            fields.function(_get_address_data, fnct_inv=_set_address_data,
                    size=64, type='char', string="Phone", multi='address'),
        'website':
            fields.function(_get_address_data, fnct_inv=_set_address_data,
                    size=64, type='char', string="Website", multi='address'),
        'phone2':
            fields.function(_get_address_data, fnct_inv=_set_address_data,
                    size=64, type='char', string="Phone 2", multi='address'),
    }

    def on_change_header(self, cr, uid, ids, phone, phone2, phone3, email,
        fax, website, vat, reg=False, context=None):
        val = []
        if phone:
            val.append(_('Phone: ') + phone)
        if phone2:
            val.append(_('Phone 2: ') + phone2)
        if fax:
            val.append(_('Fax: ') + fax)
        if website:
            val.append(_('Website: ') + website)
        if vat:
            val.append(_('VAT: ') + vat)
        if reg:
            val.append(_('Reg: ') + reg)
        return {'value': {'rml_footer1': ' | '.join(val)}}

    _header_main = """
    <header>
        <pageTemplate>
            <frame id="first" x1="1.3cm" y1="2.5cm" height="%s"
            width="19.0cm"/>
                <pageGraphics>
                    <!-- You Logo - Change X,Y,Width and Height -->
                    <image x="1.3cm" y="%s" height="40.0" >[[ company.logo or
                    removeParentNode('image') ]]</image>
                    <setFont name="DejaVu Sans" size="8"/>
                    <fill color="black"/>
                    <stroke color="black"/>
                    <lines>1.3cm %s 20cm %s</lines>

                    <drawRightString x="20cm" y="%s">[[ company.rml_header1 ]]
                    </drawRightString>

                    <drawString x="1.3cm" y="%s">[[ company.partner_id.name ]]
                    </drawString>
                    <drawString x="1.3cm" y="%s">[[ company.partner_id.address
                    and company.partner_id.address[0].street or  '' ]
                    </drawString>
                    <drawString x="1.3cm" y="%s">[[ company.partner_id.address
                    and company.partner_id.address[0].zip or '' ]]
                    [[ company.partner_id.address and company.partner_id.
                    address[0].city or '' ]] - [[ company.partner_id.address
                    and company.partner_id.address[0].country_id and company.
                    partner_id.address[0].country_id.name  or '']]</drawString>
                    <drawString x="1.3cm" y="%s">Phone:</drawString>
                    <drawString x="1.3cm" y="%s">Phone 2:</drawString>
                    <drawRightString x="7cm" y="%s">[[ company.partner_id.
                    address and company.partner_id.address[0].phone or '' ]]
                    </drawRightString>
                    <drawRightString x="7cm" y="%s">[[ company.partner_id.
                    address and company.partner_id.address[0].phone2 or '' ]]
                    </drawRightString>
                    <drawRightString x="7cm" y="%s">[[ company.partner_id.
                    address and company.partner_id.address[0].phone3 or '' ]]
                    </drawRightString>
                    <drawString x="1.3cm" y="%s">Mail:</drawString>
                    <drawRightString x="7cm" y="%s">[[ company.partner_id.
                    address and company.partner_id.address[0].email or '' ]]
                    </drawRightString>
                    <lines>1.3cm %s 7cm %s</lines>

                    <!--page bottom-->

                    <lines>1.2cm 2.15cm 19.9cm 2.15cm</lines>

                    <drawCentredString x="10.5cm" y="1.7cm">[[ company.
                    rml_footer1 ]]</drawCentredString>
                    <drawCentredString x="10.5cm" y="1.25cm">[[ company.
                    rml_footer2 ]]</drawCentredString>
                    <drawCentredString x="10.5cm" y="0.8cm">Contact :
                    [[ user.name ]] - Page: <pageNumber/></drawCentredString>
            </pageGraphics>
        </pageTemplate>
    </header>"""
    _sql_constraints = [
        ('code_structure_uniq', 'unique(code)',
         'The code must be unique per company!'), ]
res_company()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
