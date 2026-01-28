# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProjectTask(models.Model):
    _inherit = 'project.task'

    # ========== QUAN HỆ VỚI TIMESHEET ==========
    timesheet_ids = fields.One2many(
        'account.analytic.line',
        'task_id',
        string='Timesheet',
        help='Danh sách timesheet của công việc'
    )
    
    timesheet_count = fields.Integer(
        string='Số lượng Timesheet',
        compute='_compute_timesheet_count',
        store=False
    )
    
    # ========== OVERRIDE COMPUTE ==========
    @api.depends('timesheet_ids', 'timesheet_ids.unit_amount')
    def _compute_effective_hours(self):
        """Tính giờ công thực tế từ timesheet"""
        for record in self:
            total_hours = sum(record.timesheet_ids.mapped('unit_amount'))
            record.effective_hours = total_hours
    
    @api.depends('timesheet_ids')
    def _compute_timesheet_count(self):
        """Tính số lượng timesheet"""
        for record in self:
            record.timesheet_count = len(record.timesheet_ids)
    
    def action_view_timesheets(self):
        """Mở view timesheet của công việc"""
        action = {
            'name': 'Timesheet',
            'type': 'ir.actions.act_window',
            'res_model': 'account.analytic.line',
            'view_mode': 'tree,form',
            'domain': [('task_id', '=', self.id)],
            'context': {
                'default_task_id': self.id,
                'default_project_id': self.project_id.id,
                'default_account_id': self.project_id.analytic_account_id.id if self.project_id.analytic_account_id else False,
            },
        }
        return action
