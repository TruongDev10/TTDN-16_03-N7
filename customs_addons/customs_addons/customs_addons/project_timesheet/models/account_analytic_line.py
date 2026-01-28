# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    # ========== QUAN HỆ VỚI TASK ==========
    task_id = fields.Many2one(
        'project.task',
        string='Công việc',
        ondelete='cascade',
        index=True,
        help='Công việc liên quan đến timesheet này'
    )
    
    # ========== THÔNG TIN BỔ SUNG ==========
    employee_id = fields.Many2one(
        'hr.employee',
        string='Nhân viên',
        compute='_compute_employee_id',
        store=True,
        readonly=True,
        help='Nhân viên thực hiện timesheet này'
    )
    
    @api.depends('user_id')
    def _compute_employee_id(self):
        """Tính employee_id từ user_id"""
        for record in self:
            if record.user_id:
                # Tìm employee có user_id trùng với user hiện tại
                employee = self.env['hr.employee'].search([
                    ('user_id', '=', record.user_id.id)
                ], limit=1)
                record.employee_id = employee.id if employee else False
            else:
                record.employee_id = False
    
    project_id = fields.Many2one(
        'project.project',
        string='Dự án',
        related='task_id.project_id',
        store=True,
        readonly=True,
        help='Dự án của công việc'
    )
    
    # ========== COMPUTE ==========
    @api.model
    def create(self, vals):
        """Xử lý khi tạo timesheet mới"""
        # Nếu có task_id, tự động set project_id và account_id
        if vals.get('task_id'):
            task = self.env['project.task'].browse(vals['task_id'])
            if task.project_id:
                # Tạo hoặc lấy analytic account cho project
                if not task.project_id.analytic_account_id:
                    # Tạo analytic account nếu chưa có
                    analytic_account = self.env['account.analytic.account'].create({
                        'name': task.project_id.name,
                        'code': task.project_id.code,
                    })
                    task.project_id.write({'analytic_account_id': analytic_account.id})
                vals['account_id'] = task.project_id.analytic_account_id.id
        
        return super(AccountAnalyticLine, self).create(vals)
    
    def write(self, vals):
        """Xử lý khi cập nhật timesheet"""
        # Nếu thay đổi task_id, cập nhật project_id và account_id
        if vals.get('task_id'):
            task = self.env['project.task'].browse(vals['task_id'])
            if task.project_id:
                if not task.project_id.analytic_account_id:
                    analytic_account = self.env['account.analytic.account'].create({
                        'name': task.project_id.name,
                        'code': task.project_id.code,
                    })
                    task.project_id.write({'analytic_account_id': analytic_account.id})
                vals['account_id'] = task.project_id.analytic_account_id.id
        
        return super(AccountAnalyticLine, self).write(vals)
