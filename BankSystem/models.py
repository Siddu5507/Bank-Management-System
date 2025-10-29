from decimal import Decimal
from django.db import models
from django.utils import timezone


class Account(models.Model):
    ACCOUNT_TYPES = [
        ("SAVINGS", "Savings"),
        ("CURRENT", "Current"),
    ]

    account_number = models.CharField(max_length=30, unique=True)
    holder_name = models.CharField(max_length=120)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPES, default="SAVINGS")
    balance = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["account_number"]

    def __str__(self):
        return f"{self.account_number} — {self.holder_name}"


class Transaction(models.Model):
    TXN_TYPES = [
        ("DEPOSIT", "Deposit"),
        ("WITHDRAWAL", "Withdrawal"),
        ("TRANSFER", "Transfer"),
    ]

    txn_type = models.CharField(max_length=10, choices=TXN_TYPES)
    # For DEPOSIT/WITHDRAWAL
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name="transactions", null=True, blank=True)
    # For TRANSFER
    from_account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name="outgoing_transfers", null=True, blank=True)
    to_account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name="incoming_transfers", null=True, blank=True)

    amount = models.DecimalField(max_digits=14, decimal_places=2)
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        base = f"{self.txn_type} {self.amount}"
        if self.txn_type == "TRANSFER":
            return f"{base} ({self.from_account} → {self.to_account})"
        if self.account:
            return f"{base} ({self.account})"
        return base
