from odoo import models, api, fields
import logging

_logger = logging.getLogger(__name__)

class AccountJournal(models.Model):
    _inherit = 'account.journal'
    
    def get_pending_payments(self):
        if self.type not in ['bank', 'cash']:
            _logger.warning(f"El diario {self.name} no es de tipo 'bank' o 'cash'. No se obtendrán pagos pendientes.")
            return []
    
        _logger.warning(f"Fetching pending payments for journal ID: {self.id} - {self.name}")
        
        # Consulta SQL para obtener pagos pendientes
        self.env.cr.execute("""
            SELECT payment.id AS payment_id,
                   payment.payment_type AS payment_type,
                   payment.amount AS amount,
                   payment.currency_id AS currency_id,
                   payment.partner_id AS partner_id,
                   payment.move_id AS move_id
              FROM account_payment payment
              JOIN account_move move ON move.id = payment.move_id
             WHERE payment.is_matched IS NOT TRUE
               AND move.state = 'posted'
               AND move.journal_id = %s
          """, (self.id,))  # Asegúrate de que el ID sea una tupla con una coma al final
        
        # Obtener el resultado de la consulta
        pending_payments = self.env.cr.dictfetchall()
        
        _logger.info(f"Found {len(pending_payments)} pending payments for journal {self.name}")
        
        payments_data = []
        total = 0
        for payment in pending_payments:
            _logger.info(f"Processing payment ID: {payment['payment_id']}")
            payment_info = {
                'id': payment['payment_id'],
                'payment_type': payment['payment_type'],
                'amount': payment['amount'],
                'currency': self.env['res.currency'].browse(payment['currency_id']).name,
                'partner': self.env['res.partner'].browse(payment['partner_id']).name,
                'conciliado': False,  # Agrega lógica para reconciliación si es necesario
                'move_id': payment['move_id'],
            }
            if payment['payment_type'] == "inbound":
                total += payment['amount']
            elif payment['payment_type'] == "outbound":
                total -= payment['amount']
        
            payments_data.append(payment_info)
            _logger.info(f"Payment details: {payment_info}")
        
        _logger.warning(f"Total amount: {total}")
        _logger.warning(f"Completed fetching pending payments for journal ID: {self.id}")
        return payments_data
    

    def action_get_pending_payments(self):
        _logger.warning(f"Fetching pending payments for journal ID: {self.id}")
        
        # Llama a la función que obtiene los pagos pendientes para el diario
        pending_payments = self.get_pending_payments()

        # Si no se encuentran pagos, muestra un mensaje de advertencia
        if not pending_payments:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Sin Pagos Pendientes',
                    'message': 'No se encontraron pagos pendientes para este diario.',
                    'sticky': False,
                    'type': 'warning',
                }
            }

        # Redirige a la vista de lista de pagos pendientes
        payment_ids = [payment['id'] for payment in pending_payments]
        return {
            'name': 'Pagos Pendientes',  # Título de la ventana
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', payment_ids)],
            'target': 'current',  # Muestra en la ventana actual
        }



    
