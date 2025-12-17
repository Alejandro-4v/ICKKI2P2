from odoo import models, fields, api

from odoo.exceptions import UserError, ValidationError

from dateutil.relativedelta import relativedelta


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate Property Offer de Alejandro López"
    _order = "price desc"

    _check_price = models.Constraint(
        'CHECK(price > 0)',
        'The price must be strictly positive'
    )

    price = fields.Float("Price", required=True)
    validity = fields.Integer("Validity", default=7)
    date_deadline = fields.Date("Deadline", compute="_compute_date_deadline", inverse="_inverse_date_deadline", store=True)

    status = fields.Selection(
        [("accepted", "Accepted"), ("refused", "Refused")], copy=False
    )

    partner_id = fields.Many2one("res.partner", string="Partner", required=True)
    property_id = fields.Many2one("estate.property", string="Property", required=True, ondelete="cascade")

    @api.depends("validity")
    def _compute_date_deadline(self):
        for record in self:
            date = record.create_date.date() if record.create_date else fields.Date.today()
            record.date_deadline = date + relativedelta(days=record.validity)

    def _inverse_date_deadline(self):
        for record in self:
            date = record.create_date.date() if record.create_date else fields.Date.today()
            record.validity = (record.date_deadline - date).days
            print(f"inverse: {record.validity}")

    def action_accept_offer(self):
        if self.property_id.state != "offer_accepted":
            self.status = "accepted"
            self.property_id.state = "offer_accepted"
            self.property_id.selling_price = self.price
            self.property_id.buyer_id = self.partner_id
        else:
            raise UserError("An offer has already been accepted for this property.")

    def action_refuse_offer(self):
        self.status = "refused"
        self.property_id.state = "offer_received"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            property_rec = self.env["estate.property"].browse(vals.get("property_id"))

            if property_rec.offer_ids:
                max_price = max(property_rec.offer_ids.mapped("price"))
                if vals.get("price") < max_price:
                    raise ValidationError(
                        "You cannot make an offer lower than an existing one."
                    )

        offers = super().create(vals_list)

        for offer in offers:
            offer.property_id.state = "offer_received"

        return offers
