from django.db import transaction as dbtxn
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.core.exceptions import ValidationError
from .models import Account, Transaction
from .forms import AccountForm, TransactionForm


# ----------------- Account CRUD -----------------

def account_list(request):
    search = request.GET.get("search", "").strip()
    acc_type = request.GET.get("type", "").strip()
    active = request.GET.get("active", "")

    qs = Account.objects.all()
    if search:
        qs = qs.filter(
            Q(account_number__icontains=search) |
            Q(holder_name__icontains=search)
        )
    if acc_type:
        qs = qs.filter(account_type=acc_type)
    if active in ("true", "false"):
        qs = qs.filter(is_active=(active == "true"))

    return render(request, "BankSystem/account_list.html", {
        "accounts": qs,
        "search": search,
        "acc_type": acc_type,
        "active": active,
    })


def account_create(request):
    if request.method == "POST":
        form = AccountForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("banksystem:account_list")
    else:
        form = AccountForm()
    return render(request, "BankSystem/account_form.html", {"form": form, "title": "Add Account"})


def account_update(request, pk):
    account = get_object_or_404(Account, pk=pk)
    if request.method == "POST":
        form = AccountForm(request.POST, instance=account)
        if form.is_valid():
            form.save()
            return redirect("banksystem:account_list")
    else:
        form = AccountForm(instance=account)
    return render(request, "BankSystem/account_form.html", {"form": form, "title": "Edit Account"})


def account_delete(request, pk):
    account = get_object_or_404(Account, pk=pk)
    if request.method == "POST":
        account.delete()
        return redirect("banksystem:account_list")
    return render(request, "BankSystem/account_confirm_delete.html", {"account": account})


# ------------- Helpers to apply/reverse effects -------------

def _apply_effect(txn: Transaction, sign: int):
    """
    sign=+1 to apply, sign=-1 to reverse.
    Raises ValidationError if insufficient balance when applying.
    """
    amt = txn.amount
    if txn.txn_type == "DEPOSIT":
        acc = txn.account
        acc.balance = acc.balance + (amt * sign)
        acc.save(update_fields=["balance"])
    elif txn.txn_type == "WITHDRAWAL":
        acc = txn.account
        if sign == +1 and acc.balance < amt:
            raise ValidationError("Insufficient funds for withdrawal.")
        acc.balance = acc.balance - (amt * sign)
        acc.save(update_fields=["balance"])
    elif txn.txn_type == "TRANSFER":
        fa = txn.from_account
        ta = txn.to_account
        if sign == +1 and fa.balance < amt:
            raise ValidationError("Insufficient funds for transfer.")
        # apply: from -= amt ; to += amt
        fa.balance = fa.balance - (amt * sign)
        ta.balance = ta.balance + (amt * sign)
        fa.save(update_fields=["balance"])
        ta.save(update_fields=["balance"])


# ----------------- Transaction CRUD -----------------

def transaction_list(request):
    search = request.GET.get("search", "").strip()
    ttype = request.GET.get("type", "").strip()

    qs = Transaction.objects.select_related("account", "from_account", "to_account").all()
    if search:
        qs = qs.filter(
            Q(account__account_number__icontains=search) |
            Q(from_account__account_number__icontains=search) |
            Q(to_account__account_number__icontains=search) |
            Q(account__holder_name__icontains=search) |
            Q(from_account__holder_name__icontains=search) |
            Q(to_account__holder_name__icontains=search) |
            Q(note__icontains=search)
        )
    if ttype:
        qs = qs.filter(txn_type=ttype)

    return render(request, "BankSystem/transaction_list.html", {
        "transactions": qs,
        "search": search,
        "ttype": ttype,
    })


@dbtxn.atomic
def transaction_create(request):
    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            txn = form.save()         # saved to DB (atomic block ensures rollback on error)
            try:
                _apply_effect(txn, +1)
            except ValidationError as e:
                # roll back and show error
                raise dbtxn.TransactionManagementError(str(e))
            return redirect("banksystem:transaction_list")
    else:
        form = TransactionForm()
    return render(request, "BankSystem/transaction_form.html", {
        "form": form, "title": "Create Transaction"
    })


@dbtxn.atomic
def transaction_update(request, pk):
    txn = get_object_or_404(Transaction, pk=pk)
    if request.method == "POST":
        # snapshot BEFORE
        old = Transaction.objects.get(pk=pk)
        form = TransactionForm(request.POST, instance=txn)
        if form.is_valid():
            # reverse old
            _apply_effect(old, -1)
            # save new
            txn = form.save()
            # apply new
            _apply_effect(txn, +1)
            return redirect("banksystem:transaction_list")
    else:
        form = TransactionForm(instance=txn)
    return render(request, "BankSystem/transaction_form.html", {
        "form": form, "title": f"Edit Transaction #{txn.pk}"
    })


@dbtxn.atomic
def transaction_delete(request, pk):
    txn = get_object_or_404(Transaction, pk=pk)
    if request.method == "POST":
        # reverse then delete
        _apply_effect(txn, -1)
        txn.delete()
        return redirect("banksystem:transaction_list")
    return render(request, "BankSystem/transaction_confirm_delete.html", {"txn": txn})
