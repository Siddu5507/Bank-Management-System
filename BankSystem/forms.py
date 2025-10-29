from django import forms
from .models import Account, Transaction

class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ["account_number", "holder_name", "account_type", "balance", "is_active"]
        widgets = {
            "account_number": forms.TextInput(attrs={"class": "form-control"}),
            "holder_name": forms.TextInput(attrs={"class": "form-control"}),
            "account_type": forms.Select(attrs={"class": "form-select"}),
            "balance": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": 0}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["txn_type", "account", "from_account", "to_account", "amount", "note"]
        widgets = {
            "txn_type": forms.Select(attrs={"class": "form-select", "hx-target": "this"}),
            "account": forms.Select(attrs={"class": "form-select"}),
            "from_account": forms.Select(attrs={"class": "form-select"}),
            "to_account": forms.Select(attrs={"class": "form-select"}),
            "amount": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": 0}),
            "note": forms.TextInput(attrs={"class": "form-control", "placeholder": "Optional"}),
        }

    def clean(self):
        cleaned = super().clean()
        t = cleaned.get("txn_type")
        account = cleaned.get("account")
        from_acc = cleaned.get("from_account")
        to_acc = cleaned.get("to_account")
        amount = cleaned.get("amount")

        if not amount or amount <= 0:
            self.add_error("amount", "Amount must be greater than 0.")

        if t in ("DEPOSIT", "WITHDRAWAL"):
            if not account:
                self.add_error("account", "Select an account.")
            cleaned["from_account"] = None
            cleaned["to_account"] = None

        if t == "TRANSFER":
            if not from_acc or not to_acc:
                self.add_error("from_account", "Both from and to accounts are required.")
                self.add_error("to_account", "Both from and to accounts are required.")
            elif from_acc == to_acc:
                self.add_error("to_account", "From and To accounts must be different.")
            cleaned["account"] = None

        return cleaned
