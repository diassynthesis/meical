# -*- coding: utf-8 -*-
from osv import osv, fields
from tools.translate import _
import time
import datetime
import calendar

class make_planing(osv.osv_memory):
    _name = 'neos.makeplaning'
    _description = 'Class used to make a planing'
    _columns = { 
                'baseline_id': fields.many2one('neos.baseline', 'Base line'),
                'functionalscenario_id': fields.many2one('neos.functional.scenario', 'Functional scenario'),
                'iteration_ids':fields.many2many('neos.iteration','aux_table','planiteration_id','iteration_id','Iterations'),
               }
    
    def stage_data(self, cr, uid, stage_id):
        obj_stage = self.pool.get('neos.stage').browse(cr, uid, stage_id, context=None)
        obj_project_task_type = self.pool.get('project.task.type') 
        task_type_dict = {}
        task_type_dict['name'] = obj_stage.name
        task_type_dict['stage_id'] = obj_stage.id
        task_type_dict['sequence'] = obj_stage.sequence
        task_type_dict['project_default'] = 1
        stage_id_verification = self.pool.get('project.task.type').search(cr,uid,[('stage_id','=',stage_id)])
        if stage_id_verification == []:
            stage_id = obj_project_task_type.create(cr, uid, task_type_dict)
            return stage_id
        else:
            stage_id = stage_id_verification[0]
            return stage_id
    
    def initial_planning(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        values={}
        #** -Getting all data from the wizard's context- **
        this_wizard = self.browse(cr, uid, ids, context=context)[0]  
        baseline_id = this_wizard.baseline_id.id
        baseline_name= this_wizard.baseline_id.name
        iteration_ids = this_wizard.iteration_ids
        values['baseline_id']= baseline_id
        values['name']= baseline_name
#        values['department_id']= 1 # It is only for trial, it will removed later
        #** -END-Getting all data from the wizard's context- **
        
        #** -Creating a project - **
        obj_project = self.pool.get('project.project')
        project_id = obj_project.create(cr,uid,values)
        #** -END-Creating a project - **
        
        # ** - Getting list of tasks by the selected method in the current base line- **
        current_baseline_obj = self.pool.get('neos.baseline').browse(cr, uid, baseline_id, context=None)
        method_id = current_baseline_obj.method_id.id
        method_task_ids = self.pool.get('neos.tasks').search(cr,uid,[('method_id','=',method_id)])
        method_tasks = self.pool.get('neos.tasks').browse(cr, uid, method_task_ids, context=None)
        
        # ** -Getting all the details lines data- **
        aux_iteration_ids = []
        for i in range(len(iteration_ids)):
            aux_iteration_ids.append(iteration_ids[i].id)
        var_detailines_ids = self.pool.get('neos.baseline.details').search(cr,uid,[('iteration_id','in',aux_iteration_ids)])
        var_detailines = self.pool.get('neos.baseline.details').browse(cr, uid, var_detailines_ids, context=None)
        # ** -END-Getting all the details lines data- **
        
        # ** -Function used to select which is the next detail line to planning- **
        while len(var_detailines) > 0:
            for i in range(len(var_detailines)):
                planned = self.pool.get('project.task').search(cr,uid,[('detailine_id','=',var_detailines[i].after_with.id)])
                if len(planned)>0 or not var_detailines[i].after_with:
                    self.make_planing(cr, uid, ids,var_detailines[i],method_tasks,baseline_id,var_detailines[i].id,project_id,aux_iteration_ids,var_detailines[i].after_with)
                    var_detailines.remove(var_detailines[i])
                    break
        # ** -END-Function used to select which is the next detail line to planning- **
        return  {'type': 'ir.actions.act_window_close'}
             
    def make_planing(self,cr, uid, ids,var_detailines,method_tasks,baseline_id,var_detailine_id,project_id,iteration_ids, after_with):
        task_dict = {}
        task_dict['name'] = var_detailines.name
        task_dict['baseline_id'] = baseline_id
        task_dict['iteration_id'] = var_detailines.iteration_id.id
        task_dict['detailine_id'] = var_detailines.id
        task_dict['project_id'] = project_id
        task_dict['state'] = 'open'
        aux_obj_project_task = self.pool.get('project.task').create(cr,uid,task_dict)
        
        aux_priority = var_detailines.priority
        aux_planned_hours = 0
        
        for j in range(len(method_tasks)):
            work_task_dict = {}
            obj_project_task_work = self.pool.get('project.task.work')
            work_task_dict['name'] = method_tasks[j].name
            work_task_dict['baseline_id'] = baseline_id
            work_task_dict['task_id'] = aux_obj_project_task
            work_task_dict['stage_id'] = method_tasks[j].stage_id.id 
            #Getting the stage id of the relation between task and stage, and later we will get the object from this id
            task_stage_id = method_tasks[j].stage_id.id 
            stage_id = self.stage_data(cr, uid, task_stage_id)
            if aux_priority == '4':
                aux_planned_hours += method_tasks[j].complex_verylow
                work_task_dict['hours_to_spent'] = method_tasks[j].complex_verylow 
            elif aux_priority == '3':
                aux_planned_hours += method_tasks[j].complex_low
                work_task_dict['hours_to_spent'] = method_tasks[j].complex_low
            elif aux_priority == '2':
                aux_planned_hours += method_tasks[j].complex_medium
                work_task_dict['hours_to_spent'] = method_tasks[j].complex_medium
            elif aux_priority == '1':
                aux_planned_hours += method_tasks[j].complex_important
                work_task_dict['hours_to_spent'] = method_tasks[j].complex_important
            elif aux_priority == '0':
                aux_planned_hours += method_tasks[j].complex_veryimportant
                work_task_dict['hours_to_spent'] = method_tasks[j].complex_veryimportant
                
            
            task_dict['planned_hours'] = aux_planned_hours
            task_dict['remaining_hours'] = aux_planned_hours 
            # Looking if the task have one stage id (type_id) already
            object_added_task = self.pool.get('project.task').browse(cr, uid, aux_obj_project_task, context=None)
            if object_added_task.type_id:
                self.pool.get('project.task').write(cr, uid, aux_obj_project_task, task_dict)
            else:
                task_dict['type_id'] = stage_id
                self.pool.get('project.task').write(cr, uid, aux_obj_project_task, task_dict)
                
            aux_work_task_id = obj_project_task_work.create(cr,uid,work_task_dict)
            
            self.pool.get('project.task.type').write(cr, uid, stage_id, {'project_ids': [(4, project_id)]})
        #* -CTF- Calling the function "get_deadline" to get the deadline of a Base line detail line -*
        current_baseline_obj = self.pool.get('neos.baseline').browse(cr, uid, baseline_id, context=None)
        current_setup_id = current_baseline_obj.setup_id.id
        dates_dict = self.get_deadline(cr, uid, ids, aux_planned_hours,current_setup_id,baseline_id,var_detailines.id,after_with)
        self.pool.get('project.task').write(cr, uid, aux_obj_project_task, dates_dict)
        cr.commit()
        #* -END -CTF-*
        # ** - Changing the state of the current baseline, iterations and detail baselines to "Being planned" - **
        aux_state2change_dict = {}
        aux_state2change_dict['state']='progress'
        self.pool.get('neos.baseline').write(cr, uid, baseline_id,aux_state2change_dict)
        self.pool.get('neos.iteration').write(cr, uid, iteration_ids,aux_state2change_dict)
        self.pool.get('neos.baseline.details').write(cr, uid, var_detailine_id,aux_state2change_dict)
    
    def get_deadline(self, cr, uid, ids,hours_per_dline,current_setup_id,current_baseline_id,current_detailine_id,after_with):
        current_setup_obj = self.pool.get('df.bl.workingdays').browse(cr, uid, current_setup_id, context=None)
        current_baseline_obj = self.pool.get('neos.baseline').browse(cr, uid, current_baseline_id, context=None)
        current_detailine_obj = self.pool.get('neos.baseline.details').browse(cr, uid, current_detailine_id, context=None)
        hours_to_spent = hours_per_dline
        starting_position = current_detailine_obj.precedent
        if current_setup_obj.special_setup and current_setup_obj.nonconsecutive_saturdays:
            dates_dict = self.get_dates_non_con_saturdays(cr, uid,hours_to_spent,starting_position,current_setup_obj,current_baseline_id,current_detailine_id,after_with)
            return dates_dict
        elif current_setup_obj.special_setup and current_setup_obj.all_saturdays:
            dates_dict = self.get_dates_all_saturdays(cr, uid,hours_to_spent,starting_position,current_setup_obj,current_baseline_id,current_detailine_id,after_with)
            return dates_dict
        elif current_setup_obj.normal_setup:
            dates_dict = self.get_dates_normal_setup(cr, uid,hours_to_spent,starting_position,current_setup_obj,current_baseline_id,current_detailine_id,after_with)
            return dates_dict
            
    def get_dates_normal_setup(self,cr, uid,hours_to_spent,starting_position,current_setup_obj,current_baseline_id,current_detailine_id,after_with):
        hours_used_lastday = 0
        dates_dict = {}
        date_start = 0
        date_end = 0
        precedent_in_task_id = []
        if after_with:
            precedent_in_task_id = self.pool.get('project.task').search(cr, uid, [('detailine_id','=',after_with.id)], context=None)
            precedent_data = self.pool.get('project.task').browse(cr, uid, precedent_in_task_id[0], context=None)
        if starting_position == '0':
            if len(precedent_in_task_id):
                date_start = datetime.datetime.strptime(precedent_data.date_end,'%Y-%m-%d %H:%M:%S')
                date_end = date_start
                if datetime.datetime.isoweekday(date_end) == 6:
                    date_end = date_end + datetime.timedelta(days=2)
                while hours_to_spent >= current_setup_obj.hours_per_normal_day:
                    if datetime.datetime.isoweekday(date_end) == 6:
                        date_end = date_end + datetime.timedelta(days=2)
                    else:
                        date_end = date_end + datetime.timedelta(days=1)
                        hours_to_spent -= current_setup_obj.hours_per_normal_day
                dates_dict['date_start'] = date_start
                dates_dict['date_end'] = date_end
                dates_dict['date_deadline'] = date_end
                dates_dict['last_day_used_hours'] = hours_to_spent
            else:
                date_start = datetime.datetime.strptime(self.pool.get('neos.baseline').browse(cr, uid, current_baseline_id, context=None).date_start,'%Y-%m-%d %H:%M:%S')
                date_end = date_start
                if hours_used_lastday < current_setup_obj.hours_per_normal_day:
                    aux = current_setup_obj.hours_per_normal_day - hours_used_lastday
                    hours_to_spent -= aux
                    date_end = date_end + datetime.timedelta(days=1)
                while hours_to_spent >= current_setup_obj.hours_per_normal_day:
                    if datetime.datetime.isoweekday(date_end) == 6:
                        date_end = date_end + datetime.timedelta(days=2)
                    elif datetime.datetime.isoweekday(date_end) == 7:
                        date_end = date_end + datetime.timedelta(days=1)
                    else:
                        date_end = date_end + datetime.timedelta(days=1)
                        hours_to_spent -= current_setup_obj.hours_per_normal_day
                dates_dict['date_start'] = date_start
                dates_dict['date_end'] = date_end
                dates_dict['date_deadline'] = date_end
                dates_dict['last_day_used_hours'] = hours_to_spent
        elif starting_position == '1':
            if len(precedent_in_task_id):
                date_start = datetime.datetime.strptime(precedent_data.date_start,'%Y-%m-%d %H:%M:%S')
                date_end = date_start
                if datetime.datetime.isoweekday(date_end) == 6:
                    date_end = date_end + datetime.timedelta(days=2)
                while hours_to_spent >= current_setup_obj.hours_per_normal_day:
                    if datetime.datetime.isoweekday(date_end) == 6:
                        date_end = date_end + datetime.timedelta(days=2)
                    else:
                        date_end = date_end + datetime.timedelta(days=1)
                        hours_to_spent -= current_setup_obj.hours_per_normal_day
                dates_dict['date_start'] = date_start
                dates_dict['date_end'] = date_end
                dates_dict['date_deadline'] = date_end
                dates_dict['last_day_used_hours'] = hours_to_spent
            else:
                date_start = datetime.datetime.strptime(self.pool.get('neos.baseline').browse(cr, uid, current_baseline_id, context=None).date_start,'%Y-%m-%d %H:%M:%S')
                date_end = date_start
                while hours_to_spent > current_setup_obj.hours_per_normal_day:
                    if datetime.datetime.isoweekday(date_end) == 6:
                        date_end = date_end + datetime.timedelta(days=2)
                    elif datetime.datetime.isoweekday(date_end) == 7:
                        date_end = date_end + datetime.timedelta(days=1)
                    else:
                        date_end = date_end + datetime.timedelta(days=1)
                        hours_to_spent -= current_setup_obj.hours_per_normal_day
                dates_dict['date_start'] = date_start
                dates_dict['date_end'] = date_end
                dates_dict['date_deadline'] = date_end
                dates_dict['last_day_used_hours'] = hours_to_spent
        return dates_dict
    
    def get_dates_all_saturdays(self,cr, uid,hours_to_spent,starting_position,current_setup_obj,current_baseline_id,current_detailine_id,after_with):
        #**- Declaring auxiliary variables -**
        hours_used_lastday = 0
        dates_dict = {}
        date_start = 0
        date_end = 0
        precedent_in_task_id = []
        #**-END- Declaring auxiliary variables -**
        if after_with:#I do this because this var may come with a null value  
            precedent_in_task_id = self.pool.get('project.task').search(cr, uid, [('detailine_id','=',after_with.id)], context=None)
            precedent_data = self.pool.get('project.task').browse(cr, uid, precedent_in_task_id[0], context=None)
        if starting_position == '0':#Validating after position
            if len(precedent_in_task_id):# Validating if the current detailine has a precedent
                date_start = datetime.datetime.strptime(precedent_data.date_end,'%Y-%m-%d %H:%M:%S')
                date_end = date_start
                if datetime.datetime.isoweekday(date_end) == 6:
                    date_end = date_end + datetime.timedelta(days=2)
                while hours_to_spent >= current_setup_obj.hours_per_normal_day:
                    if datetime.datetime.isoweekday(date_end) == 6:
                        date_end = date_end + datetime.timedelta(days=2)
                        hours_to_spent -= current_setup_obj.hours_per_wk_day
                    else:
                        date_end = date_end + datetime.timedelta(days=1)
                        hours_to_spent -= current_setup_obj.hours_per_normal_day
                # Repito esto nuevamente porque me quedo un tiempo en horas sobrante sin asignar
                if datetime.datetime.isoweekday(date_end) == 6 and hours_to_spent > current_setup_obj.hours_per_wk_day:
                    date_end = date_end + datetime.timedelta(days=2)
                    hours_to_spent -= current_setup_obj.hours_per_wk_day
                dates_dict['date_start'] = date_start
                dates_dict['date_end'] = date_end
                dates_dict['date_deadline'] = date_end
                dates_dict['last_day_used_hours'] = hours_to_spent
                # -End- Repito esto nuevamente porque me quedo un tiempo en horas sobrante sin asignar
            else:
                date_start = datetime.datetime.strptime(self.pool.get('neos.baseline').browse(cr, uid, current_baseline_id, context=None).date_start,'%Y-%m-%d %H:%M:%S')
                date_end = date_start
                dates_dict['date_start'] = date_start
                if datetime.datetime.isoweekday(date_end) == 6:
                    if hours_used_lastday < current_setup_obj.hours_per_wk_day:
                        aux = current_setup_obj.hours_per_wk_day - hours_used_lastday
                        hours_to_spent -= aux
                        date_end = date_end + datetime.timedelta(days=2)
                elif datetime.datetime.isoweekday(date_end) == 7:
                    date_end = date_end + datetime.timedelta(days=1)
                else:
                    if hours_used_lastday < current_setup_obj.hours_per_normal_day:
                        aux = current_setup_obj.hours_per_normal_day - hours_used_lastday
                        hours_to_spent -= aux
                        date_end = date_end + datetime.timedelta(days=1)
                while hours_to_spent >= current_setup_obj.hours_per_normal_day:
                    if datetime.datetime.isoweekday(date_end) == 6:
                        date_end = date_end + datetime.timedelta(days=2)
                        hours_to_spent -= current_setup_obj.hours_per_wk_day
                    elif datetime.datetime.isoweekday(date_end) == 7:
                        date_end = date_end + datetime.timedelta(days=1)
                    else:
                        date_end = date_end + datetime.timedelta(days=1)
                        hours_to_spent -= current_setup_obj.hours_per_normal_day
                # Repito esto nuevamente porque me puede quedar un tiempo en horas sobrante sin asignar
                if datetime.datetime.isoweekday(date_end) == 6 and hours_to_spent > current_setup_obj.hours_per_wk_day:
                    date_end = date_end + datetime.timedelta(days=2)
                    hours_to_spent -= current_setup_obj.hours_per_wk_day
                # -End- Repito esto nuevamente porque me puede quedar un tiempo en horas sobrante sin asignar
                dates_dict['date_end'] = date_end
                dates_dict['date_deadline'] = date_end
                dates_dict['last_day_used_hours'] = hours_to_spent
        elif starting_position == '1':# Validating parallel position
            if len(precedent_in_task_id):# Validating if the current detailine has a precedent
                date_start = datetime.datetime.strptime(precedent_data.date_start,'%Y-%m-%d %H:%M:%S')
                date_end = date_start
                if datetime.datetime.isoweekday(date_end) == 6:
                    date_end = date_end + datetime.timedelta(days=2)
                while hours_to_spent >= current_setup_obj.hours_per_normal_day:
                    if datetime.datetime.isoweekday(date_end) == 6:
                        date_end = date_end + datetime.timedelta(days=2)
                        hours_to_spent -= current_setup_obj.hours_per_wk_day
                    else:
                        date_end = date_end + datetime.timedelta(days=1)
                        hours_to_spent -= current_setup_obj.hours_per_normal_day
                # Repito esto nuevamente porque me puede quedar un tiempo en horas sobrante sin asignar
                if datetime.datetime.isoweekday(date_end) == 6 and hours_to_spent > current_setup_obj.hours_per_wk_day:
                    date_end = date_end + datetime.timedelta(days=2)
                    hours_to_spent -= current_setup_obj.hours_per_wk_day
                # -End- Repito esto nuevamente porque me puede quedar un tiempo en horas sobrante sin asignar
                dates_dict['date_start'] = date_start
                dates_dict['date_end'] = date_end
                dates_dict['date_deadline'] = date_end
                dates_dict['last_day_used_hours'] = hours_to_spent
            else:# Repito esto nuevamente porque me puede quedar un tiempo en horas sobrante sin asignar
                date_start = datetime.datetime.strptime(self.pool.get('neos.baseline').browse(cr, uid, current_baseline_id, context=None).date_start,'%Y-%m-%d %H:%M:%S')
                date_end =date_start
                dates_dict['date_start'] = date_start
                while hours_to_spent > current_setup_obj.hours_per_normal_day:
                    if datetime.datetime.isoweekday(date_end) == 6:
                        date_end = date_end + datetime.timedelta(days=2)
                        hours_to_spent -= current_setup_obj.hours_per_normal_day
                    elif datetime.datetime.isoweekday(date_end) == 7:
                        date_end = date_end + datetime.timedelta(days=1)
                    else:
                        date_end = date_end + datetime.timedelta(days=1)
                        hours_to_spent -= current_setup_obj.hours_per_normal_day
                # Repito esto nuevamente porque me puede quedar un tiempo en horas sobrante sin asignar
                if datetime.datetime.isoweekday(date_end) == 6 and hours_to_spent > current_setup_obj.hours_per_wk_day:
                    date_end = date_end + datetime.timedelta(days=2)
                    hours_to_spent -= current_setup_obj.hours_per_wk_day
                # -End- Repito esto nuevamente porque me puede quedar un tiempo en horas sobrante sin asignar 
                dates_dict['date_end'] = date_end
                dates_dict['date_deadline'] = date_end
                dates_dict['last_day_used_hours'] = hours_to_spent
        return dates_dict
    
    def get_dates_non_con_saturdays(self,cr, uid,hours_to_spent,starting_position,current_setup_obj,current_baseline_id,current_detailine_id,after_with):
        #**- Declaring auxiliary variables -**
        hours_used_lastday = 0
        dates_dict = {}
        date_start = 0
        date_end = 0
        flag_sat_dict = {}
        precedent_in_task_id = []
        #**-END- Declaring auxiliary variables -**
        # Getting 
        flag_sat = False
        if after_with:
            flag_sat = self.pool.get('neos.baseline.details').browse(cr,uid,after_with.id).last_sat_worked
            precedent_in_task_id = self.pool.get('project.task').search(cr, uid, [('detailine_id','=',after_with.id)], context=None)
            precedent_data = self.pool.get('project.task').browse(cr, uid, precedent_in_task_id[0], context=None)
        if starting_position == '0':#Position after
            if len(precedent_in_task_id):
                date_start = datetime.datetime.strptime(precedent_data.date_end,'%Y-%m-%d %H:%M:%S')
                date_end = date_start
                while hours_to_spent >= current_setup_obj.hours_per_normal_day:
                    if datetime.datetime.isoweekday(date_end) == 6 and flag_sat is False:
                        date_end = date_end + datetime.timedelta(days=2)
                        hours_to_spent -= current_setup_obj.hours_per_wk_day
                        flag_sat = True
                    elif datetime.datetime.isoweekday(date_end) == 6 and flag_sat is True:
                        date_end = date_end + datetime.timedelta(days=2)
                        flag_sat = False
                    else:
                        date_end = date_end + datetime.timedelta(days=1)
                        hours_to_spent -= current_setup_obj.hours_per_normal_day
                # Repito esto nuevamente porque me quedo un tiempo en horas sobrante sin asignar
                if datetime.datetime.isoweekday(date_end) == 6 and flag_sat is True:
                    date_end = date_end + datetime.timedelta(days=2)
                    flag_sat = False
                elif datetime.datetime.isoweekday(date_end) == 6 and hours_to_spent > current_setup_obj.hours_per_wk_day and flag_sat is False:
                    date_end = date_end + datetime.timedelta(days=2)
                    hours_to_spent -= current_setup_obj.hours_per_wk_day
                # -End- Repito esto nuevamente porque me quedo un tiempo en horas sobrante sin asignar
                flag_sat_dict['last_sat_worked'] = flag_sat 
                self.pool.get('neos.baseline.details').write(cr,uid,current_detailine_id,flag_sat_dict)
                dates_dict['date_start'] = date_start
                dates_dict['date_end'] = date_end
                dates_dict['date_deadline'] = date_end
                dates_dict['last_day_used_hours'] = hours_to_spent
            else:
                date_start = datetime.datetime.strptime(self.pool.get('neos.baseline').browse(cr, uid, current_baseline_id, context=None).date_start,'%Y-%m-%d %H:%M:%S')
                date_end = date_start
                while hours_to_spent >= current_setup_obj.hours_per_normal_day:
                    if datetime.datetime.isoweekday(date_end) == 6 and flag_sat is False:
                        date_end = date_end + datetime.timedelta(days=2)
                        hours_to_spent -= current_setup_obj.hours_per_wk_day
                        flag_sat = True
                    elif datetime.datetime.isoweekday(date_end) == 6 and flag_sat is True:
                        date_end = date_end + datetime.timedelta(days=2)
                        flag_sat = False
                    else:
                        date_end = date_end + datetime.timedelta(days=1)
                        hours_to_spent -= current_setup_obj.hours_per_normal_day
                # Repito esto nuevamente porque me quedó un tiempo en horas sobrante sin asignar
                if datetime.datetime.isoweekday(date_end) == 6 and flag_sat is True:
                    date_end = date_end + datetime.timedelta(days=2)
                    flag_sat = False
                elif datetime.datetime.isoweekday(date_end) == 6 and hours_to_spent > current_setup_obj.hours_per_wk_day and flag_sat is False:
                    date_end = date_end + datetime.timedelta(days=2)
                    hours_to_spent -= current_setup_obj.hours_per_wk_day
                    flag_sat = True
                # -End- Repito esto nuevamente porque me quedó un tiempo en horas sobrante sin asignar
                flag_sat_dict['last_sat_worked'] = flag_sat 
                self.pool.get('neos.baseline.details').write(cr,uid,current_detailine_id,flag_sat_dict)
                dates_dict['date_end'] = date_end
                dates_dict['date_deadline'] = date_end
                dates_dict['date_start'] = date_start
                dates_dict['last_day_used_hours'] = hours_to_spent
        elif starting_position == '1':#Validating parallel position
            if len(precedent_in_task_id):
                date_start = datetime.datetime.strptime(precedent_data.date_start,'%Y-%m-%d %H:%M:%S')
                date_end = date_start
                while hours_to_spent >= current_setup_obj.hours_per_normal_day:
                    if datetime.datetime.isoweekday(date_end) == 6 and flag_sat is False:
                        date_end = date_end + datetime.timedelta(days=2)
                        hours_to_spent -= current_setup_obj.hours_per_wk_day
                        flag_sat = True
                    elif datetime.datetime.isoweekday(date_end) == 6 and flag_sat is True:
                        date_end = date_end + datetime.timedelta(days=2)
                        flag_sat = False
                    else:
                        date_end = date_end + datetime.timedelta(days=1)
                        hours_to_spent -= current_setup_obj.hours_per_normal_day
                # Repito esto nuevamente porque me quedo un tiempo en horas sobrante sin asignar
                if datetime.datetime.isoweekday(date_end) == 6 and flag_sat is True:
                    date_end = date_end + datetime.timedelta(days=2)
                    flag_sat = False
                elif datetime.datetime.isoweekday(date_end) == 6 and hours_to_spent > current_setup_obj.hours_per_wk_day and flag_sat is False:
                    date_end = date_end + datetime.timedelta(days=2)
                    hours_to_spent -= current_setup_obj.hours_per_wk_day
                    flag_sat = True
                # -End- Repito esto nuevamente porque me quedo un tiempo en horas sobrante sin asignar
                flag_sat_dict['last_sat_worked'] = flag_sat 
                self.pool.get('neos.baseline.details').write(cr,uid,current_detailine_id,flag_sat_dict)
                dates_dict['date_end'] = date_end
                dates_dict['date_deadline'] = date_end
                dates_dict['date_start'] = date_start
                dates_dict['last_day_used_hours'] = hours_to_spent
            else:
                date_start = datetime.datetime.strptime(self.pool.get('neos.baseline').browse(cr, uid, current_baseline_id, context=None).date_start,'%Y-%m-%d %H:%M:%S')
                date_end = date_start
                while hours_to_spent >= current_setup_obj.hours_per_normal_day:
                    if datetime.datetime.isoweekday(date_end) == 6 and flag_sat is False:
                        date_end = date_end + datetime.timedelta(days=2)
                        hours_to_spent -= current_setup_obj.hours_per_wk_day
                        flag_sat = True
                    elif datetime.datetime.isoweekday(date_end) == 6 and flag_sat is True:
                        date_end = date_end + datetime.timedelta(days=2)
                        flag_sat = False
                    else:
                        date_end = date_end + datetime.timedelta(days=1)
                        hours_to_spent -= current_setup_obj.hours_per_normal_day
                # Repito esto nuevamente porque me quedo un tiempo en horas sobrante sin asignar
                if datetime.datetime.isoweekday(date_end) == 6 and flag_sat is True:
                    date_end = date_end + datetime.timedelta(days=2)
                    flag_sat = False
                elif datetime.datetime.isoweekday(date_end) == 6 and hours_to_spent > current_setup_obj.hours_per_wk_day and flag_sat is False:
                    date_end = date_end + datetime.timedelta(days=2)
                    hours_to_spent -= current_setup_obj.hours_per_wk_day
                    flag_sat = True
                # -End- Repito esto nuevamente porque me quedo un tiempo en horas sobrante sin asignar   
                flag_sat_dict['last_sat_worked'] = flag_sat 
                self.pool.get('neos.baseline.details').write(cr,uid,current_detailine_id,flag_sat_dict)
                dates_dict['date_end'] = date_end
                dates_dict['date_deadline'] = date_end
                dates_dict['date_start'] = date_start
                dates_dict['last_day_used_hours'] = hours_to_spent
        return dates_dict
make_planing()
