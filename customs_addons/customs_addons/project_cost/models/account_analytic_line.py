# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    # ========== QUAN HỆ VỚI COST ==========
    cost_line_id = fields.Many2one(
        'project.cost.line',
        string='Chi phí',
        readonly=True,
        help='Chi phí được tạo từ timesheet này'
    )
    
    cost_amount = fields.Float(
        string='Chi phí',
        compute='_compute_cost_amount',
        store=False,
        help='Chi phí = Giờ công × Mức lương theo giờ'
    )
    
    @api.depends('unit_amount', 'employee_id', 'employee_id.hourly_rate')
    def _compute_cost_amount(self):
        """Tính chi phí từ timesheet"""
        for record in self:
            if record.employee_id and record.employee_id.hourly_rate > 0:
                record.cost_amount = record.unit_amount * record.employee_id.hourly_rate
            else:
                record.cost_amount = 0.0
