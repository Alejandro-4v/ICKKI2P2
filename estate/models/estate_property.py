from datetime import datetime, timedelta

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

from odoo.tools.float_utils import float_compare, float_is_zero


def threeMonthsFromToday() -> datetime:
    return datetime.today() + timedelta(days=90)


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Estate Property de Alejandro López"
    _order = "id desc"

    _check_expected_price = models.Constraint(
        'CHECK(expected_price > 0)',
        'The expected price must be strictly positive'
    )

    _check_selling_price = models.Constraint(
        'CHECK(selling_price >= 0)',
        'The offer price must be positive'
    )

    name = fields.Char("Plan Name", required=True, translate=True)
    description = fields.Text("Description")
    postcode = fields.Char("Postcode")
    date_availability = fields.Date(
        "Availability Date", default=threeMonthsFromToday(), copy=False
    )
    expected_price = fields.Float("Expected Price", required=True)
    selling_price = fields.Float("Selling Price", readonly=True, copy=False)
    bedrooms = fields.Integer("Bedrooms", default=2)
    living_area = fields.Integer("Living Area")
    facades = fields.Integer("Facades")
    garage = fields.Boolean("Garage")
    garden = fields.Boolean("Garden")
    garden_area = fields.Integer("Garden Area")
    garden_orientation = fields.Selection(
        [("north", "North"), ("south", "South"), ("east", "East"), ("west", "West")]
    )

    active = fields.Boolean("Active", default=True)
    state = fields.Selection(
        [
            ("new", "New"),
            ("offer_received", "Offer Received"),
            ("offer_accepted", "Offer Accepted"),
            ("sold", "Sold"),
            ("canceled", "Canceled"),
        ],
        default="new",
        copy=False,
    )

    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    property_tags_ids = fields.Many2many("estate.property.tag", string="Property Tags")

    buyer_id = fields.Many2one("res.partner", string="Buyer", copy=False)
    seller_id = fields.Many2one("res.users", string="Salesman", default=lambda self: self.env.user)

    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")

    total_area = fields.Integer("Total Area", compute="_compute_total_area")
    best_price = fields.Float("Best Price", compute="_compute_best_price")

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for record in self:
            if record.offer_ids:
                record.best_price = max(record.offer_ids.mapped("price"))
            else:
                record.best_price = 0.0

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = "north"
        else:
            self.garden_area = 0
            self.garden_orientation = ""

    def action_sold_property(self):
        if self.state != "canceled":
            self.state = "sold"
        else:
            raise UserError("Canceled properties cannot be sold.")


    def action_cancel_property(self):
        if self.state != "sold":
            self.state = "canceled"
        else:
            raise UserError("Sold properties cannot be canceled.")

    @api.constrains("selling_price", "expected_price")
    def _check_selling_price_vs_expected_price(self):
        for record in self:
            if float_is_zero(record.selling_price, precision_rounding=0.01):
                continue

            minimum_price = record.expected_price * 0.9

            if float_compare(
                record.selling_price,
                minimum_price,
                precision_rounding=0.01,
            ) < 0:
                raise ValidationError(
                    "The selling price cannot be lower than 90% of the expected price."
                )
    
    def search_default_available(self):
        return [record for record in self if 'available' in record.name.lower()]
    
    def unlink(self):
            for record in self:
                if record.state not in ('new', 'canceled'):
                    raise UserError(
                        "You can only delete properties in New or Canceled state."
                    )
            return super().unlink()