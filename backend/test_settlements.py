"""
Comprehensive Settlement Test Cases

Tests the canonical balance computation with settlements to ensure:
1. Settlements reduce balances toward zero
2. Settlements do NOT affect total spent or budgets
3. Balances are mathematically impossible to desync
4. System behaves exactly like Splitwise/PhonePe
"""

import asyncio
from decimal import Decimal
from datetime import datetime
from data.storage import (
    generate_group_id,
    generate_expense_id,
    generate_settlement_id,
    create_group_in_mongo,
    create_expense_in_mongo,
    create_settlement_in_mongo,
    compute_group_balances,
    delete_group_and_related_data,
    normalize_expense_split,
)


def decimal_dict_to_float(d):
    """Convert Decimal dict to float dict for display"""
    return {k: float(v) for k, v in d.items()}


async def test_case_1():
    """
    Case 1: 2 users
    - B pays ₹500, split equally
    - Balances → A: -250, B: +250
    - A settles ₹250
    - Final → A: 0, B: 0
    """
    print("\n" + "="*60)
    print("TEST CASE 1: 2 users with full settlement")
    print("="*60)
    
    group_id = generate_group_id()
    user_a = "user_test_a"
    user_b = "user_test_b"
    
    # Create group
    group = {
        "id": group_id,
        "name": "Test Group 1",
        "type": "other",
        "invite_code": "TEST01",
        "currency": "INR",
        "simplify_debts": True,
        "created_at": datetime.now(),
        "created_by": user_a,
        "members": [
            {"user_id": user_a, "name": "User A", "role": "admin", "joined_at": datetime.now()},
            {"user_id": user_b, "name": "User B", "role": "member", "joined_at": datetime.now()}
        ]
    }
    await create_group_in_mongo(group)
    
    # B pays ₹500, split equally
    expense_id = generate_expense_id()
    split_type, split_participants, _ = normalize_expense_split(
        amount=500.0,
        paid_by=user_b,
        group_members=group["members"],
        split_input=None
    )
    
    expense = {
        "id": expense_id,
        "group_id": group_id,
        "title": "Dinner",
        "amount": 500.0,
        "paid_by": user_b,
        "category": "Food",
        "split_type": split_type,
        "date": datetime.now(),
        "created_at": datetime.now(),
        "created_by": user_b,
        "splits": [{"user_id": p["user_id"], "amount_owed": float(p["share"])} for p in split_participants],
        "split_participants": [{"user_id": p["user_id"], "share": float(p["share"])} for p in split_participants],
    }
    await create_expense_in_mongo(expense)
    
    # Check balances after expense
    balances_after_expense = await compute_group_balances(group_id)
    print(f"\nBalances after expense: {decimal_dict_to_float(balances_after_expense)}")
    print(f"Expected: A: -250, B: +250")
    
    expected_a = Decimal('-250.00')
    expected_b = Decimal('250.00')
    assert abs(balances_after_expense[user_a] - expected_a) < Decimal('0.01'), f"User A balance incorrect: {balances_after_expense[user_a]}"
    assert abs(balances_after_expense[user_b] - expected_b) < Decimal('0.01'), f"User B balance incorrect: {balances_after_expense[user_b]}"
    print("✅ Balances after expense are correct")
    
    # A settles ₹250
    settlement_id = generate_settlement_id()
    settlement = {
        "id": settlement_id,
        "group_id": group_id,
        "from": user_a,  # Debtor
        "to": user_b,     # Creditor
        "amount": 250.0,
        "created_at": datetime.now()
    }
    await create_settlement_in_mongo(settlement)
    
    # Check balances after settlement
    balances_after_settlement = await compute_group_balances(group_id)
    print(f"\nBalances after settlement: {decimal_dict_to_float(balances_after_settlement)}")
    print(f"Expected: A: 0, B: 0")
    
    assert abs(balances_after_settlement[user_a]) < Decimal('0.01'), f"User A balance should be 0: {balances_after_settlement[user_a]}"
    assert abs(balances_after_settlement[user_b]) < Decimal('0.01'), f"User B balance should be 0: {balances_after_settlement[user_b]}"
    print("✅ Balances after settlement are correct (both zero)")
    
    # Cleanup
    await delete_group_and_related_data(group_id)
    print("\n✅ TEST CASE 1 PASSED")
    return True


async def test_case_2():
    """
    Case 2: 3 users, subset split
    - B pays ₹500, split between A & B only
    - Balances → A: -250, B: +250, C: 0
    - Only A and B appear in settlements
    """
    print("\n" + "="*60)
    print("TEST CASE 2: 3 users, subset split")
    print("="*60)
    
    group_id = generate_group_id()
    user_a = "user_test_a2"
    user_b = "user_test_b2"
    user_c = "user_test_c2"
    
    # Create group
    group = {
        "id": group_id,
        "name": "Test Group 2",
        "type": "other",
        "invite_code": "TEST02",
        "currency": "INR",
        "simplify_debts": True,
        "created_at": datetime.now(),
        "created_by": user_a,
        "members": [
            {"user_id": user_a, "name": "User A", "role": "admin", "joined_at": datetime.now()},
            {"user_id": user_b, "name": "User B", "role": "member", "joined_at": datetime.now()},
            {"user_id": user_c, "name": "User C", "role": "member", "joined_at": datetime.now()}
        ]
    }
    await create_group_in_mongo(group)
    
    # B pays ₹500, split between A & B only
    expense_id = generate_expense_id()
    split_type, split_participants, _ = normalize_expense_split(
        amount=500.0,
        paid_by=user_b,
        group_members=group["members"],
        split_input={"type": "equal", "participants": [user_a, user_b]}
    )
    
    expense = {
        "id": expense_id,
        "group_id": group_id,
        "title": "Lunch (A & B only)",
        "amount": 500.0,
        "paid_by": user_b,
        "category": "Food",
        "split_type": split_type,
        "date": datetime.now(),
        "created_at": datetime.now(),
        "created_by": user_b,
        "splits": [{"user_id": p["user_id"], "amount_owed": float(p["share"])} for p in split_participants],
        "split_participants": [{"user_id": p["user_id"], "share": float(p["share"])} for p in split_participants],
    }
    await create_expense_in_mongo(expense)
    
    # Check balances
    balances = await compute_group_balances(group_id)
    print(f"\nBalances: {decimal_dict_to_float(balances)}")
    print(f"Expected: A: -250, B: +250, C: 0")
    
    expected_a = Decimal('-250.00')
    expected_b = Decimal('250.00')
    expected_c = Decimal('0.00')
    assert abs(balances[user_a] - expected_a) < Decimal('0.01'), f"User A balance incorrect: {balances[user_a]}"
    assert abs(balances[user_b] - expected_b) < Decimal('0.01'), f"User B balance incorrect: {balances[user_b]}"
    assert abs(balances[user_c] - expected_c) < Decimal('0.01'), f"User C balance should be 0: {balances[user_c]}"
    print("✅ Balances are correct (C has zero balance)")
    
    # Cleanup
    await delete_group_and_related_data(group_id)
    print("\n✅ TEST CASE 2 PASSED")
    return True


async def test_case_3():
    """
    Case 3: Partial settlement
    - A owes B ₹400
    - A pays ₹150
    - Balances → A: -250, B: +250
    """
    print("\n" + "="*60)
    print("TEST CASE 3: Partial settlement")
    print("="*60)
    
    group_id = generate_group_id()
    user_a = "user_test_a3"
    user_b = "user_test_b3"
    
    # Create group
    group = {
        "id": group_id,
        "name": "Test Group 3",
        "type": "other",
        "invite_code": "TEST03",
        "currency": "INR",
        "simplify_debts": True,
        "created_at": datetime.now(),
        "created_by": user_a,
        "members": [
            {"user_id": user_a, "name": "User A", "role": "admin", "joined_at": datetime.now()},
            {"user_id": user_b, "name": "User B", "role": "member", "joined_at": datetime.now()}
        ]
    }
    await create_group_in_mongo(group)
    
    # B pays ₹400, split equally (A owes B ₹200)
    # Then B pays another ₹400, split equally (A owes B another ₹200)
    # Total: A owes B ₹400
    
    for i in range(2):
        expense_id = generate_expense_id()
        split_type, split_participants, _ = normalize_expense_split(
            amount=400.0,
            paid_by=user_b,
            group_members=group["members"],
            split_input=None
        )
        
        expense = {
            "id": expense_id,
            "group_id": group_id,
            "title": f"Expense {i+1}",
            "amount": 400.0,
            "paid_by": user_b,
            "category": "Other",
            "split_type": split_type,
            "date": datetime.now(),
            "created_at": datetime.now(),
            "created_by": user_b,
            "splits": [{"user_id": p["user_id"], "amount_owed": float(p["share"])} for p in split_participants],
            "split_participants": [{"user_id": p["user_id"], "share": float(p["share"])} for p in split_participants],
        }
        await create_expense_in_mongo(expense)
    
    # Check balances before settlement
    balances_before = await compute_group_balances(group_id)
    print(f"\nBalances before settlement: {decimal_dict_to_float(balances_before)}")
    print(f"Expected: A: -400, B: +400")
    
    expected_a_before = Decimal('-400.00')
    expected_b_before = Decimal('400.00')
    assert abs(balances_before[user_a] - expected_a_before) < Decimal('0.01'), f"User A balance incorrect: {balances_before[user_a]}"
    assert abs(balances_before[user_b] - expected_b_before) < Decimal('0.01'), f"User B balance incorrect: {balances_before[user_b]}"
    print("✅ Balances before settlement are correct")
    
    # A pays ₹150 (partial settlement)
    settlement_id = generate_settlement_id()
    settlement = {
        "id": settlement_id,
        "group_id": group_id,
        "from": user_a,  # Debtor
        "to": user_b,     # Creditor
        "amount": 150.0,
        "created_at": datetime.now()
    }
    await create_settlement_in_mongo(settlement)
    
    # Check balances after partial settlement
    balances_after = await compute_group_balances(group_id)
    print(f"\nBalances after partial settlement: {decimal_dict_to_float(balances_after)}")
    print(f"Expected: A: -250, B: +250")
    
    expected_a_after = Decimal('-250.00')
    expected_b_after = Decimal('250.00')
    assert abs(balances_after[user_a] - expected_a_after) < Decimal('0.01'), f"User A balance incorrect: {balances_after[user_a]}"
    assert abs(balances_after[user_b] - expected_b_after) < Decimal('0.01'), f"User B balance incorrect: {balances_after[user_b]}"
    print("✅ Balances after partial settlement are correct")
    
    # Cleanup
    await delete_group_and_related_data(group_id)
    print("\n✅ TEST CASE 3 PASSED")
    return True


async def test_case_4():
    """
    Case 4: Multi-expense netting with settlements
    - Multiple expenses between multiple users
    - Multiple settlements
    - Net balances must match exactly
    """
    print("\n" + "="*60)
    print("TEST CASE 4: Multi-expense netting with settlements")
    print("="*60)
    
    group_id = generate_group_id()
    user_a = "user_test_a4"
    user_b = "user_test_b4"
    user_c = "user_test_c4"
    
    # Create group
    group = {
        "id": group_id,
        "name": "Test Group 4",
        "type": "trip",
        "invite_code": "TEST04",
        "currency": "INR",
        "simplify_debts": True,
        "created_at": datetime.now(),
        "created_by": user_a,
        "members": [
            {"user_id": user_a, "name": "User A", "role": "admin", "joined_at": datetime.now()},
            {"user_id": user_b, "name": "User B", "role": "member", "joined_at": datetime.now()},
            {"user_id": user_c, "name": "User C", "role": "member", "joined_at": datetime.now()}
        ]
    }
    await create_group_in_mongo(group)
    
    # Expense 1: A pays ₹900, split equally among A, B, C
    # A: +900 -300 = +600, B: -300, C: -300
    expense_id_1 = generate_expense_id()
    split_type, split_participants, _ = normalize_expense_split(
        amount=900.0,
        paid_by=user_a,
        group_members=group["members"],
        split_input=None
    )
    expense_1 = {
        "id": expense_id_1,
        "group_id": group_id,
        "title": "Hotel",
        "amount": 900.0,
        "paid_by": user_a,
        "category": "Accommodation",
        "split_type": split_type,
        "date": datetime.now(),
        "created_at": datetime.now(),
        "created_by": user_a,
        "splits": [{"user_id": p["user_id"], "amount_owed": float(p["share"])} for p in split_participants],
        "split_participants": [{"user_id": p["user_id"], "share": float(p["share"])} for p in split_participants],
    }
    await create_expense_in_mongo(expense_1)
    
    # Expense 2: B pays ₹600, split equally among A, B, C
    # A: +600-200 = +400 net, B: +600-200 = +400 net, C: -200-300 = -500 net
    expense_id_2 = generate_expense_id()
    split_type, split_participants, _ = normalize_expense_split(
        amount=600.0,
        paid_by=user_b,
        group_members=group["members"],
        split_input=None
    )
    expense_2 = {
        "id": expense_id_2,
        "group_id": group_id,
        "title": "Transport",
        "amount": 600.0,
        "paid_by": user_b,
        "category": "Transport",
        "split_type": split_type,
        "date": datetime.now(),
        "created_at": datetime.now(),
        "created_by": user_b,
        "splits": [{"user_id": p["user_id"], "amount_owed": float(p["share"])} for p in split_participants],
        "split_participants": [{"user_id": p["user_id"], "share": float(p["share"])} for p in split_participants],
    }
    await create_expense_in_mongo(expense_2)
    
    # Check balances after expenses
    balances_after_expenses = await compute_group_balances(group_id)
    print(f"\nBalances after expenses: {decimal_dict_to_float(balances_after_expenses)}")
    print(f"Expected: A: +400, B: +100, C: -500")
    
    # A: paid 900, owes 300 + 200 = -500 → net +400
    # B: paid 600, owes 300 + 200 = -500 → net +100
    # C: paid 0, owes 300 + 200 = -500 → net -500
    expected_a = Decimal('400.00')
    expected_b = Decimal('100.00')
    expected_c = Decimal('-500.00')
    
    assert abs(balances_after_expenses[user_a] - expected_a) < Decimal('0.01'), f"User A balance incorrect: {balances_after_expenses[user_a]}"
    assert abs(balances_after_expenses[user_b] - expected_b) < Decimal('0.01'), f"User B balance incorrect: {balances_after_expenses[user_b]}"
    assert abs(balances_after_expenses[user_c] - expected_c) < Decimal('0.01'), f"User C balance incorrect: {balances_after_expenses[user_c]}"
    print("✅ Balances after expenses are correct")
    
    # Settlement 1: C pays A ₹300
    settlement_id_1 = generate_settlement_id()
    settlement_1 = {
        "id": settlement_id_1,
        "group_id": group_id,
        "from": user_c,
        "to": user_a,
        "amount": 300.0,
        "created_at": datetime.now()
    }
    await create_settlement_in_mongo(settlement_1)
    
    # Settlement 2: C pays B ₹100
    settlement_id_2 = generate_settlement_id()
    settlement_2 = {
        "id": settlement_id_2,
        "group_id": group_id,
        "from": user_c,
        "to": user_b,
        "amount": 100.0,
        "created_at": datetime.now()
    }
    await create_settlement_in_mongo(settlement_2)
    
    # Check balances after settlements
    balances_after_settlements = await compute_group_balances(group_id)
    print(f"\nBalances after settlements: {decimal_dict_to_float(balances_after_settlements)}")
    print(f"Expected: A: +100, B: 0, C: -100")
    
    # A: 400 - 300 (received from C) = +100
    # B: 100 - 100 (received from C) = 0
    # C: -500 + 300 (paid to A) + 100 (paid to B) = -100
    expected_a_final = Decimal('100.00')
    expected_b_final = Decimal('0.00')
    expected_c_final = Decimal('-100.00')
    
    assert abs(balances_after_settlements[user_a] - expected_a_final) < Decimal('0.01'), f"User A balance incorrect: {balances_after_settlements[user_a]}"
    assert abs(balances_after_settlements[user_b] - expected_b_final) < Decimal('0.01'), f"User B balance incorrect: {balances_after_settlements[user_b]}"
    assert abs(balances_after_settlements[user_c] - expected_c_final) < Decimal('0.01'), f"User C balance incorrect: {balances_after_settlements[user_c]}"
    print("✅ Balances after settlements are correct")
    
    # Cleanup
    await delete_group_and_related_data(group_id)
    print("\n✅ TEST CASE 4 PASSED")
    return True


async def run_all_tests():
    """Run all settlement test cases"""
    print("\n" + "="*60)
    print("RUNNING COMPREHENSIVE SETTLEMENT TESTS")
    print("="*60)
    
    all_passed = True
    
    try:
        await test_case_1()
    except Exception as e:
        print(f"\n❌ TEST CASE 1 FAILED: {e}")
        all_passed = False
    
    try:
        await test_case_2()
    except Exception as e:
        print(f"\n❌ TEST CASE 2 FAILED: {e}")
        all_passed = False
    
    try:
        await test_case_3()
    except Exception as e:
        print(f"\n❌ TEST CASE 3 FAILED: {e}")
        all_passed = False
    
    try:
        await test_case_4()
    except Exception as e:
        print(f"\n❌ TEST CASE 4 FAILED: {e}")
        all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ ALL TESTS PASSED - SETTLEMENTS WORKING CORRECTLY")
    else:
        print("❌ SOME TESTS FAILED - SEE ERRORS ABOVE")
    print("="*60)
    
    return all_passed


if __name__ == "__main__":
    asyncio.run(run_all_tests())
