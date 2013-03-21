
select imd.name, imd.module, data.menu_id, data.menu_name, data.group_id, data.group_name, data.category_name

from
ir_model_data imd,  
(select ium.id as menu_id, ium.name as menu_name, rg.id as group_id, rg.name as group_name, img.name as category_name
from ir_ui_menu ium 
inner join ir_ui_menu_group_rel iumgr on ium.id = iumgr.menu_id
inner join res_groups rg on rg.id = iumgr.gid
inner join ir_module_category img on rg.category_id = img.id
where ium.name like 'Work system') as data

where
(imd.res_id = data.menu_id and imd.model = 'ir.ui.menu') 
or
(imd.res_id = data.group_id and imd.model = 'res.groups')

order by data.menu_id, data.group_id

