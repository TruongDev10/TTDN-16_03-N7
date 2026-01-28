# -*- coding: utf-8 -*-

from odoo import models, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def action_cleanup_demo_data(self):
        """Clean up English demo data"""
        demo_names = [
            'Azure Interior', 
            'Deco Addict', 
            'Gemini Furniture', 
            'Ready Mat', 
            'Lumber Inc',
            'Wood Corner',
            'Brandon Freeman',
            'Colleen Diaz',
            'Nicole Ford',
            'Addison Olson',
            'Douglas Fletcher',
            'Floyd Steward',
            'Edwin Hansen',
            'Jesse Brown',
            'Oscar Morgan'
        ]
        
        # Find partners that match or contain these names
        domain = []
        for name in demo_names:
            domain.append(('name', 'ilike', name))
        
        # Combine with OR logic
        if domain:
            final_domain = ['|'] * (len(domain) - 1) + domain
            partners = self.search(final_domain)
            
            # Delete them
            # We use a loop and try-except to avoid stopping on protected records
            deleted_count = 0
            for partner in partners:
                try:
                    partner.unlink()
                    deleted_count += 1
                except:
                    # If cannot delete (due to constraints), try to archive
                    try:
                        partner.write({'active': False})
                    except:
                        pass
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Dọn dẹp hoàn tất',
                    'message': f'Đã xóa/lưu trữ {deleted_count} khách hàng mẫu.',
                    'type': 'success',
                    'sticky': False,
                    'next': {'type': 'ir.actions.act_window_close'},
                }
            }
