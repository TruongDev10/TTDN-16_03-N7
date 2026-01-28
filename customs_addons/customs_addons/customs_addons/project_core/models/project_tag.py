# -*- coding: utf-8 -*-

from odoo import models, fields


class ProjectTag(models.Model):
    _name = 'project.tag'
    _description = 'Nhãn Dự án'
    _order = 'name'

    name = fields.Char(
        string='Tên nhãn',
        required=True,
        translate=True
    )
    
    color = fields.Integer(
        string='Màu sắc',
        default=0
    )
