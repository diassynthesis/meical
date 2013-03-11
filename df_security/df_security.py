# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    Copyright (C) 2010-2011 Akretion (www.akretion.com). All Rights Reserved
#    @author Sebatien Beau <sebastien.beau@akretion.com>
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
#      update to use a single "Generate/Update" button & price computation code
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import openerp
from openerp.modules import module as modulemanager
from openerp.modules.module import loaded

import os
import base64

from osv import fields, osv
from osv.orm import MetaModel as MetaModel


class df_security_typegeneration(osv.osv_memory):
    _name = 'df.security.typegeneration'
    _columns = {
        'name':
            fields.char('Name', size=60, required=True),
    }

df_security_typegeneration()


class df_security_group(osv.osv_memory):
    _name = 'df.security.group'
    _columns = {
        'group_id':
            fields.many2one('res.groups', 'Group'),
        'name':
            fields.char('Name', size=1000),
        'type':
            fields.many2one('df.security.typegeneration', 'Generation type'),
        'menus_ids':
            fields.many2many('ir.ui.menu', 'df_security_menu'),
        'module_id':
            fields.many2one('ir.module.module', 'Module', required=True),
        'new_group':
            fields.boolean('New group'),
        'groups_inherits':
            fields.many2many('res.groups', 'df_security_groupinherits'),
        'data':
            fields.binary('File', readonly=True),
        'filename':
            fields.char('Filename', 16),
        'state':
            fields.selection([('choose', 'choose'), ('get', 'get')], 'State'),
    }

    def on_changemodule(self, cr, uid, ids, module_id):
        return self.write(cr, uid, ids, {
                                'state': 'get', 'data': '',
                                'filename': '', 'group_id': [(6, 0, [])],
                                'name': '', 'type': [(6, 0, [])],
                                'groups_inherits': [(6, 0, [])],
                                'menus_ids': [(6, 0, [])],
                                'state': 'choose'}, None)

    def to_stringelement(self, idval, nameval, model_id_id, group_id_id,
                         perm_read, perm_write, perm_create, perm_unlink):
        elem = idval + ','
        elem += str(nameval) + ','
        elem += str(model_id_id) + ','
        elem += group_id_id + ','
        elem += str(perm_read) + ','
        elem += str(perm_write) + ','
        elem += str(perm_create) + ','
        elem += str(perm_unlink)
        return elem

    def loadmodulesuninstalled(self, cr, uid):
        domain = [('state', '=', 'uninstalled')]
        module_obj = self.pool.get('ir.module.module')
        uninstalled_ids = module_obj.search(cr, uid, domain)
        uninstalled_modules = module_obj.browse(cr, uid, uninstalled_ids)
        for unmobj in uninstalled_modules:
            modulemanager.load_openerp_module(unmobj.name)

    def modifyfileopenperp(self, dirextmod, namefilexml):
        info = modulemanager.load_information_from_description_file(dirextmod)
        terp = file(dirextmod + "/__openerp__.py", 'rw+')
        if info and terp:
            lines = terp.readlines()
            os.remove(dirextmod + "/__openerp__.py")
            terp.close()
            terp = file(dirextmod + "/__openerp__.py", 'wb+')
            i = 0
            for l in lines:
                if str(l).find("update_xml") != -1:
                    lines.insert(i + 1,
                                    "\t\t\t'security/" + namefilexml + "',\n")
                    lines.insert(i + 2,
                                    "\t\t\t'security/ir.model.access.csv',\n")
                    break
                i += 1
            terp.writelines(lines)
        terp.close()

    def getmodelforsecurity(self, cr, module, dirext, namegroup, uid,
                            writenamegroup=False, groupvalid_id=-1):
        self.loadmodulesuninstalled(cr, 1)

        #buscar el modulo de referencia de un modelo
        def findmodelref(model, b=False):
            modulmodels = openerp.osv.orm.MetaModel.module_to_models.iteritems()
            for k, modells in modulmodels:
                for md in modells:
                    namemodel = ""
                    if '_name' in md.__dict__.keys():
                        namemodel = md.__dict__['_name'].replace('.', '_')
                    else:
                        namemodel = md.__name__
                    mdkeys = md.__dict__.keys()
                    if namemodel == model and '_inherit' not in mdkeys:
                        return k
            return model.split('_')[0]

        def findnamemodelref(model, b=False):
            modulmodels = openerp.osv.orm.MetaModel.module_to_models.iteritems()
            for k, modells in modulmodels:
                for md in modells:
                    namemodel = ""
                    if '_name' in md.__dict__.keys():
                        namemodel = md.__dict__['_name'].replace('.', '_')
                    else:
                        namemodel = md.__name__
                    mdkeys = md.__dict__.keys()
                    if namemodel == model and '_inherit' not in mdkeys:
                        return md.__dict__['_name']
            return model.replace('_', '.')

        def findmodelkeys(metamodellist):
            reskeys = []
            for mc in metamodellist:
                reskeys.append(mc)
            return reskeys

        #verificar si al modelo hay algun acceso por una grupo
        def verifyaccesinmodel(model):
            if groupvalid_id != -1:
                model_obj = self.pool.get('ir.model')
                modelfind = model_obj.search(cr, 1, [('model', '=', model)])
                modelacc_obj = self.pool.get('ir.model.access')
                modelaccfind = modelacc_obj.search(cr, 1,
                                            [('model_id', '=', modelfind),
                                             ('group_id', '=', groupvalid_id)])
                if len(modelaccfind):
                    return True
            return False

        global loaded
        if module.name not in loaded:
            modulemanager.load_openerp_module(module.name)
        res = []
        reg = []

        for k, cls in openerp.osv.orm.MetaModel.module_to_models.iteritems():
            if k == module.name:
                metamodelskeys = findmodelkeys(cls)
                for mc in cls:
                    if '_name' in mc.__dict__.keys():
                        if verifyaccesinmodel(mc.__dict__['_name']):
                            continue
                    idval = "access_" + namegroup + "_" \
                                      + mc.__name__.replace('.', '_')
                    nameval = module.name + "_" + mc.__name__.replace('.', '_')
                    model_id_id = "model_" + mc.__name__.replace('.', '_')
                    group_id_id = "group_" + module.name \
                                    if writenamegroup == False else namegroup

                    #permisos del modelo
                    perm_read = 1
                    perm_write = 1
                    perm_create = 1
                    perm_unlink = 1

                    namemodl = ""
                    if '_name' in mc.__dict__.keys():
                        namemt = mc.__dict__['_name']
                        namemt = findnamemodelref(mc.__dict__['_name'])
                        namemodl = mc.__dict__['_name']
                    else:
                        namemodl = mc.__name__
                        namemt = findnamemodelref(mc.__name__.replace('_', '.'))

                    #caso para los modelos normales
                    if namemodl.replace('.', '_') not in reg:
                        mod = module.name
                        if '_inherit' in mc.__dict__.keys():
                            if not isinstance(mc.__dict__['_inherit'], list):
                                if namemodl.replace('.', '_') == mc.__dict__['_inherit'].replace('.','_'):                                
                                    mod = findmodelref(mc.__dict__['_inherit'].replace('.','_'))
                                    if mod <> module.name:
                                        nameval = mod+"_"+namemodl.replace('.', '_')
                                        model_id_id = mod+"."+model_id_id                                                                                                                                  
                                                                                                                                                                                                                                                
                            else:
                                
                                for inhel in mc.__dict__['_inherit']:
                                    
                                    if namemodl.replace('.', '_') == inhel.replace('.','_'):                                
                                        mod = findmodelref(inhel.replace('.','_'))
                                        if mod <> module.name:
                                            nameval = mod+"_"+namemodl.replace('.', '_')
                                            model_id_id = mod+"."+model_id_id                                                                                                                                  
                                        break
                                        
                        elem = self.to_stringelement(idval,nameval,model_id_id,group_id_id,perm_read,
                                                         perm_write,perm_create,perm_unlink) 
                        el = {'name':namemt,
                              'module':mod,
                              'perm_write':perm_write,
                              'perm_create':perm_create,
                              'perm_unlink':perm_unlink,
                              'perm_read':perm_read,}                      
                        res.append(el) 
                        reg.append(namemodl.replace('.', '_'))
                                       
                                    
                    
                    #samenamemodel = False 
                    #falta agregar los _inherit y los _inherits                                                                                                                                            
        
        for k, cls in openerp.osv.orm.MetaModel.module_to_models.iteritems():
            if k == module.name:
                metamodelskeys = findmodelkeys(cls)
                for mc in cls:
                    if '_inherit' in mc.__dict__.keys():
                      if not isinstance(mc.__dict__['_inherit'], list):       
                          inname = mc.__dict__['_inherit'].replace('.','_')   
                          if inname not in reg:
                              if inname not in reg and inname not in metamodelskeys :                              
                                  if verifyaccesinmodel(k):
                                     continue
                                  mod = findmodelref(mc.__dict__['_inherit'].replace('.','_'))
                                  #print "             modulo encontrado "+mod
                                  #filesreg.write("             modulo encontrado "+mod+"\r\n")
                                  if mod == module.name:
                                      mod = ''
                                      modm = ''
                                  else :   
                                      mod = mod+"."
                                      modm = mod.replace('.','_')                                  
                                  
                                  elemh = self.to_stringelement("access_"+namegroup+"_"+mc.__dict__['_inherit'].replace('.','_'),
                                                   modm+str(mc.__dict__['_inherit'].replace('.','_')),
                                                   mod+"model_"+mc.__dict__['_inherit'].replace('.','_'),
                                                   group_id_id,
                                                   1,0,0,0)
                                  print "revisar _inherit "+mc.__dict__['_inherit']
                                  el = {'name':mc.__dict__['_inherit'],
                                        'module':mod,
                                        'perm_write':0,
                                        'perm_create':0,
                                        'perm_unlink':0,
                                        'perm_read':1,}
                                  res.append(el)                                                        
                                  reg.append(mc.__dict__['_inherit'].replace('.','_'))
                                    
                      else:
                          for inhel in mc.__dict__['_inherit']:
                            inname = inhel.replace('.','_')   
                            if inname not in reg:
                              if inname not in reg and inname not in metamodelskeys :        
                                  if verifyaccesinmodel(k):
                                      continue      
                                  mod = findmodelref(inhel.replace('.','_'))
                                  if mod == module.name:
                                      mod = ''
                                      modm = ''
                                  else :   
                                      mod = mod+"."
                                      modm = mod.replace('.','_')                                  
                                  elemh = self.to_stringelement("access_"+namegroup+"_"+inhel.replace('.','_'),
                                                   modm+str(inhel.replace('.','_')),
                                                   mod+"model_"+inhel.replace('.','_'),
                                                   group_id_id,
                                                   1,0,0,0)
                                  el = {'name':inhel,
                                        'module':mod,
                                        'perm_write':0,
                                        'perm_create':0,
                                        'perm_unlink':0,
                                        'perm_read':1,}
                                  res.append(el)                                                        
                                  reg.append(inhel.replace('.','_'))
                                                 
        for k, cls in openerp.osv.orm.MetaModel.module_to_models.iteritems():
            if k == module.name:
                metamodelskeys = findmodelkeys(cls)
                for mc in cls:
                    if '_inherits' in mc.__dict__.keys():
                      if len(mc.__dict__['_inherits']):
                          for k,inht in mc.__dict__['_inherits'].iteritems():
                              if verifyaccesinmodel(k):
                                      continue
                              inhs = k.replace('.','_')
                              if inhs not in reg and inhs not in metamodelskeys:        
                                  mod = findmodelref(inhs)
                                  if mod == module.name:
                                      mod = ''
                                      modm = ''
                                  else :   
                                      mod = mod+"."
                                      modm = mod.replace('.','_')      
                                  elemh = self.to_stringelement("access_"+namegroup+"_"+inhs,
                                                                modm+str(inhs),
                                                                mod+"model_"+inhs,
                                                                group_id_id,
                                                                1,0,0,0)
                                  el = {'name':k,
                                        'module':mod,
                                        'perm_write':0,
                                        'perm_create':0,
                                        'perm_unlink':0,
                                        'perm_read':1,}
                                  print "revisar _inherits "+k
                                  res.append(el)                                                                                                      
                                  reg.append(k.replace('.','_'))
                                  
                                  
        for k, cls in openerp.osv.orm.MetaModel.module_to_models.iteritems():
            if k == module.name:
                metamodelskeys = findmodelkeys(cls)
                for mc in cls:
                    if '_columns' in mc.__dict__.keys():        
                       for i,f in mc.__dict__['_columns'].iteritems():
                            if isinstance(f, fields.many2one):
                                if verifyaccesinmodel(f._obj):
                                      continue
                                many2onemodel = f._obj.replace('.', '_')
                                if many2onemodel not in reg:
                                    mod = findmodelref(many2onemodel)
                                    if mod == module.name:
                                        mod = ''
                                        modc = ''
                                    else :
                                        mod = mod+"."
                                        modc = mod.replace('.','_')   
                                    elem = self.to_stringelement("access_"+namegroup+"_"+many2onemodel,
                                                                 modc+many2onemodel,
                                                                 mod+"model_"+many2onemodel
                                                                 ,group_id_id,1,0,0,0)   
                                    
                                    print "revisar many2one "+many2onemodel
                                    el = {'name':many2onemodel.replace('_','.'),
                                          'module':mod,
                                          'perm_write':0,
                                          'perm_create':0,
                                          'perm_unlink':0,
                                          'perm_read':1,}                       
                                    res.append(el) 
                                    reg.append(many2onemodel)
        if len(res):            
            return res
        return []
    
    def registerfilecsvsecurity(self, cr, module, dirext,namegroup,uid,writenamegroup=False,groupvalid_id=-1):
                
        self.loadmodulesuninstalled(cr,1)    
        #buscar el modulo de referencia de un modelo
        def findmodelref(model,b=False):                    
            modulmodels = openerp.osv.orm.MetaModel.module_to_models.iteritems()    
            for k,modells in modulmodels:
                #if b :
                    #print "modulo del buscar "+k
                    #filesreg.write("modulo del buscar "+k+"\r\n")
                for md in modells:
                    
                 #   if b: 
                 #       print "               modelo del buscar "+md.__name__
                        #filesreg.write("               modelo del buscar "+md.
                        #__name__+"\r\n")
                        
                    namemodel = ""
                    if '_name' in md.__dict__.keys():                        
                        namemodel = md.__dict__['_name'].replace('.','_')
                        #filesreg.write("               si esta _name "+
                        #namemodel+"\r\n")
                    else : 
                        namemodel = md.__name__    
                    mdkeys = md.__dict__.keys()    
                    if namemodel == model and '_inherit' not in mdkeys:
                        #print "es este"                        
                        return k#md.__module__.split('.')[2]                        
            
            return model.split('_')[0]      
        
        def findmodelkeys(metamodellist):
            reskeys = []
            for mc in metamodellist:    
                reskeys.append(mc)
            return reskeys            
        
        #verificar si al modelo hay algun acceso por una grupo
        def verifyaccesinmodel(model):
            if groupvalid_id <> -1:
                model_obj = self.pool.get('ir.model')
                modelfind =  model_obj.search(cr, 1, [('model','=',model),])
                #modeldata = modeldata_obj_search.read(cr, 1, modelfind)            
                #print groupdata[0]['name']                               
                modelacc_obj = self.pool.get('ir.model.access')
                modelaccfind =  modelacc_obj.search(cr, 1, [('model_id','=',modelfind),('group_id','=',groupvalid_id),])
                if len(modelaccfind):
                    return True
            return False
        
        global loaded
        
        if module.name not in loaded:      
            modulemanager.load_openerp_module(module.name)
        
        res = []
        reg = []    
        
        for k, cls in openerp.osv.orm.MetaModel.module_to_models.iteritems():
            if k == module.name:
                metamodelskeys = findmodelkeys(cls)
                for mc in cls:
                    if '_name' in mc.__dict__.keys():
                        if verifyaccesinmodel(mc.__dict__['_name']):
                            continue
                    idval = "access_"+namegroup+"_"+mc.__name__.replace('.', 
                                                                        '_')
                    nameval = module.name+"_"+mc.__name__.replace('.', '_')
                    namemodelr = mc.__name__.replace('.', '_') if '_name' not in mc.__dict__.keys() else mc.__dict__['_name'].replace('.','_')                                           
                    model_id_id = "model_"+namemodelr
                    group_id_id = "group_"+module.name if writenamegroup == False else namegroup  
                        
                    #permisos del modelo             
                    perm_read = 1
                    perm_write = 1
                    perm_create = 1
                    perm_unlink = 1  
                    
                    namemodl = ""
                    if '_name' in mc.__dict__.keys():                        
                        namemodl = mc.__dict__['_name']
                    else : 
                        namemodl = mc.__name__  
                    
                    #caso para los modelos normales                                
                    #if samenamemodel == False and mc.__name__ not in reg:                        
                    #if mc.__name__ not in reg:
                    if namemodl.replace('.', '_') not in reg:
                        
                        if '_inherit' in mc.__dict__.keys():
                            if not isinstance(mc.__dict__['_inherit'], list):
                                
                                if namemodl.replace('.', '_') == mc.__dict__['_inherit'].replace('.','_'):                                
                                    mod = findmodelref(mc.__dict__['_inherit'].replace('.','_'))
                                    if mod <> module.name:
                                        nameval = mod+"_"+namemodl.replace('.', '_')
                                        model_id_id = mod+"."+model_id_id                                                                                                                                  
                                                                                                                                                                                                                                                
                            else:
                                
                                for inhel in mc.__dict__['_inherit']:
                                    
                                    if namemodl.replace('.', '_') == inhel.replace('.','_'):                                
                                        mod = findmodelref(inhel.replace('.','_'))
                                        if mod <> module.name:
                                            nameval = mod+"_"+namemodl.replace('.', '_')
                                            model_id_id = mod+"."+model_id_id                                                                                                                                  
                                        break
                                        
                        elem = self.to_stringelement(idval,nameval,model_id_id,group_id_id,perm_read,
                                                         perm_write,perm_create,perm_unlink)                          
                        res.append(elem) 
                        reg.append(namemodl.replace('.', '_'))
                                                                                               
                    #samenamemodel = False 
                    #falta agregar los _inherit y los _inherits                                                                                                                                            
        
        for k,cls in openerp.osv.orm.MetaModel.module_to_models.iteritems():
            if k == module.name:
                
                metamodelskeys = findmodelkeys(cls)
                for mc in cls:
                    if '_inherit' in mc.__dict__.keys():
                      if not isinstance(mc.__dict__['_inherit'], list):       
                          inname = mc.__dict__['_inherit'].replace('.','_')   
                          if inname not in reg:
                              if inname not in reg and inname not in metamodelskeys :                                
                                  if verifyaccesinmodel(k):
                                     continue        
                                  mod = findmodelref(mc.__dict__['_inherit'].replace('.','_'))
                                  if mod == module.name:
                                      mod = ''
                                      modm = ''
                                  else :   
                                      mod = mod+"."
                                      modm = mod.replace('.','_')                                  
                                  
                                  elemh = self.to_stringelement("access_"+namegroup+"_"+mc.__dict__['_inherit'].replace('.','_'),
                                                   modm+str(mc.__dict__['_inherit'].replace('.','_')),
                                                   mod+"model_"+mc.__dict__['_inherit'].replace('.','_'),
                                                   group_id_id,
                                                   1,0,0,0)
                                  res.append(elemh)                                                        
                                  reg.append(mc.__dict__['_inherit'].replace('.','_'))
                                    
                      else:       
                        for inhel in mc.__dict__['_inherit']:
                            inname = inhel.replace('.', '_')   
                            if inname not in reg:
                              if inname not in reg and inname not in metamodelskeys :        
                                  if verifyaccesinmodel(k):
                                      continue
                                  mod = findmodelref(inhel.replace('.','_'))
                                  if mod == module.name:
                                      mod = ''
                                      modm = ''
                                  else :   
                                      mod = mod+"."
                                      modm = mod.replace('.','_')                                  
                                  
                                  elemh = self.to_stringelement("access_"+namegroup+"_"+inhel.replace('.','_'),
                                                   modm+str(inhel.replace('.','_')),
                                                   mod+"model_"+inhel.replace('.','_'),
                                                   group_id_id,
                                                   1,0,0,0)
                                  res.append(elemh)                                                        
                                  reg.append(inhel.replace('.','_'))
                                                 
        for k, cls in openerp.osv.orm.MetaModel.module_to_models.iteritems():
            if k == module.name:
                metamodelskeys = findmodelkeys(cls)
                for mc in cls:
                    if '_inherits' in mc.__dict__.keys():
                      if len(mc.__dict__['_inherits']):
                          for k,inht in mc.__dict__['_inherits'].iteritems():
                              if verifyaccesinmodel(k):
                                      continue
                              inhs = k.replace('.','_')
                              if inhs not in reg and inhs not in metamodelskeys:        
                                  mod = findmodelref(inhs)
                                  if mod == module.name:
                                      mod = ''
                                      modm = ''
                                  else :   
                                      mod = mod+"."
                                      modm = mod.replace('.','_')    
                                  elemh = self.to_stringelement("access_"+namegroup+"_"+inhs,
                                                                modm+str(inhs),
                                                                mod+"model_"+inhs,
                                                                group_id_id,
                                                                1,0,0,0)
                                  res.append(elemh)                                                                                                      
                                  reg.append(k.replace('.','_'))
                                  
        for k, cls in openerp.osv.orm.MetaModel.module_to_models.iteritems():
            if k == module.name:
                metamodelskeys = findmodelkeys(cls)
                for mc in cls:
                    if '_columns' in mc.__dict__.keys():
                       for i,f in mc.__dict__['_columns'].iteritems():
                            if isinstance(f, fields.many2one):
                                if verifyaccesinmodel(f._obj):
                                      continue
                                many2onemodel = f._obj.replace('.', '_')
                                if many2onemodel not in reg:
                                    mod = findmodelref(many2onemodel)
                                    if mod == module.name:
                                        mod = ''
                                        modc = ''
                                    else :
                                        mod = mod+"."
                                        modc = mod.replace('.','_')   
                                    elem = self.to_stringelement("access_"+namegroup+"_"+many2onemodel,
                                                                 modc+many2onemodel,
                                                                 mod+"model_"+many2onemodel
                                                                 ,group_id_id,1,0,0,0)                          
                                    res.append(elem) 
                                    reg.append(many2onemodel)
        if len(res):
            csvmanag = csv_output(dirext+'/ir.model.access.csv' if dirext else 'ir.model.access.csv')
            fieldnames = "id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink"
            data = csvmanag.input(res,fieldnames)
            return data
        return []
    
    def registerfilexmlsecurity(self, cr, module, dirext,objgroupsec,uid):
              
        xmlfile = xml_output(dirext+'/'+module.name+'_security.xml')
        xmlfile.startXml()             
        #defino el atributo 
        xmlfile.defaultStart("openerp",{})
        attr = {'noupdate':"0"}
        xmlfile.defaultStart("data",attr)
        #defino el grupo y sus atributos
        attrsg = {'id':"group_"+module.name,'model':"res.groups"}            
        xmlfile.defaultStart("record",attrsg,1)
                           
        attrsg = {'name':"name"}            
        xmlfile.defaultStart("field",attrsg,2,objgroupsec.name)
        xmlfile.defaultEnd("field") 
        
        menudata_obj_search = self.pool.get('ir.model.data')
        
        #print "cantidad"
        #print len(objgroupsec.groups_inherits)
        if len(objgroupsec.groups_inherits):
            #  <field name="implied_ids" eval="[(4, ref('group_pos_user')), (4, ref('stock.group_stock_user'))]"/>
            cadimplied = ''
            i = 0    
            for objgroupimplied in objgroupsec.groups_inherits:   
                                    
                groupiddata = menudata_obj_search.search(cr, 1, [('res_id','=',objgroupimplied.id),('model','=','res.groups')])#('name','like','group_%'),                                                                                    
                groupdata = menudata_obj_search.read(cr, 1, groupiddata)     
                print "cantidad "+str(len(groupdata))                
                if len(groupdata):
                    
                    if i < len(objgroupsec.groups_inherits)-1: cadimplied += "(4,ref('"+groupdata[0]['module']+"."+groupdata[0]['name']+"'))"+','
                    else : cadimplied += "(4,ref('"+groupdata[0]['module']+"."+groupdata[0]['name']+"'))"
                    i +=1
                
                
                
            attrsg = {'name':"implied_ids",'eval':"["+cadimplied+"]"}    
            xmlfile.defaultStart("field",attrsg,2,'',True)                
                    
                    
        #termino tag de definicion de grupo
        xmlfile.defaultEnd("record",1)                                        
        if len(objgroupsec.menus_ids):
                                    
            menu_obj_search = self.pool.get('ir.ui.menu')
            
            for objmenu in objgroupsec.menus_ids:                                
                #print objmenu.name
                
                menuiddata = menudata_obj_search.search(cr, 1, [('res_id','=',objmenu.id),('model','=','ir.ui.menu')])#,('name','like','menu_%')
                #print "menu "
                #print objmenu.id                                     
                if len(menuiddata):           
                    menudata = menudata_obj_search.read(cr, 1, menuiddata)
                    #print "cantidad"
                    #print len(menudata)
                    #for md in menudata:
                    #    print md   
                    #xmlfile.addComment("Menu Name: "+objmenu.name+" ID:"+str(objmenu.id))
                    
                    if len(menudata):
                        
                        attrsm = {'id':str(menudata[0]['module'])+'.'+str(menudata[0]['name']),'model':"ir.ui.menu"}
                        
                        xmlfile.defaultStart("record",attrsm,1)
                        attrsg = {'eval':"[(4, ref('"+"group_"+module.name+"'))]",'name':"groups_id"}            
                        xmlfile.defaultStart("field",attrsg,2,'',True)               
                        xmlfile.defaultEnd("record",1)
                    
                
            xmlfile.defaultEnd("data")
            xmlfile.defaultEnd("openerp")
            xmlfile.endPage()
                                
        return True
        
        
        
        
    def generatenewgroup(self, cr, uid, ids, context):
        #todo aqui hay que copiarlo al modulo
        #o sea al security del modulo 
            
        #busco el modulo que fue seleccionado
        module_obj_search = self.pool.get('ir.module.module')
        objlist = self.browse(cr, uid, ids, context) 
        obj = objlist[0]
        #busco el elemento module en la bd
        module = module_obj_search.browse(cr, uid, obj.module_id.id, context)
        
            
        #obtengo el config con las variables globales del openerp    
        config = openerp.tools.config        
        
        for addons_dir in config['addons_path'].split(','):
            directorylist = os.listdir(addons_dir)
            for dir in directorylist:       
                dir_ext = addons_dir+"/"+dir         
                if os.path.isfile(dir_ext+"/__openerp__.py"):
                    modname = module.name
                    #info = modulemanager.load_information_from_description_file(dir_ext)
                    #print str(dir)+"<----->"+str(module.name)
                    if str(dir)==str(modname):                        
                        #print "si encontrado "+modname                        
                        #verfico la existencia del directorio security                        
                        if "security" not in os.listdir(dir_ext):
                            #creo el directorio si no existe
                            os.makedirs(dir_ext+"/security")
                            #modifico el fichero __openerp__
                            self.modifyfileopenperp(dir_ext,module.name+'_security.xml')
                        else:
                            #elimino los ficheros y la carpeta para crearla nuevamente
                            os.remove(dir_ext+"/security/"+module.name+'_security.xml')
                            os.remove(dir_ext+"/security/"+'ir.model.access.csv')                                                                                                           
                        #invoco a los modelos para crear las reglas de acceso a ellos
                        #en el fichero csv
                        self.registerfilecsvsecurity(cr,module,dir_ext+"/security",obj.name,uid)                        
                        #en el xml
                        self.registerfilexmlsecurity(cr,module,dir_ext+"/security",obj,uid)                        
                        break
                        
        return self.write(cr, uid, ids, {'data':'', 
                                        'filename':'',
                                        'group_id':False,
                                        'name':'',
                                        'type':False,
                                        'groups_inherits':
                                                [(6,0,[])],                                         
                                         'menus_ids':
                                                [(6,0,[])],
                                         'state':'choose'}, 
                                        context=context)                                               
        #self.write(cr, uid, ids, {'name':'','type':'', 'group_id':''}, context=context)
        #return                       
        
        
    def genfromexitsgroups(self, cr, uid, ids, context):
        
        def check__inherits(modelname):
            model_obj = self.pool.get(modelname)
               
            _inheritc = getattr(model_obj, '_inherit',None)
            _inheritsc = getattr(model_obj, '_inherits',None)
            if _inheritc :#or len(_inheritsc)>0                                 
                return False
                        
            return True                        
                
                
        groups_obj_create = self.pool.get('res.groups')
        
        #salvo el objeto grupo nuevo para hacer el cambio efectivo
        objlist = self.browse(cr, uid, ids, context)        
        #busco el elemento en la bd
        #groups_obj_search = groups_obj_create.search(cr, 1, [('name','=',objlist[0].name)])
        #verifico si existe ya uno con ese nombre   
                    
        #si el tipo que se selecciono es para el registro de los permisos
        #en la base de datos
        #entonces registro el grupo de usuario
        
        obj = objlist[0]
        #busco el modulo que fue seleccionado
        module_obj_search = self.pool.get('ir.module.module')                    
        #busco el elemento module en la bd
        module = module_obj_search.browse(cr, uid, obj.module_id.id, context)
        #invoco a los modelos para crear las reglas de acceso a ellos
        #en el fichero csv        
                                       
        modeldata_obj_search = self.pool.get('ir.model.data')
        groupiddata =  modeldata_obj_search.search(cr, 1, [('res_id','=',obj.group_id.id),('model','=','res.groups')])
        groupdata = modeldata_obj_search.read(cr, 1, groupiddata)
           
        if obj.type.id == 1:
           
           
           #print groupdata[0]['name']                                                
           data = self.registerfilecsvsecurity(cr,module,'',groupdata[0]['module']+'.'+groupdata[0]['name'],uid,True)
           if len(data):
               out=base64.encodestring(data)
               return self.write(cr, uid, ids, {'state':'get', 
               'data':out, 
               'filename':'irmodelacc.csv',
               'group_id':False,
               'name':'',
               'type':False,
               'groups_inherits':
                       [(6,0,[])],                
                'menus_ids':
                       [(6,0,[])]}, 
               context)
        else:
            
            groups_obj = self.pool.get('res.groups') 
            group = groups_obj.browse(cr, uid, obj.group_id.id, context)            
            #objeto ir model access para registrar los accesos
            ir_model_access_obj = self.pool.get('ir.model.access') 
            ir_model_obj = self.pool.get('ir.model')
                                                                   
            res= self.getmodelforsecurity(cr,module,'',groupdata[0]['module']+'.'+groupdata[0]['name'],uid,True)
            
            for model_acc in res:                          
                    
               #if check__inherits(model_acc['name']):   
               print  "->>>"+model_acc['name']     
               modelsearch = ir_model_obj.search(cr, 1, [('model','=',model_acc['name'])])
               print str(modelsearch)      
                                                             
               if len(modelsearch):               
                   vals = {'model_id':modelsearch[0],
                       'perm_read':model_acc['perm_read'],
                       'name':model_acc['module']+'.'+model_acc['name'],
                       'perm_unlink':model_acc['perm_unlink'],
                       'perm_write':model_acc['perm_write'],
                       'perm_create':model_acc['perm_create'],
                       'group_id':obj.group_id.id,}
                   #print str(vals)                                
                   ir_model_access_obj.create(cr,1,vals,context)
                        
            return self.write(cr, uid, ids, {'state':'choose', 
                                               'data':'', 
                                               'filename':'irmodelacc.csv',
                                               'group_id':False,
                                               'name':'',
                                               'type':False,
                                               'groups_inherits':
                                                       [(6,0,[])],
                                                'module_id':obj.module_id.id,
                                                'menus_ids':
                                                       [(6,0,[])]}, 
                                               context=context)                                                                                                                                                                                                                                                                    
                                                                
    def generategroupexits(self, cr, uid, ids, context):

        def check__inherits(modelname):
            model_obj = self.pool.get(modelname)
            _inheritc = getattr(model_obj, '_inherit', None)
            _inheritsc = getattr(model_obj, '_inherits', None)
            if _inheritc or len(_inheritsc) > 0:
                return False
            return True

        groups_obj_create = self.pool.get('res.groups')
        #salvo el objeto grupo nuevo para hacer el cambio efectivo
        objlist = self.browse(cr, uid, ids, context)
        #busco el elemento en la bd
        groups_obj_search = groups_obj_create.search(cr, 1,
                                            [('name', '=', objlist[0].name)])
        #verifico si existe ya uno con ese nombre
        if not len(groups_obj_search):
            #si el tipo que se selecciono es para el registro de los permisos
            #en la base de datos
            #registro el grupo de usuario
            if objlist[0].type.id == 2:
                groups_obj_create.create(cr, 1, {'name': objlist[0].name})
                cr.commit()
                groups_obj_create = groups_obj_create.search(cr, 1,
                                            [('name', '=', objlist[0].name)])
            #arreglo para guardar los registros para el csv
            valarray = []
            for obj in self.browse(cr, uid, ids, context):
                #objeto group
                groups_obj = self.pool.get('res.groups')
                group = groups_obj.browse(cr, uid, obj.group_id.id, context)
                #objeto ir model access para registrar los accesos
                ir_model_access_obj = self.pool.get('ir.model.access')
                if group.model_access:
                    for model_acc in group.model_access:
                        if check__inherits(model_acc.model_id.model):
                           if objlist[0].type.id == 2:
                               vals = {
                                    'model_id': model_acc.model_id.id,
                                    'perm_read': model_acc.perm_read,
                                    'name': "access_" + model_acc.model_id.model.replace('.', '_'),
                                    'perm_unlink': model_acc.perm_unlink,
                                    'perm_write': model_acc.perm_write,
                                    'perm_create': model_acc.perm_create,
                                    'group_id': groups_obj_create[0],}
                               ir_model_access_obj.create(cr,1,vals,context)
                           else:
                               perm_read = 0
                               perm_write = 0
                               perm_create = 0
                               perm_unlink = 0
                               #permisos del modelo 
                               if model_acc.perm_read:
                                   perm_read = 1
                               if model_acc.perm_create :
                                   perm_create = 1
                               if model_acc.perm_write:
                                   perm_write = 1
                               if model_acc.perm_unlink:
                                   perm_unlink = 1
                               namegroup = objlist[0].name
                               idval = "access_"+namegroup+"_"+model_acc.model_id.model.replace('.', '_')
                               nameval = "module_"+namegroup+"_"+model_acc.model_id.model.replace('.', '_')                                      
                               model_id_id = "model_"+model_acc.model_id.model.replace('.', '_')
                               group_id_id = "group_"+namegroup
                               
                               elem = idval + ','
                               elem += str(nameval) + ','
                               elem += str(model_id_id) + ','
                               elem += group_id_id + ','
                               elem += str(perm_read) + ','
                               elem += str(perm_write) + ','
                               elem += str(perm_create) + ','
                               elem += str(perm_unlink)
                               valarray.append(elem)
                    if len(valarray):           
                       csvmanag = csv_output('ir.model.access.csv')
                       fieldnames = "id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink"
                       data = csvmanag.input(valarray,fieldnames)
                       
                       if len(data):
                           out=base64.encodestring(data)
                           return self.write(cr, uid, ids, {'state':'get', 
                                                            'data':out, 
                                                            'filename':
                                                                'test.csv',
                                                            'group_id':False,
                                                            'name':'',
                                                            'type':False,
                                                            'groups_inherits':
                                                                    [(6,0,[])],                                                             
                                                             'menus_ids':
                                                                    [(6,0,[])]}, 
                                                            context=context)
                           #return {'value':{'group_id':False}}                                
        return self.write(cr, uid, ids, {'state':'choose', 
                                                            'data':'', 
                                                            'filename':'',
                                                            'group_id':False,
                                                            'name':'',
                                                            'type':False,
                                                            'groups_inherits':
                                                                    [(6,0,[])],                                                             
                                                             'menus_ids':
                                                                    [(6,0,[])],}, 
                                                            context=context)
        
df_security_group()


class csv_output(object):

    def __init__(self, filename, *args, **argv):
        self.fp = file(filename, 'wb+')
        return

    def input(self, rows, fieldnames):
        self.fp.write(fieldnames + "\r\n")
        for r in rows:
            self.fp.write(r + "\r\n")
        self.fp.seek(0)
        data = self.fp.read()
        self.fp.close()
        return data


class xml_output(object):

    def __init__(self, filename):
        self.out = file(filename, 'wb+')
        self.passthrough = True
        self.pila = []
        return

    def defaultStart(self, name, attrs, tabcant=0, content='', simple=False):
        if self.passthrough:
            self.out.write(self.genTab(tabcant) + '<' + name)
            self.pila.append({'name': name,
                              'tabcant': tabcant,
                              'simple': simple})
            for key, val in attrs.items():
                self.out.write(' %s="%s"' % (key, val))
            if not content:
                endline = '\r\n'
            else:
                endline = ''
            if not simple:
                self.out.write('>' + endline)
            else:
                self.out.write('/>' + endline)
            if content:
                self.defaultContent(content)

    def genTab(self, tabcant):
        i = 1
        cadtab = ''
        while i <= tabcant:
            cadtab += '\t'
            i += 1
        return cadtab

    def defaultContent(self, content):
        self.out.write(content)

    def defaultEnd(self, name, tabcant=0, simple=False):
        if self.passthrough:
            self.out.write(self.genTab(tabcant) + '</%s>' % name)
            self.out.write('\r\n')

    def startXml(self):
        self.writeHeader()
        self.passthrough = True

    def addComment(self, comment):
        self.out.write("<!-- " + comment + " -->" + '\r\n')

    def endPage(self):
        self.passthrough = False
        self.out.close()

    def writeHeader(self):
        self.out.write('<?xml version="1.0" encoding="utf-8"?>' + "\r\n")
