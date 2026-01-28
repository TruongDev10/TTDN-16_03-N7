# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProjectProject(models.Model):
    _inherit = 'project.project'

    # ========== ANALYTIC ACCOUNT ==========
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Tài khoản Phân tích',
        help='Tài khoản phân tích cho dự án (dùng cho timesheet)'
    )
    
    # ========== TIMESHEET ==========
    timesheet_ids = fields.One2many(
        'account.analytic.line',
        'project_id',
        string='Timesheet',
        help='Danh sách timesheet của dự án (từ các task)'
    )
    
    timesheet_count = fields.Integer(
        string='Số lượng Timesheet',
        compute='_compute_timesheet_count',
        store=False
    )
    
    total_hours = fields.Float(
        string='Tổng giờ công',
        compute='_compute_total_hours',
        store=False,
        help='Tổng số giờ công của dự án'
    )
    
    @api.depends('task_ids', 'task_ids.timesheet_ids')
    def _compute_timesheet_count(self):
        """Tính số lượng timesheet từ các task"""
        for record in self:
            # Lấy tất cả timesheet từ các task của dự án
            all_timesheets = self.env['account.analytic.line'].search([
                ('task_id.project_id', '=', record.id)
            ])
            record.timesheet_count = len(all_timesheets)
    
    @api.depends('task_ids', 'task_ids.timesheet_ids', 'task_ids.timesheet_ids.unit_amount')
    def _compute_total_hours(self):
        """Tính tổng giờ công từ các task"""
        for record in self:
            # Lấy tất cả timesheet từ các task của dự án
            all_timesheets = self.env['account.analytic.line'].search([
                ('task_id.project_id', '=', record.id)
            ])
            total = sum(all_timesheets.mapped('unit_amount'))
            record.total_hours = total
    
    def action_view_timesheets(self):
        """Mở view timesheet của dự án"""
        action = {
            'name': 'Timesheet',
            'type': 'ir.actions.act_window',
            'res_model': 'account.analytic.line',
            'view_mode': 'tree,form',
            'domain': [('task_id.project_id', '=', self.id)],
            'context': {
                'default_account_id': self.analytic_account_id.id if self.analytic_account_id else False,
            },
        }
        return action
