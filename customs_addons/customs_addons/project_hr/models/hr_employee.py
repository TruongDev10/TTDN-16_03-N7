# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # ========== HOURLY RATE ==========
    hourly_rate = fields.Float(
        string='Mức lương theo giờ',
        default=0.0,
        tracking=True,
        help='Mức lương theo giờ để tính chi phí (sẽ dùng trong project_cost)'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Tiền tệ',
        default=lambda self: self.env.company.currency_id,
        help='Đơn vị tiền tệ cho hourly rate'
    )
    
    # ========== QUAN HỆ VỚI DỰ ÁN ==========
    project_ids = fields.Many2many(
        'project.project',
        'project_project_employee_rel',
        'employee_id',
        'project_id',
        string='Dự án',
        help='Danh sách dự án nhân viên tham gia'
    )
    
    project_count = fields.Integer(
        string='Số lượng Dự án',
        compute='_compute_project_count',
        store=False
    )
    
    task_ids = fields.Many2many(
        'project.task',
        'project_task_employee_rel',
        'employee_id',
        'task_id',
        string='Công việc',
        help='Danh sách công việc nhân viên được gán'
    )
    
    task_count = fields.Integer(
        string='Số lượng Công việc',
        compute='_compute_task_count',
        store=False
    )
    
    # ========== WORKLOAD ==========
    workload_hours = fields.Float(
        string='Tổng giờ công',
        compute='_compute_workload',
        store=False,
        help='Tổng số giờ công nhân viên đã làm (từ timesheet)'
    )
    
    workload_projects = fields.Integer(
        string='Số dự án đang tham gia',
        compute='_compute_workload',
        store=False
    )
    
    workload_tasks = fields.Integer(
        string='Số công việc đang làm',
        compute='_compute_workload',
        store=False
    )
    
    @api.depends('project_ids', 'task_ids')
    def _compute_project_count(self):
        """Tính số lượng dự án"""
        for record in self:
            record.project_count = len(record.project_ids)
    
    @api.depends('project_ids', 'task_ids')
    def _compute_task_count(self):
        """Tính số lượng công việc"""
        for record in self:
            record.task_count = len(record.task_ids)
    
    def _compute_workload(self):
        """Tính workload của nhân viên"""
        for record in self:
            # Placeholder: workload_hours sẽ được tính từ timesheet trong project_timesheet
            record.workload_hours = 0.0
            record.workload_projects = len(record.project_ids.filtered(lambda p: p.state == 'active'))
            record.workload_tasks = len(record.task_ids.filtered(lambda t: t.state in ['todo', 'in_progress', 'review']))
    
    def action_view_projects(self):
        """Mở view dự án của nhân viên"""
        action = {
            'name': 'Dự án',
            'type': 'ir.actions.act_window',
            'res_model': 'project.project',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.project_ids.ids)],
        }
        return action
    
    def action_view_tasks(self):
        """Mở view công việc của nhân viên"""
        action = {
            'name': 'Công việc',
            'type': 'ir.actions.act_window',
            'res_model': 'project.task',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.task_ids.ids)],
        }
        return action
