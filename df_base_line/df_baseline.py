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


class project_project(osv.osv):
    _name = "project.project"
    _inherit = "project.project"
    _description = "Neos project concept representations "
    _columns = {
        'baseline_id': fields.integer('Base line id'),
        'processarea_ids':
            fields.one2many('neos.proccessarea', 'project_id', 'Process area'),
    }
project_project()


class project_task(osv.osv):
    _name = "project.task"
    _inherit = "project.task"
    _description = "Inheritance from project task for add some new features"
    _columns = {
        'baseline_id': fields.integer('Base line id'),
        'iteration_id': fields.integer('Iteration id'),
        'detailine_id': fields.integer('Detail line id'),
        'last_day_used_hours': fields.integer('Last day used hours'),
    }
    # ** - Functions - **
    def _change_type(self, cr, uid, ids, next, *args):
        for task in self.browse(cr, uid, ids):
            if  task.project_id.type_ids:
                typeid = task.type_id.id
                types_seq={}
                for type in task.project_id.type_ids :
                    types_seq[type.id] = type.sequence
                if next:
                    types = sorted(types_seq.items(), lambda x, y: cmp(x[1], y[1]))
                else:
                    types = sorted(types_seq.items(), lambda x, y: cmp(y[1], x[1]))
                sorted_types = [x[0] for x in types]
                if not typeid:
                    self.write(cr, uid, task.id, {'type_id': sorted_types[0]})
                elif typeid and typeid in sorted_types and sorted_types.index(typeid) != len(sorted_types)-1:
                    index = sorted_types.index(typeid)
                    self.write(cr, uid, task.id, {'type_id': sorted_types[index+1]})
                    # ** - New things added - **
                    task_id = ids
                    taskworks_ids = self.pool.get('project.task.work').search(cr,uid,[('task_id','=',task_id)])
                    aux_tw_dict = {}
                    aux_tw_dict['state'] = 'done'
                    for i in range(len(taskworks_ids)):
                        tw_object = self.pool.get('project.task.work').browse(cr, uid, taskworks_ids[i], context=None)
                        stage_object = self.pool.get('project.task.type').browse(cr, uid, typeid, context=None)
                        aux_list = []
                        aux_list.append(taskworks_ids[i])
                        if tw_object.stage_id  ==   stage_object.stage_id:
                            #self.pool.get('project.task.work').write(cr, uid,[ids[0]],aux_dict)
                            self.pool.get('project.task.work').end_task_work(cr, uid,aux_list,context=None)
        return True
project_task()

class project_task_work(osv.osv):
    _name = "project.task.work"
    _inherit = "project.task.work"
    _description = "Inheritance from project task work for add some new features"
    _columns = {
        'baseline_id': fields.integer('Base line id'),
        'stage_id': fields.integer('Stage id'),
        'hours_to_spent': fields.float('Hour to spent'),
        'state': fields.selection([('open', 'In Progress'),('done', 'Done')], 'State', readonly=True, required=True,
                                  help='When the task is created the state is \'In Progress\'.\n state.\
                                  \n When the task is over, the state is set to \'Done\'.'),
    }
    _defaults = {
      'state': 'open',
    }
    
    def end_task_work(self, cr, uid, ids, context=None):
        tw_object = self.pool.get('project.task.work').browse(cr, uid, ids[0], context=None)
        aux_dict = {}
        aux_dict['state'] = 'done'
        aux_dict['hours'] = tw_object.hours_to_spent
        self.pool.get('project.task.work').write(cr, uid,[ids[0]],aux_dict)
        #From here i'm trying to get the progress of the task for evaluate if it is equal to 99.99% for 
        #change its state to 'done'
        parent_task_id = tw_object.task_id.id
        parent_task_object = self.pool.get('project.task').browse(cr, uid, parent_task_id, context=None)
        if parent_task_object.progress == 99.99:
            aux_task_dict = {}
            aux_task_dict['state'] = 'done'
            self.pool.get('project.task').write(cr, uid,parent_task_id,aux_task_dict)
        
        
project_task_work()

class project_task_type(osv.osv):
    _name = "project.task.type"
    _inherit = "project.task.type"
    _description = "Inheritance from project task type to add some new features"
    _columns = {
        'stage_id': fields.integer('Stage id'),
    }
project_task_type()

class neos_baseline(osv.osv):
    _name = "neos.baseline"
    _description = "Base line concept business"
    _columns = {
        'name':fields.char('Name', size=100, required=True),
        'code':fields.char('Code', size=50, required=True),
        'version':fields.char('Version', size=100, required=True),
        'description':fields.text('Description',help="Objective description of the Base line."),
        'iteration_ids': fields.one2many('neos.iteration', 'baseline_id', 'Base line'),
        'baseline_details_lines': fields.one2many('neos.baseline.details', 'baseline_id', 'Process'),
        'method_id': fields.many2one('neos.method', 'Method',required = True),
        'setup_id': fields.many2one('df.bl.workingdays', 'Set-up Working days',required = True),
        'task_ids': fields.related('method_id', 'tasks_ids', type='one2many', relation='neos.tasks'),
        'state': fields.selection([('draft', 'Draft'),('progress', 'Being planned')], 'State', readonly=True, required=True,
                                  help='When the task is created the state is \'Draft\'.\n state.\
                                  \n When the task is being planned, the state is set to \'Being planned\'.'),
        'date_start': fields.datetime('Starting Date',select=True),
        }
    _defaults = {
      'state': 'draft',
      
    }
    
#    def create(self, cr, uid, vals,context):
#        aux = vals['baseline_details_lines'][0]
#        listaux = aux[2]
neos_baseline()

class neos_baseline_details(osv.osv):
    _name = "neos.baseline.details"
    _description = "Neos base line details concept business"
    _columns = {
        'name': fields.char('Name', size=100, required=True),
        'code': fields.char('Code', size=50, required=True),
        'precedent': fields.selection([('0', 'After'),
                                       ('1', 'Parallel')],
                                      'Type of precedence', required=False, 
                                      help='Feature used to select the type of precedence'),
        'priority':
            fields.selection([('4', 'Very low'),('3', 'Low'),('2', 'Medium'),
                              ('1', 'Important'),
                              ('0', 'Very important')], 'Complexity', 
                              required=False),
        'description':
            fields.text('Description',
                        help="Description objective of the base line details."),
        'date_start':
            fields.datetime('Starting Date', select=True),
        'date_end':
            fields.datetime('Ending Date', select=True),
        'process_area_id':
            fields.many2one('neos.proccessarea', 'Process area'),
        'functional_group_id':
            fields.many2one('neos.functional.group', 'Functional grouping'),
        'functional_scenario_id':
            fields.many2one('neos.functional.scenario', 'Functional scenario'),
        'iteration_id':
            fields.many2one('neos.iteration', 'Iteration', required=False),
        'baseline_id':
            fields.many2one('neos.baseline', 'Base line'),
        'state': fields.selection([('draft', 'Draft'),('progress', 'Being planned')], 'State', readonly=True, required=True,
                                  help='When the task is created the state is \'Draft\'.\n state.\
                                  \n When the task is being planned, the state is set to \'Being planned\'.'),
        'last_sat_worked': fields.boolean('Last sat worked'),
        'after_with':
            fields.many2one('neos.baseline.details', 'To be preceded', required=False),
    }
    _defaults = {
        'priority': '2',
        'precedent':'0',
        'state': 'draft',
        'last_sat_worked':False
    }
neos_baseline_details()

class neos_method(osv.osv):
    _name = "neos.method"
    _description = "Methods to group tasks"
    _columns = {
        'name':fields.char('Name', size=100, required=True),
        'code':fields.char('Code', size=50, required=True),
        'description':fields.text('Description',help="Description objective of the base line details."),
        'tasks_ids':fields.one2many('neos.tasks','method_id','Tasks'),
    }
    _sql_constraints = [
        ('name_processarea_uniq', 'unique(name)', 'The name must be unique per base line!'),
        ('code_processarea_uniq', 'unique(code)', 'The code must be unique per base line!'),
    ]
neos_method()

class neos_tasks(osv.osv):
    _name = "neos.tasks"
    _description = "Function used to create tasks"
    _columns = {
        'name':fields.char('Name', size=100, required=True),
        'code':fields.char('Code', size=50, required=True),
        'complex_low':fields.float('Low', required=True),
        'complex_verylow':fields.float('Very low', required=True),
        'complex_medium':fields.float('Medium', required=True),
        'complex_important':fields.float('Important', required=True),
        'complex_veryimportant':fields.float('Very important', required=True),
        'description':fields.text('Description'),
        'method_id':fields.many2one('neos.method','Method'),
        'stage_id':fields.many2one('neos.stage','Stage'),
    }
neos_tasks()

class neos_stage(osv.osv):
    _name = 'neos.stage'
    _description = 'Function used to create the stages for the detail lines'
    _columns = {
        'name': fields.char('Stage Name', required=True, size=64,Translate=True),
        'description': fields.text('Description'),
        'sequence': fields.integer('Sequence'),
   }
neos_stage()

class neos_iteration(osv.osv):
    _name = 'neos.iteration'
    _description = 'Function used to manage the base line iterations'
    _columns = {
        'name': fields.char('Name', size=64, required=False, readonly=False),
        'code': fields.char('Code', size=64, required=False, readonly=False),
        'description':
            fields.text('Description'),
        'baseline_id':
            fields.many2one('neos.baseline', 'Baseline', required=False),
        'functional_scenaro_id':
            fields.many2one('neos.functional.scenario', 'Functional scenario',
                            required=False),
        'project_id':
            fields.many2one('project.project', 'Project', required=False),
        'baselinedetails_ids':
            fields.one2many('neos.baseline.details', 'iteration_id',
                            'Baseline detail lines', required=False),
        'state': fields.selection([('draft', 'Draft'),('progress', 'Being planned')], 'State', readonly=True, required=True,
                                  help='When the task is created the state is \'Draft\'.\n state.\
                                  \n When the task is being planned, the state is set to \'Being planned\'.'),
    }
    _defaults = {
      'state': 'draft',
    }
neos_iteration()

class df_working_days(osv.osv):
    _name = "df.bl.workingdays"
    _description = "This class is used to set up the working days per project"
    _columns = {
        'name':fields.char('Name', size=100, required=True),
        'code':fields.char('Code', size=50, required=True),
        'hours_per_normal_day': fields.integer('Normal day',help="In this field we must insert the number of working hours per day in a normal week."),
        'hours_per_wk_day': fields.integer('Saturdays working hours',help="In this field we must insert the number of working hours per Saturdays in a special week."),
        'normal_setup': fields.boolean('Normal Set-up', help="If we select the normal set-up the working days will be only between Monday and Friday."),
        'special_setup': fields.boolean('Special Set-up', help="If we select the special set-up the working days will be only between Monday and Saturday."),
        'nonconsecutive_saturdays': fields.boolean('Non-consecutive Saturdays', help="If we select the special set-up and Non-Consecutive Saturdays the working days will be all the Saturdays non-consecutive of the month."),
        'all_saturdays': fields.boolean('All Saturdays', help="If we select All Saturdays option of the special set-up, it means i will work all the Saturdays of the month."),
        'description':fields.text('Description',help="Objective description of the current working day set up."),
    }
    _defaults = {
      'normal_setup': 1,
    }
    # *- Validation constraints -*
    def _check_hours_per_normal_day(self, cr, uid, ids, context=None):
        obj_fsetup = self.browse(cr, uid, ids[0], context=context)
        if obj_fsetup.hours_per_normal_day > 24:
            return False
        return True
    
    def _check_hours_per_wk_day(self, cr, uid, ids, context=None):
        obj_fsetup = self.browse(cr, uid, ids[0], context=context)
        if obj_fsetup.hours_per_wk_day > 24:
            return False
        return True
    # *End*- Validation constraints -*
    
    _constraints = [
        (_check_hours_per_normal_day, _('Error! The amount of hours per day must be less than 24.'), ['hours_per_normal_day']),
        (_check_hours_per_wk_day, _('Error! The amount of hours per day must be less than 24.'), ['hours_per_wk_day'])
    ]
    # *- Functions -*
    def onchange_normal_setup(self, cr, uid, ids,normal_setup,special_setup):
        if normal_setup:
            return {'value': {'special_setup' : 0}}
        elif normal_setup == 0 and special_setup == 0:
            return {'value': {'special_setup' : 1,'normal_setup' : 0}}
        
    def onchange_special_setup(self, cr, uid, ids,special_setup,normal_setup):
        if special_setup: 
            return {'value': {'normal_setup' : 0,'nonconsecutive_saturdays':1}}
        elif normal_setup == 0 and special_setup == 0:
            return {'value': {'special_setup' : 0,'normal_setup' : 1}}
    
    def onchange_nonconsecutive_saturdays(self, cr, uid, ids,nonconsecutive_saturdays,all_saturdays):
        if nonconsecutive_saturdays:
            return {'value': {'all_saturdays' : 0}}
        elif nonconsecutive_saturdays == 0 and all_saturdays == 0:
            return {'value': {'nonconsecutive_saturdays' : 0,'all_saturdays' : 1}}
        
    def onchange_all_saturdays(self, cr, uid, ids,all_saturdays,nonconsecutive_saturdays):
        if all_saturdays: 
            return {'value': {'nonconsecutive_saturdays' : 0}}
        elif nonconsecutive_saturdays == 0 and all_saturdays == 0:
            return {'value': {'nonconsecutive_saturdays' : 1,'all_saturdays' : 0}}
    # *End*- Functions -*
df_working_days()

class df_holidays(osv.osv):
    _name = 'df.bl.holidays'
    _description = 'Class used to set up the holidays'
    _columns = {
        'name': 
            fields.char('Name', size=64, required=False, readonly=False),
        'date_start':
            fields.datetime('Starting Date', select=True),
        'date_end':
            fields.datetime('Ending Date', select=True),
        'description':
            fields.text('Description'),
    }
df_holidays()
