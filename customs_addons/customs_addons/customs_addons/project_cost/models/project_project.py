# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProjectProject(models.Model):
    _inherit = 'project.project'

    # ========== CHI PHÍ ==========
    cost_line_ids = fields.One2many(
        'project.cost.line',
        'project_id',
        string='Chi phí',
        help='Danh sách chi phí của dự án'
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
        help='Tổng chi phí của dự án'
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
        """Mở view chi phí của dự án"""
        action = {
            'name': 'Chi phí',
            'type': 'ir.actions.act_window',
            'res_model': 'project.cost.line',
            'view_mode': 'tree,form',
            'domain': [('project_id', '=', self.id)],
            'context': {
                'default_project_id': self.id,
            },
        }
        return action
    
    def action_compute_cost_from_timesheet(self):
        """Tự động tính chi phí từ timesheet của tất cả task trong dự án"""
        for record in self:
            # Lấy tất cả task của dự án
            tasks = self.env['project.task'].search([('project_id', '=', record.id)])
            for task in tasks:
                task.action_compute_cost_from_timesheet()
