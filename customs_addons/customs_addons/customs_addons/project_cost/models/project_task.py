# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProjectTask(models.Model):
    _inherit = 'project.task'

    # ========== CHI PHÍ ==========
    cost_line_ids = fields.One2many(
        'project.cost.line',
        'task_id',
        string='Chi phí',
        help='Danh sách chi phí của công việc'
    )
    
    cost_count = fields.Integer(
        string='Số lượng Chi phí',
        compute='_compute_cost_count',
        store=False
    )
    
    total_cost = fields.Float(
        string='Tổng chi phí',
        compute='_compute_total_cost',
        store=False,
        help='Tổng chi phí của công việc'
    )
    
    @api.depends('cost_line_ids')
    def _compute_cost_count(self):
        """Tính số lượng cost line"""
        for record in self:
            record.cost_count = len(record.cost_line_ids)
    
    @api.depends('cost_line_ids', 'cost_line_ids.cost_amount')
    def _compute_total_cost(self):
        """Tính tổng chi phí"""
        for record in self:
            total = sum(record.cost_line_ids.mapped('cost_amount'))
            record.total_cost = total
    
    def action_view_costs(self):
        """Mở view chi phí của công việc"""
        action = {
            'name': 'Chi phí',
            'type': 'ir.actions.act_window',
            'res_model': 'project.cost.line',
            'view_mode': 'tree,form',
            'domain': [('task_id', '=', self.id)],
            'context': {
                'default_task_id': self.id,
                'default_project_id': self.project_id.id,
            },
        }
        return action
    
    def action_compute_cost_from_timesheet(self):
        """Tự động tính chi phí từ timesheet"""
        for record in self:
            # Lấy tất cả timesheet chưa có cost line
            timesheets = record.timesheet_ids.filtered(
                lambda t: not t.cost_line_id and t.employee_id and t.employee_id.hourly_rate > 0
            )
            
            for timesheet in timesheets:
                self.env['project.cost.line'].create({
                    'name': f'Chi phí từ timesheet: {timesheet.name}',
                    'date': timesheet.date,
                    'project_id': record.project_id.id,
                    'task_id': record.id,
                    'timesheet_id': timesheet.id,
                    'employee_id': timesheet.employee_id.id,
                    'hours': timesheet.unit_amount,
                    'hourly_rate': timesheet.employee_id.hourly_rate,
                    'state': 'confirmed',
                })
