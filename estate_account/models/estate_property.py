from odoo import models, Command
from odoo.exceptions import UserError


class EstatePropertyAccount(models.Model):
    _inherit = "estate.property"

    def action_sold_property(self):

        super().action_sold_property()

        for property in self:
            journal = self.env["account.journal"].search(
                [
                    ("type", "=", "sale")
                ],
                limit=1,
            )

            if not journal:
                raise UserError("No Sales Journal found for the current company. Please go to the Invoicing module -> Configuration -> Settings -> Fiscal Localization -> Select Spain - SMEs (2008) (This is the one I've tried and works fine with this module invoices' as it includes the Sales Journal and makes it easier to configure)")

            income_account = self.env["account.account"].search(
                [
                    ("account_type", "=", "income"),
                ],
                limit=1,
            )
            if not income_account:
                raise UserError("No income account found for the current company.")

            self.env["account.move"].create(
                {
                    "partner_id": property.buyer_id.id,
                    "move_type": "out_invoice",
                    "journal_id": journal.id,
                    "invoice_line_ids": [
                        Command.create(
                            {
                                "name": property.name,
                                "quantity": 1,
                                "price_unit": property.selling_price,
                                "account_id": income_account.id,
                            }
                        ),
                        Command.create(
                            {
                                "name": "6% Commission",
                                "quantity": 1,
                                "price_unit": property.selling_price * 0.06,
                                "account_id": income_account.id,
                            }
                        ),
                        Command.create(
                            {
                                "name": "Administrative Fees",
                                "quantity": 1,
                                "price_unit": 100.0,
                                "account_id": income_account.id,
                            }
                        ),
                    ],
                }
            )
