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
from openerp import addons
from osv import fields, osv
import pygraphviz as pgv
from pygraphviz import *
from tools.translate import _
import pydot
import inspect


class df_design(osv.osv_memory):
    """df_design Model
    Generates different artifacts that help to understand a module.
    """
    _name = 'df.design'
    _columns = {
        'module_id':
            fields.many2one('ir.module.module', 'Module'),
        'artifact':
            fields.selection([
                (1, 'Dependencies graph'),
                (2, 'Uses graph'),
                (3, 'Class diagram')],
                'Artifact'),
        'format':
            fields.selection([
                ('svg', 'SVG'),
                ('jpg', 'JPG'),
                ('png', 'PNG')],
                'Format'),
        'columns': fields.boolean('Columns'),
        'attributes': fields.boolean('Attributes'),
        'methods': fields.boolean('Methods'),
        'image':
            fields.binary('Image', filters='*.png,*.svg,*.jpg', readonly=True)
    }
    _defaults = {
        'artifact': 3,
        'format': 'png',
        'columns': True,
        'attributes': True,
        'methods': True
    }

    def generate(self, cr, uid, ids, context):
        """Generates the artifact solicited by the user"""
        for obj in self.browse(cr, uid, ids, context):
            if obj.artifact == 1:
                uri = self.generate_dependencies_graph(cr, uid, obj, context)
            elif obj.artifact == 2:
                uri = self.generate_uses_graph(cr, uid, obj, context)
            else:
                try:
                    addon = getattr(addons, obj.module_id.name)
                    uri = self.generate_class_diagram(cr, uid, obj,
                                                                addon, context)
                except AttributeError:
                    addon = __import__(obj.module_id.name)
                    uri = self.generate_class_diagram(cr, uid, obj,
                                                                addon, context)
                    del addon
            self.write(cr, uid, obj.id, {'image': open(uri, 'rb').
                                     read().encode('base64')}, context)
        return True

    def generate_dependencies_graph(self, cr, uid, obj, context):
        """Generates a graph with all the dependencies of a module"""
        graph = pgv.AGraph(strict=False, directed=True)
        graph = self.update_dependencies_graph(cr, uid, graph,
                                                obj.module_id.id, context)
        graph.layout(prog='dot')
        uri = str(inspect.getabsfile(self.__class__))\
                .replace('df_design.py', 'tmp/' + obj.module_id.name +
                                            '_dependencies.' + obj.format)
        try:
            graph.draw(uri)
        except:
            raise osv.except_osv(_('Message: '),
                              _('The URI is not correct.'))
        return uri

    def update_dependencies_graph(self, cr, uid, graph, mod_id, context):
        """Recursively draw a graph of a module's dependencies"""
        module_obj = self.pool.get('ir.module.module')
        module = module_obj.browse(cr, uid, mod_id, context)
        if module.dependencies_id:
            deps = [d.name for d in module.dependencies_id]
            graph.add_node(module.name)
            for d in deps:
                graph.add_node(d)
                ids = module_obj.search(cr, uid, [('name', '=', d)])
                if ids:
                    graph = self.update_dependencies_graph(cr, uid, graph,
                                                              ids[0], context)
                if not graph.has_edge(module.name, d):
                    graph.add_edge(module.name, d)
        return graph

    def generate_uses_graph(self, cr, uid, obj, context):
        """Generates a graph with all the modules that depends of a module"""
        graph = pgv.AGraph(strict=False, directed=True)
        graph = self.update_uses_graph(cr, uid, graph,
                                          obj.module_id.id, context)
        graph.layout(prog='dot')
        uri = str(inspect.getabsfile(self.__class__))\
                    .replace('df_design.py', 'tmp/' + obj.module_id.name +
                                            '_uses.' + obj.format)
        try:
            graph.draw(uri)
        except:
            raise osv.except_osv(_('Message: '),
                              _('The URI is not correct.'))
        return uri

    def update_uses_graph(self, cr, uid, graph, mod_id, context):
        """Recursively draw a graph with the modules that depend of a module"""
        dependency_obj = self.pool.get('ir.module.module.dependency')
        module_obj = self.pool.get('ir.module.module')
        module = module_obj.browse(cr, uid, mod_id, context)
        uses_ids = dependency_obj.search(cr, uid, [('name', '=', module.name)])
        if len(uses_ids):
            uses = dependency_obj.browse(cr, uid, uses_ids, context)
            mods = [u.module_id for u in uses]
            graph.add_node(module.name)
            for mod in mods:
                graph.add_node(mod.name)
                graph = self\
                    .update_uses_graph(cr, uid, graph, mod.id, context)
                if not graph.has_edge(mod.name, module.name):
                    graph.add_edge(mod.name, module.name)
        return graph

    def generate_class_diagram(self, cr, uid, obj, addon, context):
        """Generates a class diagram of a module's classes and its relations"""
        classes = []
        self.get_inner_classes(addon, classes)
        data = self.process_class_list(classes, obj)
        graph = self.draw_class_diagram(data)
        uri = str(inspect.getabsfile(self.__class__))\
                    .replace('df_design.py', 'tmp/' + obj.module_id.name +
                                            '_class_diagram.' + obj.format)
        try:
            if obj.format == 'png':
                graph.write_png(uri)
            elif obj.format == 'jpg':
                graph.write_jpg(uri)
            elif obj.format == 'svg':
                graph.write_svg(uri)
        except:
            raise osv.except_osv(_('Message: '),
                              _('The URI is not correct.'))
        return uri

    def get_inner_classes(self, module, classes):
        """Returns the information of all classes defined in the
        given module"""
        module_dict = module.__dict__
        mdict = {attr: module_dict[attr] for attr in module_dict
                                            if not attr.startswith('__')}
        for item in mdict.itervalues():
            if inspect.ismodule(item):
                if self.is_file_module(item):
                    classes.extend(self.inspect_file(item))
                elif module.__name__ in item.__name__:
                    self.get_inner_classes(item, classes)
        return classes

    def inspect_file(self, mfile):
        """Returns the information of all classes defined in the given file"""
        classes = []
        file_dict = mfile.__dict__
        mdict = {attr: file_dict[attr] for attr in file_dict
                                        if not attr.startswith('__')}
        for item in mdict.itervalues():
            if inspect.isclass(item) and self.is_inner_class(item, mfile):
                classes.append(self.inspect_class(item))

        return classes

    def inspect_class(self, mclass):
        """Returns the information of the given class"""
        class_info = {
#             'class_name': mclass.__name__,
             'name': mclass._name if hasattr(mclass, '_name') else '',
             'entity': True if hasattr(mclass, '__mro__')
                            and osv.osv in mclass.__mro__ else False,
#             'module':mclass._module if hasattr(mclass, '_module' ) else None,
             'parent': mclass._inherit if hasattr(mclass, '_inherit') else '',
             'inherits': mclass._inherits.keys()
                            if hasattr(mclass, '_inherits') else [],
             'py_inherits': [p.__name__ for p in mclass.__mro__
                            if not p.__name__ in [mclass.__name__,
                                                  'Model', 'BaseModel',
                                                  'TransientModel', 'object']
                            ],
             'attributes': self.gather_attributes_info(mclass),
             'fields': self.gather_columns_info(mclass),
             'methods': self.gather_methods_info(mclass)
            }
        if not class_info.get('name', False):
            class_info['name'] = class_info.get('parent', False)
        if not class_info.get('name', False):
            class_info['name'] = mclass.__name__
        if class_info.get('parent', False):
            class_info['inherits'].extend([class_info['parent']])
        return class_info

    def gather_attributes_info(self, mclass):
        """Returns the information of all attributes defined in the
        given class"""
        attributes = []
        class_dict = mclass.__dict__
        mdict = {attr: class_dict[attr] for attr in class_dict
                if not attr.startswith('__')
                and not attr in
                ['_columns',
                 '_defaults',
                 '_inherit',
                 '_inherits',
                 '_module',
                 '_description',
                 '_name',
                 '_original_module',
                 '_sql_constraints',
                 '_constraints']}
        for key in mdict:
            if not inspect.ismethod(getattr(mclass, key)):
                attributes.append(key)
        return attributes

    def gather_columns_info(self, mclass):
        """Returns the information of all columns defined in the given class"""
        fields = []
        if hasattr(mclass, '_columns'):
            columns = getattr(mclass, '_columns')
            defaults = getattr(mclass, '_defaults', [])
            for key in columns:
                field = {
                         'field_name': key,
                         'field_type': columns[key].__class__.__name__
                         }
                if key in defaults:
                    field['default_value'] = defaults[key]\
                                    if not inspect.isfunction(defaults[key])\
                                    else defaults[key].__name__
                    field['default_value'] = str(field['default_value'])\
                                                        .replace('<', '')
                    field['default_value'] = str(field['default_value'])\
                                                        .replace('>', '')
                    field['default_value'] = str(field['default_value'])\
                                                .replace('unbound method', '')
                if field['field_type'] in\
                            ['one2one', 'many2one', 'one2many', 'many2many']:
                    field['reference_class'] = columns[key]._obj
                if field['field_type'] == 'many2many':
                    field['reference_table'] = columns[key]._rel
                fields.append(field)
        return fields

    def gather_methods_info(self, mclass):
        """Returns the information of all methods defined in the given class"""
        methods = []
        class_dict = mclass.__dict__
        mdict = {attr: class_dict[attr] for attr in class_dict
                                        if not attr.startswith('__')}
        for key in mdict:
            if inspect.ismethod(getattr(mclass, key)):
                methods.append(key)
        return methods

    def is_file_module(self, module):
        """Determine if the given module is a file or a package"""
        if hasattr(module, '__file__'):
            file_name = getattr(module, '__file__')
            if not '__init__' in file_name:
                return True
        return False

    def is_inner_class(self, mclass, mfile):
        """Determine if the given class is defined in the given file"""
        class_dict = mclass.__dict__
        if class_dict.get('__module__', False) == getattr(mfile, '__name__'):
            return True
        return False

    def process_class_list(self, classes, obj):
        """Prepare the information needed to draw a complete class diagram"""
        class_list = {}
        for mclass in classes:
            if class_list.get(mclass['name'], False):
                class_list[mclass['name']]['attributes']\
                                                .extend(mclass['attributes'])
                class_list[mclass['name']]['fields'].extend(mclass['fields'])
                class_list[mclass['name']]['methods'].extend(mclass['methods'])
            else:
                class_list[mclass['name']] = mclass
        total_info = {
                      'class_list': class_list
                      }
        total_info['links'] = {}
        for mclass in classes:
            for mfield in mclass['fields']:
                if mfield['field_type'] in\
                                        ['one2one', 'many2one', 'many2many']:
                    if class_list.get(mfield['reference_class'], False):
                        reverse = 'no'
                        relacion = mclass['name'] + '<' + mfield['field_type']\
                                            + '>' + mfield['reference_class']
                        if mfield['field_type'] == 'many2many':
                            reverse = mfield['reference_table']
                            relacion = mfield['reference_table']
                        if not total_info['links'].get(reverse, False):
                            total_info['links'][relacion] = {
                                 'src_class': mclass['name'],
                                 'src_field': mfield['field_name'],
                                 'src_type': mfield['field_type'],
                                 'dest_class': mfield['reference_class']
                                 }
                    else:
                        mfield['external_reference'] = True
        for mclass in classes:
            if not obj.columns:
                mclass['fields'] = []
            if not obj.attributes:
                mclass['attributes'] = []
            if not obj.methods:
                mclass['methods'] = []
        return total_info

    def draw_class_diagram(self, total_info):
        """Returns a graph with all classes and its relations"""
        graph = pydot.Dot(graph_type='digraph')
        graph.set_ratio('compress')
        for mclass in total_info['class_list'].values():
            separator = self.draw_separator()
            header = self.draw_header(mclass)
            fields = ''.join([self.draw_field(k) for k in mclass['fields']])
            attributes = ''.join([self.draw_attribute(k)
                                  for k in mclass['attributes']])
            methods = ''.join([self.draw_method(k)
                                for k in mclass['methods']])
            if fields and (attributes or methods):
                fields += separator
            if attributes and methods:
                attributes += separator
            tail = self.draw_tail()
            label = header + fields + attributes + methods + tail
            node = pydot.Node(mclass['name'], label=label)
            node.set_shape('none')
            graph.add_node(node)
        for mclass in total_info['class_list'].values():
            for parent in mclass['inherits']:
                if mclass['name'] != parent and\
                            total_info['class_list'].get(parent, False):
                    edge = self.draw_inherit(mclass['name'], parent)
                    graph.add_edge(edge)
            for parent in mclass['py_inherits']:
                if total_info['class_list'].get(parent, False):
                    edge = self.draw_inherit(mclass['name'], parent, True)
                    graph.add_edge(edge)
        for link in total_info['links'].values():
            edge = self.draw_edge(link)
            graph.add_edge(edge)
        graph.set_fontsize('8.0')
        return graph

    def draw_inherit(self, src_class, dest_class, py_inherit=False):
        """Returns an edge representing a class inheritance between
        src_class(child) and dest_class(parent). If the py_inherit parameter
        is specified True means that is a python inheritance, otherwise is
        taken as a OpenErp inheritance"""
        edge = pydot.Edge(src_class, dest_class)
        if py_inherit:
            edge.set_color('red')
        return edge

    def draw_edge(self, link):
        """Returns an edge representing a database relation
        between tow classes"""
        edge = pydot.Edge(link['src_class'], link['dest_class'])
        edge.set_arrowsize('0')
        if link['src_type'] == 'many2many':
            edge.set_headlabel(' * ')
            edge.set_taillabel(' * ')
        elif link['src_type'] == 'one2many':
            edge.set_headlabel(' * ')
            edge.set_taillabel(' 1 ')
        elif link['src_type'] == 'many2one':
            edge.set_headlabel(' 1 ')
            edge.set_taillabel(' * ')
        elif link['src_type'] == 'one2one':
            edge.set_headlabel(' 1 ')
            edge.set_taillabel(' 1 ')
        return edge

    def draw_header(self, class_info):
        """Returns the html elements needed to begin a node"""
        color = 'blue' if class_info.get('entity', False) else 'olivedrab4'
        name = class_info.get('name', False)
        parent = ','.join(class_info.get('inherits', ''))
        if parent:
            parent = "(" + parent + ")"
        header = """<
        <TABLE BGCOLOR="palegoldenrod" BORDER="1" CELLBORDER="0"
        ><TR>
                <TD COLSPAN="3" ALIGN="CENTER" BGCOLOR="%s" BORDER="1">
                <FONT FACE="Helvetica Bold" COLOR="white">%s %s</FONT>
                </TD>
            </TR>
        """ % (color, name, parent)
        return header

    def draw_attribute(self, attribute_name):
        """Returns the html elements needed to draw a class attribute"""
        attribute = """
            <TR><TD COLSPAN="3" CELLPADDING="4" ALIGN="LEFT" BORDER="0"
            ><FONT FACE="Helvetica Bold">%s</FONT
            ></TD>
           </TR>
        """ % attribute_name
        return attribute

    def draw_method(self, method_name):
        """Returns the html elements needed to draw a class method"""
        method = """
            <TR><TD COLSPAN="3" CELLPADDING="4" ALIGN="LEFT" BORDER="0"
            ><FONT FACE="Helvetica Bold">%s</FONT
            ></TD>
           </TR>
        """ % method_name
        return method

    def draw_field(self, field_info):
        """Returns the html elements needed to draw a database field"""
        name = field_info.get('field_name', ' ')
        ftype = field_info.get('field_type', ' ')
        color = 'red' if field_info.get('external_reference', False)\
                    else 'black'
        reference = ' ' + field_info.get('reference_class', ' ')
        field = """
            <TR><TD ALIGN="LEFT" BORDER="0"
            ><FONT FACE="Helvetica Bold" >%s</FONT
            ></TD>
            <TD ALIGN="LEFT"
            ><FONT FACE="Helvetica Bold" >%s</FONT
            ></TD>
            <TD ALIGN="RIGHT"
            ><FONT FACE="Helvetica Bold"  COLOR="%s">%s</FONT
            ></TD></TR>
        """ % (name, ftype, color, reference)
        return field

    def draw_tail(self):
        """Returns the html elements needed to end a node"""
        tail = """
        </TABLE>
        >"""
        return tail

    def draw_separator(self):
        """Returns the html elements needed to draw a separator"""
        separator = """
            <TR><TD COLSPAN="3"
            >_________________________________</TD>
           </TR>
        """
        return separator

df_design()
