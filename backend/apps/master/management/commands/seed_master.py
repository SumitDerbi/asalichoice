"""Idempotent seeder for M01 Master Management.

Seeds India + states + curated top cities, default UoMs, GST tax slabs,
default payment modes, and the HQ branch (replacing the Phase-0 placeholder).

Usage::

    python manage.py seed_master              # idempotent
    python manage.py seed_master --reset      # DEBUG only — drops + re-creates
"""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.master.models import (
    Branch,
    BranchType,
    City,
    Country,
    PaymentMode,
    State,
    Tax,
    UnitOfMeasure,
)
from apps.master.seed_data import (
    DEFAULT_BRANCH,
    DEFAULT_PAYMENT_MODES,
    DEFAULT_TAX_SLABS,
    DEFAULT_UOMS,
    INDIA,
    INDIAN_STATES,
    TOP_CITIES,
    gst_components,
)


class Command(BaseCommand):
    help = "Seed Phase-1 master-management defaults (idempotent)."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--reset",
            action="store_true",
            help="DEBUG only: delete seeded rows before re-creating.",
        )

    @transaction.atomic
    def handle(self, *args, **options) -> None:
        if options["reset"]:
            if not settings.DEBUG:
                raise CommandError("--reset is only allowed when DEBUG=True.")
            self._reset()

        country = self._seed_country()
        states = self._seed_states(country)
        self._seed_cities(states)
        self._seed_uoms()
        self._seed_taxes()
        self._seed_payment_modes()
        self._seed_branch()

        self.stdout.write(self.style.SUCCESS("seed_master: completed."))

    # ------------------------------------------------------------------ #
    # Individual sections                                                #
    # ------------------------------------------------------------------ #

    def _seed_country(self) -> Country:
        country, created = Country.objects.get_or_create(
            iso2=INDIA["iso2"],
            defaults={
                "iso3": INDIA["iso3"],
                "name": INDIA["name"],
                "phone_code": INDIA["phone_code"],
                "currency": INDIA["currency"],
            },
        )
        self.stdout.write(f"  country: {country.name} {'[created]' if created else '[exists]'}")
        return country

    def _seed_states(self, country: Country) -> dict[str, State]:
        out: dict[str, State] = {}
        for code, name, gst in INDIAN_STATES:
            state, _ = State.objects.get_or_create(
                country=country,
                code=code,
                defaults={"name": name, "gst_state_code": gst},
            )
            out[code] = state
        self.stdout.write(f"  states: {len(out)} ensured")
        return out

    def _seed_cities(self, states: dict[str, State]) -> None:
        created_count = 0
        for state_code, city_name in TOP_CITIES:
            state = states.get(state_code)
            if state is None:
                continue
            _, created = City.objects.get_or_create(state=state, name=city_name)
            if created:
                created_count += 1
        self.stdout.write(f"  cities: {len(TOP_CITIES)} ensured ({created_count} new)")

    def _seed_uoms(self) -> None:
        for code, name, symbol, decimals in DEFAULT_UOMS:
            UnitOfMeasure.objects.get_or_create(
                code=code,
                defaults={"name": name, "symbol": symbol, "decimals": decimals},
            )
        self.stdout.write(f"  uoms: {len(DEFAULT_UOMS)} ensured")

    def _seed_taxes(self) -> None:
        for code, name, rate_str in DEFAULT_TAX_SLABS:
            Tax.objects.get_or_create(
                code=code,
                defaults={
                    "name": name,
                    "rate_total": Decimal(rate_str),
                    "components_json": gst_components(rate_str),
                },
            )
        self.stdout.write(f"  taxes: {len(DEFAULT_TAX_SLABS)} ensured")

    def _seed_payment_modes(self) -> None:
        for code, name, ptype, is_online in DEFAULT_PAYMENT_MODES:
            PaymentMode.objects.get_or_create(
                code=code,
                defaults={"name": name, "type": ptype, "is_online": is_online},
            )
        self.stdout.write(f"  payment_modes: {len(DEFAULT_PAYMENT_MODES)} ensured")

    def _seed_branch(self) -> None:
        Branch.objects.get_or_create(
            code=DEFAULT_BRANCH["code"],
            defaults={
                "name": DEFAULT_BRANCH["name"],
                "type": BranchType(DEFAULT_BRANCH["type"]),
            },
        )
        self.stdout.write("  branch: HQ ensured")

    # ------------------------------------------------------------------ #
    def _reset(self) -> None:
        from django.db.models import Q

        seeded_state_codes = {code for code, _, _ in INDIAN_STATES}
        seeded_city_pairs = set(TOP_CITIES)
        seeded_uom_codes = {code for code, *_ in DEFAULT_UOMS}
        seeded_tax_codes = {code for code, *_ in DEFAULT_TAX_SLABS}
        seeded_pm_codes = {code for code, *_ in DEFAULT_PAYMENT_MODES}

        Branch.objects.filter(code=DEFAULT_BRANCH["code"]).delete()
        PaymentMode.objects.filter(code__in=seeded_pm_codes).delete()
        Tax.objects.filter(code__in=seeded_tax_codes).delete()
        UnitOfMeasure.objects.filter(code__in=seeded_uom_codes).delete()
        # Cities: drop only the curated ones.
        city_q = Q()
        for state_code, city_name in seeded_city_pairs:
            city_q |= Q(state__code=state_code, name=city_name)
        if city_q:
            City.objects.filter(city_q).delete()
        State.objects.filter(country__iso2=INDIA["iso2"], code__in=seeded_state_codes).delete()
        Country.objects.filter(iso2=INDIA["iso2"]).delete()
        self.stdout.write(self.style.WARNING("  reset: seeded rows removed."))
