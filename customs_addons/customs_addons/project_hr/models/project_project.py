# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProjectProject(models.Model):
    _inherit = 'project.project'

    # ========== GÁN NHÂN VIÊN ==========
    employee_ids = fields.Many2many(
        'hr.employee',
        'project_project_employee_rel',
        'project_id',
        'employee_id',
        string='Nhân viên',
        help='Danh sách nhân viên được gán vào dự án'
    )
    
    employee_count = fields.Integer(
        string='Số lượng Nhân viên',
        compute='_compute_employee_count',
        store=False
    )
    
    @api.depends('employee_ids')
    def _compute_employee_count(self):
        """Tính số lượng nhân viên trong dự án"""
        for record in self:
            record.employee_count = len(record.employee_ids)
    
    def action_view_employees(self):
        """Mở view nhân viên của dự án"""
        action = {
            'name': 'Nhân viên',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.employee',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.employee_ids.ids)],
        }
        return action
