# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProjectTask(models.Model):
    _inherit = 'project.task'

    # ========== GÁN NHÂN VIÊN ==========
    user_ids = fields.Many2many(
        'res.users',
        'project_task_user_rel',
        'task_id',
        'user_id',
        string='Người thực hiện',
        help='Danh sách người dùng được gán vào công việc'
    )
    
    employee_ids = fields.Many2many(
        'hr.employee',
        'project_task_employee_rel',
        'task_id',
        'employee_id',
        string='Nhân viên',
        help='Danh sách nhân viên được gán vào công việc'
    )
    
    employee_count = fields.Integer(
        string='Số lượng Nhân viên',
        compute='_compute_employee_count',
        store=False
    )
    
    @api.depends('employee_ids')
    def _compute_employee_count(self):
        """Tính số lượng nhân viên trong công việc"""
        for record in self:
            record.employee_count = len(record.employee_ids)
    
    def action_view_employees(self):
        """Mở view nhân viên của công việc"""
        action = {
            'name': 'Nhân viên',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.employee',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.employee_ids.ids)],
        }
        return action
